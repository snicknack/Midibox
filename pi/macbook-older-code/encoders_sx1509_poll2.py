# midio/encoders_sx1509_poll2.py
# Polling-only SX1509 encoder reader (no GPIO/INT required)

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
    API:
      begin()
      read_and_zero() -> list[(idx, delta, pressed_bool=False)]
      close()
    """
    def __init__(self, addr=0x3E, pairs=None, poll_hz=500):
        self.addr = addr
        self.pairs = pairs or [(0,1),(3,4),(6,7),(9,10),(12,13)]
        self.poll_hz = poll_hz
        self._last_state = [0]*len(self.pairs)
        self._accum = [0]*len(self.pairs)
        self._t_next = 0.0
        self._period = 1.0/float(self.poll_hz)

    def begin(self):
        # Configure pins as inputs with pull-ups enabled.
        _wr8(self.addr, REG_DIR_A, 0xFF)
        _wr8(self.addr, REG_DIR_B, 0xFF)
        _wr8(self.addr, REG_INPUT_DISABLE_A, 0x00)  # enable input buffers
        _wr8(self.addr, REG_INPUT_DISABLE_B, 0x00)
        _wr8(self.addr, REG_PULL_UP_A, 0xFF)        # pull-ups ON
        _wr8(self.addr, REG_PULL_UP_B, 0xFF)
        # Seed last state
        ports = _read_ports(self.addr)
        for i,(a,b) in enumerate(self.pairs):
            self._last_state[i] = (((ports >> a) & 1) << 1) | ((ports >> b) & 1)
        self._t_next = monotonic()
        return self

    def _sample_once(self):
        ports = _read_ports(self.addr)
        # decode each encoder
        for i,(abit,bbit) in enumerate(self.pairs):
            a = (ports >> abit) & 1
            b = (ports >> bbit) & 1
            st  = (a<<1) | b
            prev = self._last_state[i]
            # quadrature LUT (+1 / -1 / 0)
            lut = {
                (0,1):+1,(1,3):+1,(3,2):+1,(2,0):+1,
                (0,2):-1,(2,3):-1,(3,1):-1,(1,0):-1
            }
            d = lut.get((prev, st), 0)
            if d:
                self._accum[i] += d
            self._last_state[i] = st

    def read_and_zero(self):
        """
        Poll at up to poll_hz. Returns list of (idx, delta, False)
        since we're not reading push switches here.
        """
        out = []
        now = monotonic()
        # Ensure at least one sample per call; if loop runs faster, rate-limit
        if now >= self._t_next:
            self._sample_once()
            self._t_next = now + self._period

        for i,acc in enumerate(self._accum):
            if acc:
                out.append((i, acc, False))
                self._accum[i] = 0
        return out

    def close(self):
        # nothing persistent to tear down in polling mode
        pass
