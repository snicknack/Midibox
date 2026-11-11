# midio/encoders_sx1509_poll2.py
# Polling-only SX1509 encoder reader with button support (old-style).
# Keeps the original API and behavior; just adds reading the press pins.

from smbus2 import SMBus
from time import monotonic

I2C_BUS = 1

# SX1509 registers (subset)
REG_INPUT_DISABLE_B = 0x00
REG_INPUT_DISABLE_A = 0x01
REG_PULL_UP_B       = 0x06
REG_PULL_UP_A       = 0x07
REG_DIR_B           = 0x0E
REG_DIR_A           = 0x0F
REG_DATA_B          = 0x10
REG_DATA_A          = 0x11
# Optional debounce regs (leave off for legacy feel)
#REG_DEBOUNCE_CONFIG   = 0x22
#REG_DEBOUNCE_ENABLE_B = 0x23
#REG_DEBOUNCE_ENABLE_A = 0x24

def _wr8(addr, reg, val):
    with SMBus(I2C_BUS) as bus:
        bus.write_byte_data(addr, reg, val & 0xFF)

def _rd8(addr, reg):
    with SMBus(I2C_BUS) as bus:
        return bus.read_byte_data(addr, reg) & 0xFF

def _read_ports(addr):
    a = _rd8(addr, REG_DATA_A)
    b = _rd8(addr, REG_DATA_B)
    return a | (b << 8)   # 16-bit P15..P0 (bit N corresponds to PN)

class SX1509Encoders:
    """
    Simple polling quadrature decoder for SX1509.
    API (unchanged from your original):
      begin()
      read_and_zero() -> list[(idx, delta, pressed_bool)]
      close()
    """
    def __init__(self, addr=0x3E, pairs=None, poll_hz=500, presses=None, use_hw_debounce=False, debounce_code=0b100):
        # pairs: list of (A,B) pins
        # presses: list of press pin numbers aligned with pairs; if omitted, use defaults
        self.addr = addr
        self.pairs = pairs or [(0,1),(3,4),(6,7),(9,10),(12,13)]
        if presses is None:
            # default for your arc1..4 + tempo layout
            presses = [2,5,8,11,14][:len(self.pairs)]
        self.presses = presses
        self.poll_hz = poll_hz
        self._period = 1.0/float(self.poll_hz)
        self._t_next = 0.0

        # state
        self._last_state = [0]*len(self.pairs)   # (A<<1 | B)
        self._accum      = [0]*len(self.pairs)   # counts per encoder
        self._last_sw    = [1]*len(self.pairs)   # last switch level (1=idle, 0=pressed), pull-ups on
        self._pressed    = [False]*len(self.pairs)  # current pressed state

        # config
        self.use_hw_debounce = use_hw_debounce
        self.debounce_code = debounce_code & 0x07  # 0..7

        # quadrature LUT (+1/-1/0)
        self._lut = {
            (0,1):+1,(1,3):+1,(3,2):+1,(2,0):+1,
            (0,2):-1,(2,3):-1,(3,1):-1,(1,0):-1
        }

    def _enable_hw_debounce(self):
        # Enable debounce on the press pins only (enc A/B left “raw” for legacy feel)
        if not self.use_hw_debounce:
            return
        # Set global debounce time
        _wr8(self.addr, REG_DEBOUNCE_CONFIG, self.debounce_code)
        # Build masks per bank
        maskA = 0
        maskB = 0
        for sw in self.presses:
            if sw < 8: maskA |= (1 << sw)
            else:      maskB |= (1 << (sw-8))
        # Enable debounce on those pins
        _wr8(self.addr, REG_DEBOUNCE_ENABLE_A, maskA)
        _wr8(self.addr, REG_DEBOUNCE_ENABLE_B, maskB)

    def begin(self):
        # Configure all pins we touch as inputs, enable input buffers, turn pull-ups on.
        _wr8(self.addr, REG_DIR_A, 0xFF)
        _wr8(self.addr, REG_DIR_B, 0xFF)
        _wr8(self.addr, REG_INPUT_DISABLE_A, 0x00)  # input buffers enabled
        _wr8(self.addr, REG_INPUT_DISABLE_B, 0x00)
        _wr8(self.addr, REG_PULL_UP_A, 0xFF)        # pull-ups ON
        _wr8(self.addr, REG_PULL_UP_B, 0xFF)

        # Optional: enable HW debounce on press pins
        self._enable_hw_debounce()

        # Seed last A/B and switch states
        ports = _read_ports(self.addr)
        for i,(a,b) in enumerate(self.pairs):
            self._last_state[i] = (((ports >> a) & 1) << 1) | ((ports >> b) & 1)
        for i,sw in enumerate(self.presses):
            self._last_sw[i] = (ports >> sw) & 1
            self._pressed[i] = (self._last_sw[i] == 0)

        self._t_next = monotonic()
        return self

    def _sample_once(self):
        ports = _read_ports(self.addr)

        # decode each encoder A/B
        for i,(abit,bbit) in enumerate(self.pairs):
            a = (ports >> abit) & 1
            b = (ports >> bbit) & 1
            st  = (a<<1) | b
            prev = self._last_state[i]
            d = self._lut.get((prev, st), 0)
            if d:
                self._accum[i] += d
            self._last_state[i] = st

        # read presses (active-low)
        for i,sw in enumerate(self.presses):
            level = (ports >> sw) & 1
            if level != self._last_sw[i]:
                # update current pressed state (level 0 = pressed)
                self._pressed[i] = (level == 0)
                self._last_sw[i] = level

    def read_and_zero(self):
        """
        Poll at up to poll_hz and return list of (idx, delta, pressed_bool).
        'pressed_bool' is the current button state (True=held down), not an edge.
        """
        out = []
        now = monotonic()
        # At least one sample per call; rate-limit if loop is faster
        if now >= self._t_next:
            self._sample_once()
            self._t_next = now + self._period

        for i,acc in enumerate(self._accum):
            if acc or self._pressed[i]:
                out.append((i, acc, self._pressed[i]))
                self._accum[i] = 0
        return out

    def close(self):
        # nothing persistent to tear down in polling mode
        pass
