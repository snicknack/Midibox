# midio/encoders_sx1509_poll2.py
# Original polling driver with ONE extra pushbutton on Arc1 (pin default=2).
# API unchanged:
#   - SX1509Encoders(addr=0x3E, pairs=[...], poll_hz=500, arc1_press_pin=2, use_hw_debounce=True, debounce_code=0b100)
#   - begin()
#   - read_and_zero() -> list of (idx, delta, pressed_bool)
#   - close()

from smbus2 import SMBus
from time import monotonic

I2C_BUS = 1

# SX1509 registers (subset)
REG_INPUT_DISABLE_B   = 0x00
REG_INPUT_DISABLE_A   = 0x01
REG_PULL_UP_B         = 0x06
REG_PULL_UP_A         = 0x07
REG_DIR_B             = 0x0E
REG_DIR_A             = 0x0F
REG_DATA_B            = 0x10
REG_DATA_A            = 0x11
REG_DEBOUNCE_CONFIG   = 0x22
REG_DEBOUNCE_ENABLE_B = 0x23
REG_DEBOUNCE_ENABLE_A = 0x24

def _wr8(addr, reg, val):
    with SMBus(I2C_BUS) as bus:
        bus.write_byte_data(addr, reg, val & 0xFF)

def _rd8(addr, reg):
    with SMBus(I2C_BUS) as bus:
        return bus.read_byte_data(addr, reg) & 0xFF

def _read_ports(addr):
    a = _rd8(addr, REG_DATA_A)
    b = _rd8(addr, REG_DATA_B)
    return a | (b << 8)   # 16-bit P15..P0

class SX1509Encoders:
    """
    Simple polling quadrature decoder for SX1509 + ONE Arc1 pushbutton.
    read_and_zero() returns a list of (idx, delta, pressed_bool).
      - For Arc1: pressed_bool reflects the *current* state, but we only emit a row on edge OR when delta!=0.
      - For other encoders: pressed_bool is always False (unchanged from your original behaviour).
    """
    def __init__(self, addr=0x3E, pairs=None, poll_hz=500,
                 arc1_press_pin=2, use_hw_debounce=True, debounce_code=0b100):
        # Encoders (A,B) pin pairs in your established order
        self.addr = addr
        self.pairs = pairs or [(0,1),(3,4),(6,7),(9,10),(12,13)]
        self.poll_hz = poll_hz
        self._period = 1.0/float(self.poll_hz)
        self._t_next = 0.0

        # ONE pushbutton on Arc1 only (active low, pull-up enabled)
        # Set to None if you want it disabled without changing code elsewhere.
        self.arc1_press_pin = arc1_press_pin
        self.use_hw_debounce = bool(use_hw_debounce)
        self.debounce_code = debounce_code & 0x07  # 0..7

        # State
        n = len(self.pairs)
        self._last_state = [0]*n      # (A<<1 | B)
        self._accum      = [0]*n      # counts per encoder

        # Arc1 switch state + edge latch
        self._arc1_level_last = 1     # with pull-up: 1=idle, 0=pressed
        self._arc1_pressed    = False # logical pressed
        self._arc1_edge       = None  # None / "press" / "release"

        # Quadrature LUT (x4) — unchanged
        self._lut = {
            (0,1):+1,(1,3):+1,(3,2):+1,(2,0):+1,
            (0,2):-1,(2,3):-1,(3,1):-1,(1,0):-1
        }

    def _enable_arc1_hw_debounce(self):
        """Enable SX1509 debounce on the Arc1 press pin only (if configured)."""
        if self.arc1_press_pin is None or not self.use_hw_debounce:
            return
        _wr8(self.addr, REG_DEBOUNCE_CONFIG, self.debounce_code)
        if self.arc1_press_pin < 8:
            maskA = (1 << self.arc1_press_pin)
            curA = _rd8(self.addr, REG_DEBOUNCE_ENABLE_A)
            _wr8(self.addr, REG_DEBOUNCE_ENABLE_A, curA | maskA)
        else:
            bitB = self.arc1_press_pin - 8
            maskB = (1 << bitB)
            curB = _rd8(self.addr, REG_DEBOUNCE_ENABLE_B)
            _wr8(self.addr, REG_DEBOUNCE_ENABLE_B, curB | maskB)

    def begin(self):
        # Configure all pins we touch as inputs; enable input buffers; enable pull-ups globally
        _wr8(self.addr, REG_DIR_A, 0xFF)
        _wr8(self.addr, REG_DIR_B, 0xFF)
        _wr8(self.addr, REG_INPUT_DISABLE_A, 0x00)
        _wr8(self.addr, REG_INPUT_DISABLE_B, 0x00)
        _wr8(self.addr, REG_PULL_UP_A, 0xFF)
        _wr8(self.addr, REG_PULL_UP_B, 0xFF)

        # Debounce ONLY Arc1 press pin (if requested)
        self._enable_arc1_hw_debounce()

        # Seed states
        ports = _read_ports(self.addr)
        for i,(a,b) in enumerate(self.pairs):
            self._last_state[i] = (((ports >> a) & 1) << 1) | ((ports >> b) & 1)
        if self.arc1_press_pin is not None:
            lvl = (ports >> self.arc1_press_pin) & 1
            self._arc1_level_last = lvl
            self._arc1_pressed = (lvl == 0)
            self._arc1_edge = None

        self._t_next = monotonic()
        return self

    def _sample_once(self):
        ports = _read_ports(self.addr)

        # Quadrature decode (unchanged)
        for i,(abit,bbit) in enumerate(self.pairs):
            a = (ports >> abit) & 1
            b = (ports >> bbit) & 1
            st  = (a<<1) | b
            prev = self._last_state[i]
            d = self._lut.get((prev, st), 0)
            if d:
                self._accum[i] += d
            self._last_state[i] = st

        # Arc1 press (active-low) — edge detect only
        if self.arc1_press_pin is not None:
            lvl = (ports >> self.arc1_press_pin) & 1
            if lvl != self._arc1_level_last:
                self._arc1_pressed = (lvl == 0)
                self._arc1_edge = "press" if self._arc1_pressed else "release"
                self._arc1_level_last = lvl

    def read_and_zero(self):
        """
        Poll at up to poll_hz and return list of (idx, delta, pressed_bool).
        Emits a row when:
          - any encoder i has non-zero delta, or
          - Arc1 button produced an edge (press/release) since last call.
        """
        out = []
        now = monotonic()
        if now >= self._t_next:
            self._sample_once()
            self._t_next = now + self._period

        # Encoders deltas
        for i,acc in enumerate(self._accum):
            if acc:
                pressed = (self._arc1_pressed if i == 0 else False)
                out.append((i, acc, pressed))
                self._accum[i] = 0

        # Arc1 button edge-only emission (even if delta==0)
        if self._arc1_edge is not None:
            out.append((0, 0, self._arc1_pressed))
            self._arc1_edge = None

        return out

    def close(self):
        # nothing persistent to tear down in polling mode
        pass
