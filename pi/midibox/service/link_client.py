"""PatchSYS Link client for the MidiBox Pi.

Speaks the protocol of ``patchsys/remote_link.py`` (protocol version 1), the same one the
iPad remote uses, so PatchSYS needs no change to be driven by the box:

- newline-delimited JSON over TCP, ``register`` → ``session``;
- ``claim_writer`` → ``writer_granted`` (a lease bound to this connection; the device that
  armed last holds it, and a ``writer_released`` push says someone else took it);
- ``set_parameter`` with a monotonic ``sequence`` under the lease, latest value wins per
  parameter, so a knob burst never queues up stale values;
- ``action`` messages for the buttons (tempo, set_depth, variation, generate, undo …);
- pushes: ``session`` (target changed), ``parameter_confirmed`` (the app's confirmed value,
  which the screen must follow, never the knob), ``state`` (tempo, labels, status).

One thread owns the socket: it reads with a short timeout, then flushes what the router
queued. Nothing here touches hardware; the router passes values in and takes callbacks out.
"""

from __future__ import annotations

import json
import logging
import socket
import threading
import time

LOGGER = logging.getLogger("midibox.link")

PROTOCOL_VERSION = 1
# The eight semantic controls of patchsys/hardware_bridge.py, in the app's order.
PARAMETER_IDS = (
    "oscillator_mix", "brightness", "bite", "env_amount",
    "filter_attack", "filter_release", "movement", "movement_speed",
)
PARAMETER_NAMES = {
    "oscillator_mix": "Balance", "brightness": "Cutoff", "bite": "Resonance",
    "env_amount": "Env Amount", "filter_attack": "Filter Attack",
    "filter_release": "Filter Release", "movement": "Movement", "movement_speed": "Movement Speed",
}
MAX_FRAME_BYTES = 1 << 20
HEARTBEAT_S = 5.0
CLAIM_RETRY_S = 0.5


class PatchSysLink:
    """Owns one TCP connection to a PatchSYS Link server and keeps it alive."""

    def __init__(self, host, port=39276, *, instance_id="midibox-pi", reconnect_s=3.0,
                 send_hz=50, on_session=None, on_value=None, on_state=None):
        self.host = str(host)
        self.port = int(port)
        self.instance_id = str(instance_id)
        self.reconnect_s = float(reconnect_s)
        self.send_period = 1.0 / float(send_hz)
        self.on_session = on_session
        self.on_value = on_value
        self.on_state = on_state

        self._lock = threading.Lock()
        self._pending: dict[str, float] = {}
        self._actions: list[tuple[str, dict]] = []
        self._thread = None
        self._stop = threading.Event()

        # context, as the last session frame said
        self.connected = False
        self.online = False
        self.session_id = ""
        self.generation = 0
        self.synth_name = ""
        self.status = "DISCONNECTED"
        self.values: dict[str, float] = {}
        self.state: dict = {}
        # writer lease
        self._writer = "none"       # none | claiming | granted
        self._lease_id = ""
        self._claim_sent_at = 0.0
        self._arm_epoch = 0
        self._sequence = 0
        self._requests: dict[str, tuple] = {}
        self._counter = 0
        self.sent_parameters = 0
        self.sent_actions = 0
        self.errors: dict[str, int] = {}

    # -- public ---------------------------------------------------------------------------

    def start(self):
        if self._thread is not None:
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="midibox-link", daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        thread, self._thread = self._thread, None
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=2.0)

    def set_macro(self, parameter_id, value):
        """Latest wins: the router may call this at any rate."""
        if parameter_id not in PARAMETER_IDS:
            return
        value = max(0.0, min(1.0, float(value)))
        with self._lock:
            self._pending[parameter_id] = value

    def action(self, name, **payload):
        with self._lock:
            # one tempo / one depth in flight: a later value replaces an unsent one
            if name in ("tempo", "set_depth"):
                self._actions = [item for item in self._actions if item[0] != name]
            self._actions.append((name, dict(payload)))

    @property
    def summary(self):
        writer = self._writer
        return (f"link {'up' if self.connected else 'down'} {self.host}:{self.port} "
                f"{self.status} {self.synth_name or ''} writer={writer} "
                f"sent={self.sent_parameters}/{self.sent_actions} errors={self.errors or '-'}")

    # -- the socket thread -------------------------------------------------------------------

    def _run(self):
        while not self._stop.is_set():
            sock = None
            try:
                sock = socket.create_connection((self.host, self.port), timeout=4.0)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                sock.settimeout(0.02)
                self.connected = True
                self.status = "CONNECTED"
                LOGGER.info("connected to %s:%d", self.host, self.port)
                self._session(sock)
            except (OSError, ConnectionError) as error:
                LOGGER.warning("link: %s", error)
            finally:
                if sock is not None:
                    try:
                        sock.close()
                    except OSError:
                        pass
                self._reset_connection_state()
            if not self._stop.is_set():
                self._stop.wait(self.reconnect_s)

    def _reset_connection_state(self):
        self.connected = False
        self.online = False
        self.status = "DISCONNECTED"
        self._writer = "none"
        self._lease_id = ""
        self._requests.clear()
        with self._lock:
            self._pending.clear()
        if self.on_session is not None:
            try:
                self.on_session(self)
            except Exception:
                LOGGER.exception("on_session failed")

    def _session(self, sock):
        buffer = b""
        self._send(sock, "register")
        last_rx = time.monotonic()
        last_flush = 0.0
        while not self._stop.is_set():
            try:
                data = sock.recv(65536)
                if not data:
                    raise ConnectionError("server closed the link")
                buffer += data
                last_rx = time.monotonic()
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if len(line) > MAX_FRAME_BYTES:
                        continue
                    try:
                        self._handle(json.loads(line))
                    except (ValueError, TypeError):
                        continue
            except socket.timeout:
                pass
            now = time.monotonic()
            if now - last_flush >= self.send_period:
                last_flush = now
                self._flush(sock)
            if now - last_rx > HEARTBEAT_S:
                last_rx = now
                self._send(sock, "heartbeat")
            if now - last_rx > HEARTBEAT_S * 4:
                raise ConnectionError("no answer from PatchSYS")

    def _send(self, sock, message_type, **fields):
        self._counter += 1
        request_id = f"{self.instance_id}-{self._counter}"
        message = {
            "type": message_type,
            "protocol_version": PROTOCOL_VERSION,
            "request_id": request_id,
            "instance_id": self.instance_id,
            **fields,
        }
        kind = fields.get("parameter_id") or fields.get("action") or message_type
        self._requests[request_id] = (message_type, kind)
        if len(self._requests) > 512:
            for key in list(self._requests)[:256]:
                self._requests.pop(key, None)
        payload = json.dumps(message, separators=(",", ":")).encode("utf-8") + b"\n"
        sock.sendall(payload)
        return request_id

    def _flush(self, sock):
        with self._lock:
            pending = dict(self._pending)
            actions = list(self._actions)
            self._actions.clear()
        if not self.online:
            # the target is away: keep the newest knob value for when it returns, drop buttons
            return
        for name, payload in actions:
            self._send(sock, "action", action=name, session_id=self.session_id,
                       generation=self.generation, **payload)
            self.sent_actions += 1
        if not pending:
            return
        if self._writer == "granted":
            with self._lock:
                self._pending.clear()
            for parameter_id, value in pending.items():
                self._sequence += 1
                self._send(sock, "set_parameter", session_id=self.session_id,
                           generation=self.generation, lease_id=self._lease_id,
                           parameter_id=parameter_id, normalized_value=value,
                           sequence=self._sequence)
                self.sent_parameters += 1
        elif self._writer == "none" or time.monotonic() - self._claim_sent_at > CLAIM_RETRY_S:
            self._writer = "claiming"
            self._claim_sent_at = time.monotonic()
            self._arm_epoch += 1
            self._send(sock, "claim_writer", session_id=self.session_id,
                       generation=self.generation, arm_epoch=self._arm_epoch)

    def _handle(self, message):
        if not isinstance(message, dict):
            return
        kind = message.get("type")
        request = self._requests.pop(message.get("request_id") or "", None)
        if kind == "session":
            self._apply_session(message)
        elif kind == "writer_granted":
            self._writer = "granted"
            self._lease_id = str(message.get("lease_id", ""))
            self._sequence = 0
        elif kind == "writer_released":
            self._writer = "none"
            self._lease_id = ""
        elif kind == "parameter_confirmed":
            parameter_id = message.get("parameter_id")
            value = message.get("normalized_value")
            if parameter_id in PARAMETER_IDS and isinstance(value, (int, float)):
                self.values[parameter_id] = float(value)
                if self.on_value is not None:
                    self.on_value(parameter_id, float(value))
        elif kind == "state":
            state = message.get("state")
            if isinstance(state, dict):
                self.state.update(state)
                if self.on_state is not None:
                    self.on_state(state)
        elif kind == "error":
            error = str(message.get("error", "?"))
            self.errors[error] = self.errors.get(error, 0) + 1
            if error in ("writer_required", "invalid_lease", "stale_sequence"):
                self._writer = "none"
            elif error in ("stale_session", "stale_generation", "target_offline"):
                self._writer = "none"
                # the next session push carries the new ids; the newest knob values are resent then
            elif error == "parameter_unavailable":
                with self._lock:
                    self._pending.clear()
            elif error == "target_not_ready":
                self._writer = "none"
            if request is not None and request[0] == "claim_writer":
                self._writer = "none"
            LOGGER.debug("link error %s for %s", error, request)
        # parameter_queued, action_queued, pong: nothing to do

    def _apply_session(self, message):
        was_online = self.online
        self.online = bool(message.get("online"))
        new_session = str(message.get("session_id", ""))
        new_generation = int(message.get("generation", 0) or 0)
        target_changed = (new_session != self.session_id) or (new_generation != self.generation)
        self.session_id = new_session
        self.generation = new_generation
        self.synth_name = str(message.get("synth_name", "") or "")
        self.status = str(message.get("status", "") or ("ONLINE" if self.online else "OFFLINE"))
        if message.get("writer") is False and self._writer == "granted":
            self._writer = "none"
        if target_changed:
            self._writer = "none"
            self._lease_id = ""
            self.values = {}
        for item in message.get("parameters") or ():
            if not isinstance(item, dict):
                continue
            parameter_id = item.get("id")
            value = item.get("value")
            if parameter_id in PARAMETER_IDS and isinstance(value, (int, float)):
                self.values[parameter_id] = float(value)
        if isinstance(message.get("state"), dict):
            self.state.update(message["state"])
        if not self.online:
            with self._lock:
                self._pending.clear()
        if self.on_session is not None:
            try:
                self.on_session(self)
            except Exception:
                LOGGER.exception("on_session failed")
        if self.online and not was_online:
            LOGGER.info("PatchSYS online: %s (%s)", self.synth_name, self.status)
