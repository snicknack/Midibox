# drivers/faders/infinium_x1_serial.py
# Behringer Infinium X1 (3.3V UART @ 31250) expressive fader driver.
# Parses a MIDI-like byte stream from a UART (e.g., /dev/ttyS0) and produces a
# normalized position plus mapping modes (single/dual/zones), curves, smoothing,
# pickup (soft-takeover), gesture metrics, and optional throw trigger.

from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque
from typing import Optional, Dict, List, Tuple
import time
import math
import serial  # pip install pyserial

# -------------------- Config dataclasses --------------------

@dataclass
class SerialConfig:
    port: str = "/dev/serial0"
    baud: int = 31250
    timeout: float = 0.001  # seconds

@dataclass
class FilterConfig:
    smoothing_ms: int = 6   # EMA time constant (lower = snappier)
    rate_hz: int = 500      # process() cadence

@dataclass
class CurveConfig:
    kind: str = "linear"    # "linear" | "log" | "exp" | "s"
    s_strength: float = 0.6 # used when kind == "s"

@dataclass
class PickupConfig:
    enabled: bool = True
    deadband_cc: int = 3    # 7-bit units

@dataclass
class GestureConfig:
    velocity_scale: float = 0.0   # disabled by default (quiet)
    accel_scale: float = 0.0
    throw_threshold: float = 0.90
    throw_window_s: float = 0.25
    throw_note: Optional[int] = None

@dataclass
class Zone:
    lo: float
    hi: float
    cc: int
    alt_cc: Optional[int] = None
    scale: float = 1.0
    offset: float = 0.0

@dataclass
class DualMapping:
    bottom_cc: int
    top_cc: int
    split: float = 0.5

@dataclass
class MappingLayers:
    # Example:
    # pages = {
    #   "A": {"cc": 74, "side_cc": 71, "presets": {"Pad01": 91}},
    #   "B": {"cc": 91}
    # }
    pages: Dict[str, Dict] = field(default_factory=dict)
    default_page: str = "A"

@dataclass
class InfiniumSerialConfig:
    serial: SerialConfig = field(default_factory=SerialConfig)
    filters: FilterConfig = field(default_factory=FilterConfig)
    curve: CurveConfig = field(default_factory=CurveConfig)
    pickup: PickupConfig = field(default_factory=PickupConfig)
    gesture: GestureConfig = field(default_factory=GestureConfig)
    zones: List[Zone] = field(default_factory=list)
    dual: Optional[DualMapping] = None
    fourteen_bit: bool = False     # irrelevant in paircc mode; keep for API symmetry
    midi_channel: int = 1
    layers: Optional[MappingLayers] = None
    prefer_pitchbend: bool = False # ignored in paircc mode
    learn_cc: Optional[int] = None # ignored in paircc mode

# -------------------- MIDI stream parser --------------------

class MidiStream:
    """
    Parser tolerant of running-status streams.
    If no status byte is seen, treat incoming bytes as PAIRS and automatically
    choose which byte (index 0 or 1) carries the useful signal by comparing variance.
    Emits: ("paircc", value_0_127) once a pair is complete.
    Also handles real PB (0xE0) and CC (0xB0) if status bytes appear.
    """
    def __init__(self):
        self.status = None
        self._pair: List[int] = []
        # Auto-select state
        self._decided = False
        self._use_idx = 1           # default to second byte until decided
        self._buf0: List[int] = []
        self._buf1: List[int] = []

    def _variance(self, xs: List[int]) -> float:
        if len(xs) < 2:
            return 0.0
        m = sum(xs) / len(xs)
        return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)

    def _maybe_decide(self):
        if self._decided:
            return
        # Decide after ~8 pairs
        if min(len(self._buf0), len(self._buf1)) >= 8:
            v0 = self._variance(self._buf0)
            v1 = self._variance(self._buf1)
            self._use_idx = 0 if v0 > v1 else 1
            self._decided = True

    def feed(self, data: bytes):
        events = []
        i = 0
        while i < len(data):
            b = data[i]

            if b & 0x80:
                # Status byte (PB/CC/ActiveSensing/etc.)
                self.status = b
                self._pair.clear()
                i += 1
                continue

            # Data byte
            if self.status is None:
                # Running-status-only: accumulate pairs, auto-pick the signal byte
                self._pair.append(b)
                if len(self._pair) == 2:
                    d0, d1 = self._pair
                    self._buf0.append(d0)
                    self._buf1.append(d1)
                    self._maybe_decide()
                    value = d0 if self._use_idx == 0 else d1
                    events.append(("paircc", value))
                    self._pair.clear()
                i += 1
                continue

            # If we *do* see status bytes, handle PB/CC normally
            st = self.status & 0xF0
            ch = (self.status & 0x0F) + 1

            if st == 0xE0:  # Pitch Bend: LSB, MSB
                if i + 1 < len(data):
                    lsb = data[i]
                    msb = data[i + 1]
                    events.append(("pb", ch, (msb << 7) | lsb))
                    i += 2
                else:
                    break
            elif st == 0xB0:  # Control Change: cc#, value
                if i + 1 < len(data):
                    cc = data[i]
                    val = data[i + 1]
                    events.append(("cc", ch, cc, val))
                    i += 2
                else:
                    break
            elif self.status == 0xFE:  # Active Sensing (single byte)
                i += 1
            else:
                # Unhandled status type; advance conservatively
                i += 1

        return events

# -------------------- Driver --------------------

class InfiniumX1Serial:
    def __init__(self, cfg: InfiniumSerialConfig):
        self.cfg = cfg
        self.ser = serial.Serial(
            port=cfg.serial.port,
            baudrate=cfg.serial.baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=cfg.serial.timeout,
        )

        # Adaptive parser (auto-detects which byte in each pair is the real signal)
        self._stream = MidiStream()

        # Motion state
        self._norm = 0.0
        self._ema: Optional[float] = None
        self._last_ts: Optional[float] = None
        self._vel_buf = deque(maxlen=6)
        self._acc_buf = deque(maxlen=6)
        self._throw_hist = deque()

        # Pickup / mapping state
        self._armed = False
        self._latched = True
        self._target_cc_value: Optional[int] = None
        self._page = cfg.layers.default_page if cfg.layers else "A"
        self._preset = None

    # ----- External control -----
    def set_page(self, page: str): self._page = page
    def set_preset(self, preset): self._preset = preset
    def set_target_value_for_pickup(self, cc_value_0_127: int):
        self._target_cc_value = max(0, min(127, int(cc_value_0_127)))
        self._armed = True
        self._latched = False

    # ----- Processing -----
    def process(self) -> Dict[str, object]:
        # 1) Read UART bytes and turn into events
        evts = self._poll_serial()

        # 2) Choose source for position (paircc preferred for this fader)
        pb_val14 = None
        learned_cc_val = None
        any_cc_val = None
        paircc_val = None

        for e in evts:
            if e[0] == "paircc":
                paircc_val = e[1]
            elif e[0] == "pb":
                _, _ch, v14 = e
                pb_val14 = v14
            elif e[0] == "cc":
                _, _ch, cc, val = e
                any_cc_val = val if any_cc_val is None else any_cc_val
                if self.cfg.learn_cc is not None and cc == self.cfg.learn_cc:
                    learned_cc_val = val

        if paircc_val is not None:
            norm_in = paircc_val / 127.0
        elif self.cfg.prefer_pitchbend and pb_val14 is not None:
            norm_in = max(0.0, min(1.0, pb_val14 / 16383.0))
        elif learned_cc_val is not None:
            norm_in = learned_cc_val / 127.0
        elif any_cc_val is not None:
            norm_in = any_cc_val / 127.0
        else:
            norm_in = getattr(self, "_norm", 0.0)

        # 3) Smoothing, velocity/accel, throw
        now = time.monotonic()
        self._update_motion_metrics(norm_in, now)
        out = self._apply_curve(self._ema if self._ema is not None else norm_in)
        self._norm = max(0.0, min(1.0, out))

        # 4) Mapping (zones -> dual -> single)
        cc_events: List[Tuple[int, int]] = []
        note_events: List[Tuple[int, bool]] = []
        zone_idx = None

        def to7(x: float) -> int: return int(round(max(0, min(127, x * 127))))
        val7 = to7(self._norm)

        if self.cfg.zones:
            for i, z in enumerate(self.cfg.zones):
                if z.lo <= self._norm < z.hi or (i == len(self.cfg.zones) - 1 and math.isclose(self._norm, 1.0)):
                    zone_idx = i
                    local = (self._norm - z.lo) / max(1e-6, (z.hi - z.lo))
                    local = self._apply_curve(local) * z.scale + z.offset
                    v7 = to7(local)
                    if self._handle_pickup(v7):
                        cc_events.append((z.cc, v7))
                    break

        elif self.cfg.dual:
            if self._norm < self.cfg.dual.split:
                local = self._norm / max(1e-6, self.cfg.dual.split)
                v7 = to7(self._apply_curve(local))
                if self._handle_pickup(v7):
                    cc_events.append((self.cfg.dual.bottom_cc, v7))
            else:
                local = (self._norm - self.cfg.dual.split) / max(1e-6, (1 - self.cfg.dual.split))
                v7 = to7(self._apply_curve(local))
                if self._handle_pickup(v7):
                    cc_events.append((self.cfg.dual.top_cc, v7))

        else:
            cc = self._cc_for_page_and_preset()
            if self._handle_pickup(val7):
                cc_events.append((cc, val7))

        # 5) Optional gesture side-CC (kept off by default in config)
        side = self._side_cc_for_page()
        if side is not None and (self.cfg.gesture.velocity_scale or self.cfg.gesture.accel_scale):
            v = 0.0 if not self._vel_buf else sum(self._vel_buf) / len(self._vel_buf)
            a = 0.0 if not self._acc_buf else sum(self._acc_buf) / len(self._acc_buf)
            v_cc = max(0, min(127, int(round(64 + self.cfg.gesture.velocity_scale * v * 64))))
            a_cc = max(0, min(127, int(round(64 + self.cfg.gesture.accel_scale * a * 32))))
            cc_events.extend([(side, v_cc), (side, a_cc)])

        # 6) Throw trigger
        if self.cfg.gesture.throw_note is not None and self._is_throw():
            note_events.append((self.cfg.gesture.throw_note, True))

        return {
            'cc_events': cc_events,
            'note_events': note_events,
            'zone': zone_idx,
            'latched': self._latched,
            'norm': self._norm
        }

    # ----- Helpers -----

    def _poll_serial(self):
        chunk = self.ser.read(128)
        if not chunk:
            return []
        return self._stream.feed(chunk)

    def _apply_curve(self, x: float) -> float:
        k = self.cfg.curve.kind
        x = max(0.0, min(1.0, x))
        if k == "linear": return x
        if k == "log":    return math.log1p(9 * x) / math.log(10)
        if k == "exp":    return x ** 2
        if k == "s":
            s = max(0.01, min(0.99, self.cfg.curve.s_strength))
            a = max(1e-6, x ** (1 - s))
            b = max(1e-6, (1 - x) ** (1 - s))
            return a / (a + b)
        return x

    def _update_motion_metrics(self, x: float, now: float):
        if self._ema is None:
            self._ema = x
        dt = 0.0 if self._last_ts is None else max(1e-6, now - self._last_ts)
        self._last_ts = now
        tau = self.cfg.filters.smoothing_ms / 1000.0
        alpha = 1.0 if tau <= 0 else min(1.0, dt / (tau + dt))
        self._ema = (1 - alpha) * self._ema + alpha * x

        last_out = getattr(self, "_last_out", self._ema)
        vel = (self._ema - last_out) / max(1e-6, dt)
        self._vel_buf.append(vel)
        if len(self._vel_buf) >= 2:
            acc = (self._vel_buf[-1] - self._vel_buf[-2]) / max(1e-6, dt)
            self._acc_buf.append(acc)
        self._last_out = self._ema

        # keep throw history within window
        self._throw_hist.append((now, self._ema))
        while self._throw_hist and now - self._throw_hist[0][0] > self.cfg.gesture.throw_window_s:
            self._throw_hist.popleft()

    def _is_throw(self) -> bool:
        if len(self._throw_hist) < 2:
            return False
        t0, x0 = self._throw_hist[0]
        t1, x1 = self._throw_hist[-1]
        return (t1 - t0) <= self.cfg.gesture.throw_window_s and abs(x1 - x0) >= self.cfg.gesture.throw_threshold

    def _handle_pickup(self, val7: int) -> bool:
        if not self.cfg.pickup.enabled or self._target_cc_value is None:
            self._latched = True
            return True
        if not self._armed:
            self._latched = True
            return True
        if abs(val7 - self._target_cc_value) <= self.cfg.pickup.deadband_cc:
            self._armed = False
            self._latched = True
            return True
        self._latched = False
        return False

    def _cc_for_page_and_preset(self) -> int:
        layers = self.cfg.layers
        if not layers:
            return 7
        page_cfg = layers.pages.get(self._page, {})
        preset_map = page_cfg.get('presets', {})
        if self._preset in preset_map:
            return int(preset_map[self._preset])
        return int(page_cfg.get('cc', 7))

    def _side_cc_for_page(self) -> Optional[int]:
        layers = self.cfg.layers
        if not layers:
            return None
        page_cfg = layers.pages.get(self._page, {})
        return page_cfg.get('side_cc')
