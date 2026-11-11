#!/usr/bin/env python3
"""MidiBox service: every device on the box in one process, controlling PatchSYS.

Run from ~/midibox on the Pi:

    sudo python3 -m service.midibox_service            # all devices, talk to PatchSYS
    sudo python3 -m service.midibox_service --no-link  # devices only, print what would be sent
    python3 -m service.midibox_service --no-hw --selftest   # no hardware: synthetic events

What it does
- Encoders 1-4 drive four of PatchSYS's eight semantic controls (bank A), the Arc1 press
  swaps to the other four (bank B). PatchSYS's confirmed values come back and move the
  screen's arcs, so the arcs follow the app, never the knob.
- The SuperCore (the tempo encoder with the ring and haptics) has modes: TEMPO turns
  PatchSYS's tempo, DEPTH turns its variation depth; a long press makes a VARIATION.
  The ring shows the value and the mode's colour; every detent ticks, the ends bump.
- Touching an arc on the screen writes the same control as turning its encoder.
- Wheels go out as MIDI pitch bend and CC1, to the screen bars and to the two wheel pixels.
- Faders go out as MIDI CC (7 and 74 by default), or to a PatchSYS control if configured.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import queue
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from service.link_client import PARAMETER_IDS, PARAMETER_NAMES, PatchSysLink  # noqa: E402

LOGGER = logging.getLogger("midibox")


class Service:
    def __init__(self, config, *, use_hw=True, use_link=True):
        self.cfg = config
        self.use_hw = use_hw
        self.events: "queue.Queue[tuple]" = queue.Queue()
        self.stop = threading.Event()
        self.threads = []

        self.banks = {name: list(ids) for name, ids in config.get("banks", {}).items()}
        self.bank_names = list(self.banks) or ["A"]
        self.bank = self.bank_names[0]
        self.arc_names = list(config["encoders"].get("arc_names", []))
        self.tempo_arc = config["encoders"].get("tempo_arc_name", "uic_t1Arc5Tempo")
        self.step = float(config["encoders"].get("step_per_edge", 1)) / 127.0
        self.press_roles = config["encoders"].get("press_roles", {})
        self.long_press_s = float(config["encoders"].get("long_press_s", 0.7))

        sc = config.get("supercore", {})
        self.sc_index = int(sc.get("index", 4))
        self.sc_modes = list(sc.get("modes", ["tempo", "depth"]))
        self.sc_mode = 0
        self.sc_cfg = sc
        self.tempo = float(sc.get("tempo", {}).get("start", 120))
        self.depth = float(sc.get("depth", {}).get("start", 33))
        self.sc_send_period = 1.0 / float(sc.get("send_hz", 20))
        self.sc_last_send = {"tempo": 0.0, "depth": 0.0}
        self.sc_dirty = {"tempo": False, "depth": False}

        # the value we asked for per control, and when we last touched it: confirmed values
        # from the app only replace ours once the knob has been still for a moment
        self.requested: dict[str, float] = {}
        self.touched_at: dict[str, float] = {}
        self.press_down_at = None
        self.bank_flash_color = None
        self.shown_patchsys_page = False
        self.counts = {"turn": 0, "press": 0, "esp_get": 0, "wheel": 0, "fader": 0}

        self.encoders = self.wheels = self.faders = self.leds = self.haptics = self.esp = self.midi = None
        self.link = None
        if use_link and config.get("link", {}).get("enabled", True):
            link = config["link"]
            self.link = PatchSysLink(
                link.get("host", "127.0.0.1"), link.get("port", 39276),
                instance_id=link.get("instance_id", "midibox-pi"),
                reconnect_s=link.get("reconnect_s", 3.0), send_hz=link.get("send_hz", 50),
                on_session=self._on_session, on_value=self._on_value, on_state=self._on_state,
            )
        if use_hw:
            self._open_hardware()

    # -- hardware ------------------------------------------------------------------------------

    def _open_hardware(self):
        from service import hardware
        cfg = self.cfg

        def open_device(name, factory):
            if not cfg.get(name, {}).get("enabled", True):
                LOGGER.info("%s disabled in config", name)
                return None
            try:
                device = factory()
                LOGGER.info("%s ready", name)
                return device
            except Exception as error:
                LOGGER.warning("%s unavailable: %s", name, error)
                return None

        self.encoders = open_device("encoders", lambda: hardware.Encoders(cfg["encoders"]))
        self.wheels = open_device("wheels", lambda: hardware.Wheels(cfg["wheels"], ROOT))
        self.faders = open_device("faders", lambda: hardware.Faders(cfg["faders"], ROOT))
        self.leds = open_device("leds", lambda: hardware.Leds(cfg["leds"]))
        self.haptics = open_device("haptics", lambda: hardware.Haptics(cfg["haptics"]))
        self.esp = open_device("esp", lambda: hardware.Esp(cfg["esp"]))
        self.midi = open_device("midi", lambda: hardware.MidiOut(cfg["midi"]))

    def _spawn(self, name, target, period):
        def loop():
            while not self.stop.is_set():
                started = time.monotonic()
                try:
                    target()
                except Exception as error:
                    LOGGER.warning("%s loop: %s", name, error)
                    time.sleep(0.2)
                elapsed = time.monotonic() - started
                if period > elapsed:
                    time.sleep(period - elapsed)
        thread = threading.Thread(target=loop, name=f"midibox-{name}", daemon=True)
        self.threads.append(thread)
        thread.start()

    def _read_encoders(self):
        for event in self.encoders.read():
            self.events.put(event)

    def _read_wheels(self):
        for name, value01, value7 in self.wheels.read():
            self.events.put(("wheel", name, value01, value7))

    def _read_faders(self):
        for index, value01, value7 in self.faders.read():
            self.events.put(("fader", index, value01, value7))

    def _read_esp(self):
        for message in self.esp.poll():
            if "get" in message:
                self.events.put(("esp_get", str(message.get("get")), message.get("val")))

    # -- routing -------------------------------------------------------------------------------

    def start(self):
        if self.link is not None:
            self.link.start()
        if self.encoders is not None:
            self._spawn("encoders", self._read_encoders, 0.001)
        if self.wheels is not None:
            self._spawn("wheels", self._read_wheels, 1.0 / float(self.cfg["wheels"].get("rate_hz", 60)))
        if self.faders is not None:
            self._spawn("faders", self._read_faders, 1.0 / float(self.cfg["faders"].get("rate_hz", 250)))
        if self.esp is not None:
            self._spawn("esp", self._read_esp, 0.005)
        self._show_supercore(force=True)
        self._push_bank_to_screen()

    def shutdown(self):
        self.stop.set()
        if self.link is not None:
            self.link.stop()
        if self.leds is not None:
            try:
                self.leds.clear()
            except Exception:
                pass

    def run(self, seconds=None, status_every=2.0):
        deadline = None if seconds is None else time.monotonic() + float(seconds)
        last_status = 0.0
        try:
            while not self.stop.is_set():
                try:
                    event = self.events.get(timeout=0.005)
                except queue.Empty:
                    event = None
                if event is not None:
                    self.handle(event)
                self._tick()
                now = time.monotonic()
                if now - last_status >= status_every:
                    last_status = now
                    LOGGER.info(self.summary())
                if deadline is not None and now >= deadline:
                    break
        finally:
            self.shutdown()

    def summary(self):
        link = self.link.summary if self.link is not None else "link off"
        return (f"bank {self.bank} | supercore {self.sc_modes[self.sc_mode]} tempo {int(self.tempo)} "
                f"depth {int(self.depth)} | events {self.counts} | {link}")

    def current_ids(self):
        return self.banks.get(self.bank, [])

    def handle(self, event):
        kind = event[0]
        if kind == "turn":
            _, index, delta = event
            self.counts["turn"] += 1
            if index == self.sc_index:
                self._supercore_turn(delta)
            else:
                self._encoder_turn(index, delta)
        elif kind == "press":
            _, button, pressed = event
            self._press(button, pressed)
        elif kind == "esp_get":
            _, name, value = event
            self.counts["esp_get"] += 1
            self._screen_touch(name, value)
        elif kind == "wheel":
            _, name, value01, value7 = event
            self.counts["wheel"] += 1
            self._wheel(name, value01, value7)
        elif kind == "fader":
            _, index, value01, value7 = event
            self.counts["fader"] += 1
            self._fader(index, value01, value7)

    def _encoder_turn(self, index, delta):
        ids = self.current_ids()
        if index >= len(ids):
            return
        parameter_id = ids[index]
        base = self.requested.get(parameter_id)
        if base is None:
            base = self.link.values.get(parameter_id, 0.5) if self.link is not None else 0.5
        value = max(0.0, min(1.0, base + delta * self.step))
        self._write_control(parameter_id, value, index)

    def _screen_touch(self, name, value):
        # the PatchSYS page's buttons
        if name in ("ps_gen", "ps_vary", "ps_undo"):
            action = {"ps_gen": "generate", "ps_vary": "variation", "ps_undo": "undo"}[name]
            if self.link is not None:
                self.link.action(action)
            else:
                LOGGER.info("would send action %s", action)
            if self.haptics is not None:
                self.haptics.confirm()
            return
        if name == "ps_bank":
            self._switch_bank()
            return
        if name == "ps_mode":
            self._cycle_supercore_mode()
            return
        if name == "ps_back":
            return
        if not isinstance(value, (int, float)):
            return
        arc_index = None
        if name in self.arc_names:
            arc_index = self.arc_names.index(name)
        elif name.startswith("ps_arc") and name[6:].isdigit():
            arc_index = int(name[6:]) - 1
        if arc_index is not None:
            ids = self.current_ids()
            if 0 <= arc_index < len(ids):
                self._write_control(ids[arc_index], max(0.0, min(1.0, float(value) / 127.0)), arc_index, from_screen=True)
        # the tempo arc has no screen event and the bars belong to the wheels

    def _write_control(self, parameter_id, value, index, *, from_screen=False):
        self.requested[parameter_id] = value
        self.touched_at[parameter_id] = time.monotonic()
        if self.link is not None:
            self.link.set_macro(parameter_id, value)
        else:
            LOGGER.info("would set %s (%s) = %.3f", parameter_id, PARAMETER_NAMES[parameter_id], value)
        if not from_screen and self.esp is not None and index < len(self.arc_names):
            self.esp.send(self.arc_names[index], round(value * 127))
            self.esp.send(f"ps_arc{index + 1}", round(value * 127))

    def _press(self, button, pressed):
        self.counts["press"] += 1
        roles = self.press_roles.get(button, {})
        if pressed:
            self.press_down_at = time.monotonic()
            return
        held = (time.monotonic() - self.press_down_at) if self.press_down_at is not None else 0.0
        self.press_down_at = None
        role = roles.get("long" if held >= self.long_press_s else "short")
        if role == "bank":
            self._switch_bank()
        elif role == "supercore_mode":
            self._cycle_supercore_mode()
        elif role == "variation":
            if self.link is not None:
                self.link.action("variation")
            if self.haptics is not None:
                self.haptics.confirm()
            LOGGER.info("variation requested")

    def _cycle_supercore_mode(self):
        self.sc_mode = (self.sc_mode + 1) % len(self.sc_modes)
        if self.haptics is not None:
            self.haptics.confirm()
        self._show_supercore(force=True)
        LOGGER.info("SuperCore mode: %s", self.sc_modes[self.sc_mode])

    def _switch_bank(self):
        position = self.bank_names.index(self.bank)
        self.bank = self.bank_names[(position + 1) % len(self.bank_names)]
        if self.haptics is not None:
            self.haptics.confirm()
        if self.leds is not None:
            self.leds.flash()
        self._push_bank_to_screen()
        LOGGER.info("bank %s: %s", self.bank, ", ".join(PARAMETER_NAMES[i] for i in self.current_ids()))

    def _push_bank_to_screen(self):
        if self.esp is None:
            return
        self.esp.send("ps_bank", self.bank_names.index(self.bank))
        for index, parameter_id in enumerate(self.current_ids()):
            if index >= len(self.arc_names):
                break
            self.esp.send_text(f"ps_lbl{index + 1}", PARAMETER_NAMES[parameter_id].upper())
            value = self.requested.get(parameter_id)
            if value is None and self.link is not None:
                value = self.link.values.get(parameter_id)
            if value is not None:
                self.esp.send(self.arc_names[index], round(value * 127))
                self.esp.send(f"ps_arc{index + 1}", round(value * 127))

    def _push_link_to_screen(self):
        """Status, target and sound on the PatchSYS page."""
        if self.esp is None:
            return
        link = self.link
        if link is None:
            self.esp.send("ps_status", 0)
            return
        status = str(link.status or "")
        code = 1 if link.online else (2 if "BUSY" in status.upper() else 0)
        self.esp.send("ps_status", code)
        if code == 0 and status and status not in ("OFFLINE", "DISCONNECTED"):
            self.esp.send_text("ps_status_t", status[:12].upper())
        self.esp.send_text("ps_synth", (link.synth_name or "").upper())
        sound = link.state.get("sound") if isinstance(link.state, dict) else ""
        self.esp.send_text("ps_sound", str(sound or ""))

    def _supercore_turn(self, delta):
        mode = self.sc_modes[self.sc_mode]
        spec = self.sc_cfg.get(mode, {})
        lo, hi = float(spec.get("min", 0)), float(spec.get("max", 100))
        per_edge = float(spec.get("bpm_per_edge", spec.get("per_edge", 1)))
        current = self.tempo if mode == "tempo" else self.depth
        value = max(lo, min(hi, current + delta * per_edge))
        at_end = value in (lo, hi) and value != current
        if mode == "tempo":
            self.tempo = value
        else:
            self.depth = value
        self.sc_dirty[mode] = True
        if self.haptics is not None:
            (self.haptics.endstop if at_end else self.haptics.tick)()
        self._show_supercore()

    def _show_supercore(self, force=False):
        mode = self.sc_modes[self.sc_mode]
        spec = self.sc_cfg.get(mode, {})
        lo, hi = float(spec.get("min", 0)), float(spec.get("max", 100))
        value = self.tempo if mode == "tempo" else self.depth
        fraction = (value - lo) / (hi - lo) if hi > lo else 0.0
        if self.leds is not None:
            color = self.leds.mode_colors.get(mode, (0, 255, 255, 0))
            if force:
                self.leds.ring_lit = -1
            self.leds.ring(fraction, color)
        if self.esp is not None:
            if mode == "tempo":
                self.esp.send(self.tempo_arc, int(value))
            self.esp.send("ps_sc", int(round(fraction * 100)))
            self.esp.send_text("ps_scval", str(int(value)))
            if force:
                self.esp.send_text("ps_mode", mode.upper())
                self.esp.send_text("ps_unit", "BPM" if mode == "tempo" else "%")
                self.esp.send("ps_mode_color", 0 if mode == "tempo" else 1)

    def _tick(self):
        """Rate-limited sends of the SuperCore's value to PatchSYS."""
        now = time.monotonic()
        for mode in ("tempo", "depth"):
            if self.sc_dirty[mode] and now - self.sc_last_send[mode] >= self.sc_send_period:
                self.sc_dirty[mode] = False
                self.sc_last_send[mode] = now
                if self.link is not None:
                    if mode == "tempo":
                        self.link.action("tempo", bpm=int(self.tempo))
                    else:
                        self.link.action("set_depth", depth=int(self.depth))
                else:
                    LOGGER.info("would send %s %d", mode, int(self.tempo if mode == "tempo" else self.depth))

    def _wheel(self, name, value01, value7):
        if self.midi is not None:
            if name == "pitch":
                self.midi.pitch(value01)
            else:
                self.midi.cc(1, value7)
        if self.esp is not None:
            self.esp.send(self.cfg["wheels"].get("pitch_bar" if name == "pitch" else "mod_bar"), value7)
        if self.leds is not None and self.wheels is not None:
            try:
                self.leds.wheels(self.wheels.last7[0] or 64, self.wheels.last01[1])
            except Exception as error:
                LOGGER.debug("wheel leds: %s", error)

    def _fader(self, index, value01, value7):
        targets = self.cfg["faders"].get("targets", [])
        target = targets[index] if index < len(targets) else {}
        if "macro" in target and target["macro"] in PARAMETER_IDS:
            self._write_control(target["macro"], value01, len(self.arc_names))  # no arc to mirror
        elif self.midi is not None:
            self.midi.cc(int(target.get("cc", 7 if index == 0 else 74)), value7)

    # -- from PatchSYS --------------------------------------------------------------------------

    def _on_session(self, link):
        LOGGER.info("PatchSYS: %s %s online=%s", link.status, link.synth_name, link.online)
        self._push_link_to_screen()
        if link.online:
            self.requested = {}
            self._push_bank_to_screen()
            if self.esp is not None and not self.shown_patchsys_page:
                self.shown_patchsys_page = True
                self.esp.send("ps_show", 1)

    def _on_value(self, parameter_id, value):
        """The app's confirmed value replaces ours once the knob has been still for 300 ms."""
        if time.monotonic() - self.touched_at.get(parameter_id, 0.0) < 0.3:
            return
        self.requested[parameter_id] = value
        ids = self.current_ids()
        if parameter_id in ids and self.esp is not None:
            index = ids.index(parameter_id)
            if index < len(self.arc_names):
                self.esp.send(self.arc_names[index], round(value * 127))
                self.esp.send(f"ps_arc{index + 1}", round(value * 127))

    def _on_state(self, state):
        if self.esp is not None and ("sound" in state or "status" in state):
            self._push_link_to_screen()
        tempo = state.get("tempo")
        if isinstance(tempo, (int, float)) and not self.sc_dirty["tempo"] and abs(tempo - self.tempo) >= 1:
            self.tempo = float(tempo)
            if self.sc_modes[self.sc_mode] == "tempo":
                self._show_supercore()
        depth = state.get("depth")
        if isinstance(depth, (int, float)) and not self.sc_dirty["depth"]:
            self.depth = float(depth)
            if self.sc_modes[self.sc_mode] == "depth":
                self._show_supercore()


def selftest(service):
    """Synthetic events through the router, in the order a hand would make them."""
    script = [
        ("turn", 0, +4), ("turn", 1, -2), ("turn", 2, +10), ("turn", 3, +1),
        ("esp_get", "uic_t1Arc3", 100),
        ("press", "arc1", True), ("press", "arc1", False),      # short: bank B
        ("turn", 0, +3), ("turn", 3, -5),
        ("turn", 4, +6), ("turn", 4, -2),                        # SuperCore tempo
        ("press", "arc1", True), ("sleep", 0.9), ("press", "arc1", False),  # long: depth mode
        ("turn", 4, +5),
        ("wheel", "pitch", 0.75, 95), ("wheel", "mod", 0.2, 25),
        ("fader", 0, 0.5, 64), ("fader", 1, 1.0, 127),
    ]
    for event in script:
        if event[0] == "sleep":
            time.sleep(event[1])
            continue
        service.events.put(event)
        time.sleep(0.03)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json"))
    parser.add_argument("--no-hw", action="store_true", help="open no devices")
    parser.add_argument("--no-link", action="store_true", help="do not talk to PatchSYS; print what would be sent")
    parser.add_argument("--host", help="PatchSYS host (overrides the config)")
    parser.add_argument("--selftest", action="store_true", help="feed synthetic events, then run for --seconds")
    parser.add_argument("--seconds", type=float, default=None, help="run this long, then exit")
    parser.add_argument("--only", help="comma list of devices to open: encoders,wheels,faders,leds,haptics,esp,midi")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(name)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
    with open(args.config, "r", encoding="utf-8") as handle:
        config = json.load(handle)
    if args.host:
        config.setdefault("link", {})["host"] = args.host
    if args.only:
        wanted = {name.strip() for name in args.only.split(",")}
        for name in ("encoders", "wheels", "faders", "leds", "haptics", "esp", "midi"):
            config.setdefault(name, {})["enabled"] = name in wanted
    service = Service(config, use_hw=not args.no_hw, use_link=not args.no_link)
    service.start()
    if args.selftest:
        threading.Thread(target=selftest, args=(service,), daemon=True).start()
    service.run(seconds=args.seconds)
    LOGGER.info("final: %s", service.summary())


if __name__ == "__main__":
    main()
