# infinium_x1_serial.py
# Behringer Infinium X1 (serial @ 31250 baud, 3.3V TTL) → expressive fader driver.
# Reads raw MIDI-like bytes from /dev/serial0, decodes CC or Pitch Bend,
# and exposes a normalized 0..1 position with velocity/accel, zones, pickup, etc.

from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque
import time, math, threading
from typing import Optional, Dict, List, Tuple
import serial  # pip install pyserial

# ---- Configs ----

@dataclass
class SerialConfig:
    port: str = "/dev/serial0"
    baud: int = 31250
    timeout: float = 0.001      # seconds (non-blocking)

@dataclass
class FilterConfig:
    smoothing_ms: int = 6       # EMA time constant
    rate_hz: int = 500          # internal timing for velocity/accel calc

@dataclass
class CurveConfig:
    kind: str = "linear"        # "linear"|"log"|"exp"|"s"
    s_strength: float = 0.6

@dataclass
class PickupConfig:
    enabled: bool = True
    deadband_cc: int = 3

@dataclass
class GestureConfig:
    velocity_scale: float = 1.0
    accel_scale: float = 0.4
    throw_threshold: float = 0.85
    throw_window_s: float = 0.25
    throw_note: Optional[int] = None

@dataclass
class Zone:
    lo: float; hi: float; cc: int
    alt_cc: Optional[int] = None
    scale: float = 1.0
    offset: float = 0.0

@dataclass
class DualMapping:
    bottom_cc:int; top_cc:int; split:float=0.5

@dataclass
class MappingLayers:
    pages: Dict[str, Dict] = field(default_factory=dict)  # e.g., {"A":{"cc":74,"side_cc":71}, "B":{"cc":91}}
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
    fourteen_bit: bool = True
    midi_channel: int = 1
    layers: Optional[MappingLayers] = None
    # Input interpretation
    prefer_pitchbend: bool = True   # if device sends pitch bend, use it as primary
    learn_cc: Optional[int] = None  # if set, use this CC id as the primary source

# ---- MIDI decoder (minimal but solid) ----

class MidiStream:
    """
    Robust MIDI byte stream parser that tolerates running-status-only streams.
    If no status has been seen yet but data bytes arrive in even pairs, we emit PB events.
    """
    def __init__(self, default_mode="pb"):
        self.status = None
        self._pair = []
        self.default_mode = default_mode  # "pb" or "cc"

    def feed(self, data: bytes):
        events = []
        i = 0
        while i < len(data):
            b = data[i]
            if b & 0x80:
                # status byte
                self.status = b
                self._pair.clear()
                i += 1
                continue

            # data byte
            if self.status is None:
                # No status yet (running-status-only stream) -> infer pairs
                self._pair.append(b)
                if len(self._pair) == 2:
                    if self.default_mode == "pb":
                        lsb, msb = self._pair
                        events.append(("pb", 1, (msb << 7) | lsb))  # assume ch 1
                    else:
                        cc, val = self._pair
                        events.append(("cc", 1, cc, val))
                    self._pair.clear()
                i += 1
                continue

            st = self.status & 0xF0
            ch = (self.status & 0x0F) + 1

            if st == 0xE0:  # Pitch Bend
                if i + 1 < len(data):
                    lsb = data[i]
                    msb = data[i + 1]
                    events.append(("pb", ch, (msb << 7) | lsb))
                    i += 2
                else:
                    break
            elif st == 0xB0:  # Control Change
                if i + 1 < len(data):
                    cc = data[i]
                    val = data[i + 1]
                    events.append(("cc", ch, cc, val))
                    i += 2
                else:
                    break
            elif self.status == 0xFE:  # Active Sensing
                i += 1
            else:
                # Skip unknown; try to move ahead by 1
                i += 1
        return events


# ---- Driver: converts MIDI events to normalized position and expressive outputs ----

class InfiniumX1Serial:
    def __init__(self, cfg: InfiniumSerialConfig):
        self.cfg = cfg
        self._ser = serial.Serial(
            port=cfg.serial.port,
            baudrate=cfg.serial.baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=cfg.serial.timeout,
            pickup=PickupConfig(enabled=False),
        )
        self._stream = MidiStream(default_mode="cc")
        self._norm = 0.0
        self._ema = None
        self._last_ts = None
        self._vel_buf = deque(maxlen=6)
        self._acc_buf = deque(maxlen=6)
        self._throw_hist = deque()
        self._armed = False
        self._latched = True
        self._target_cc_value = None
        self._page = cfg.layers.default_page if cfg.layers else "A"
        self._preset = None
        self._lock = threading.Lock()

    # --- Control surface API ---
    def set_page(self, page:str): self._page = page
    def set_preset(self, preset): self._preset = preset
    def set_target_value_for_pickup(self, cc_value_0_127:int):
        self._target_cc_value = max(0,min(127,int(cc_value_0_127)))
        self._armed = True
        self._latched = False

    # --- Read/Decode/update ---
    def _poll_serial(self):
        chunk = self._ser.read(128)
        if not chunk: return []
        return self._stream.feed(chunk)

    def _apply_curve(self, x:float)->float:
        k = self.cfg.curve.kind
        if k == "linear": return x
        if k == "log":    return math.log1p(9*x)/math.log(10)
        if k == "exp":    return x*x
        if k == "s":
            s = max(0.01,min(0.99,self.cfg.curve.s_strength))
            return x**(1-s)/((x**(1-s)+(1-x)**(1-s)) or 1e-6)
        return x

    def _update_motion_metrics(self, x:float, now:float):
        if self._ema is None: self._ema = x
        dt = 0.0 if self._last_ts is None else max(1e-6, now-self._last_ts)
        self._last_ts = now
        tau = self.cfg.filters.smoothing_ms/1000.0
        alpha = 1.0 if tau<=0 else min(1.0, dt/(tau+dt))
        self._ema = (1-alpha)*self._ema + alpha*x
        vel = (self._ema - getattr(self, "_last_out", self._ema))/max(1e-6, dt)
        self._vel_buf.append(vel)
        if len(self._vel_buf) >= 2:
            acc = (self._vel_buf[-1]-self._vel_buf[-2])/max(1e-6, dt)
            self._acc_buf.append(acc)
        self._last_out = self._ema
        # throw history
        self._throw_hist.append((now, self._ema))
        while self._throw_hist and now - self._throw_hist[0][0] > self.cfg.gesture.throw_window_s:
            self._throw_hist.popleft()

    def _is_throw(self)->bool:
        if len(self._throw_hist) < 2: return False
        t0,x0 = self._throw_hist[0]; t1,x1 = self._throw_hist[-1]
        return (t1-t0) <= self.cfg.gesture.throw_window_s and abs(x1-x0) >= self.cfg.gesture.throw_threshold

    def _handle_pickup(self, val7:int)->bool:
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

    def _cc_for_page_and_preset(self)->int:
        layers = self.cfg.layers
        if not layers: return 7
        page_cfg = layers.pages.get(self._page, {})
        preset_map = page_cfg.get('presets', {})
        if self._preset in preset_map: return int(preset_map[self._preset])
        return int(page_cfg.get('cc', 7))

    def _side_cc_for_page(self)->Optional[int]:
        layers = self.cfg.layers
        if not layers: return None
        page_cfg = layers.pages.get(self._page, {})
        return page_cfg.get('side_cc')

    # --- Public: step the engine once; returns event dict like before ---
    def process(self) -> Dict[str, object]:
        # 1) Read and decode any incoming MIDI bytes from the fader
        evts = self._poll_serial()

        # 2) Choose the best source for "position"
        #    Preference: Pitch Bend (14-bit) if present and allowed; else learned CC; else any CC seen.
        pb_val14 = None
        learned_cc_val = None
        any_cc_val = None

        for e in evts:
            if e[0] == "pb":
                _, ch, v14 = e
                pb_val14 = v14
            elif e[0] == "cc":
                _, ch, cc, val = e
                any_cc_val = val if any_cc_val is None else any_cc_val
                if self.cfg.learn_cc is not None and cc == self.cfg.learn_cc:
                    learned_cc_val = val

        # 3) Convert to normalized 0..1
        if self.cfg.prefer_pitchbend and pb_val14 is not None:
            norm = max(0.0, min(1.0, pb_val14/16383.0))
        elif learned_cc_val is not None:
            norm = learned_cc_val/127.0
        elif any_cc_val is not None:
            norm = any_cc_val/127.0
        else:
            # no new bytes → keep previous output (still update smoothing to maintain timing)
            norm = getattr(self, "_norm", 0.0)

        now = time.monotonic()
        self._update_motion_metrics(norm, now)
        out = self._apply_curve(self._ema)
        self._norm = max(0.0, min(1.0, out))

        # 4) Build higher-level behaviors (zones / dual / single target)
        cc_events: List[Tuple[int,int]] = []
        note_events: List[Tuple[int,bool]] = []
        zone_idx = None

        def to7(x:float)->int: return int(round(max(0,min(127, x*127))))
        val7 = to7(self._norm)

        # Zones
        if self.cfg.zones:
            for i,z in enumerate(self.cfg.zones):
                if z.lo <= self._norm < z.hi or (i==len(self.cfg.zones)-1 and math.isclose(self._norm,1.0)):
                    zone_idx = i
                    local = (self._norm - z.lo)/max(1e-6, (z.hi - z.lo))
                    local = self._apply_curve(local)*z.scale + z.offset
                    val7z = to7(local)
                    if self._handle_pickup(val7z):
                        cc_events.append((z.cc, val7z))
                    break
        # Dual
        elif self.cfg.dual:
            if self._norm < self.cfg.dual.split:
                local = self._norm / max(1e-6, self.cfg.dual.split)
                val7d = to7(self._apply_curve(local))
                if self._handle_pickup(val7d):
                    cc_events.append((self.cfg.dual.bottom_cc, val7d))
            else:
                local = (self._norm - self.cfg.dual.split)/max(1e-6, (1-self.cfg.dual.split))
                val7d = to7(self._apply_curve(local))
                if self._handle_pickup(val7d):
                    cc_events.append((self.cfg.dual.top_cc, val7d))
        # Single mapping (page/preset aware)
        else:
            cc = self._cc_for_page_and_preset()
            if self._handle_pickup(val7):
                cc_events.append((cc, val7))

        # Gestures (velocity/accel to side-CC)
        v = 0.0 if not self._vel_buf else sum(self._vel_buf)/len(self._vel_buf)
        a = 0.0 if not self._acc_buf else sum(self._acc_buf)/len(self._acc_buf)
        side = self._side_cc_for_page()
        if side is not None:
            v_cc = max(0,min(127,int(round(64 + self.cfg.gesture.velocity_scale * v*64))))
            a_cc = max(0,min(127,int(round(64 + self.cfg.gesture.accel_scale * a*32))))
            cc_events.extend([(side, v_cc), (side, a_cc)])

        # “Throw” trigger (fast long move) → note
        if self.cfg.gesture.throw_note is not None and self._is_throw():
            note_events.append((self.cfg.gesture.throw_note, True))

        return {'cc_events': cc_events, 'note_events': note_events,
                'zone': zone_idx, 'latched': self._latched, 'norm': self._norm}
