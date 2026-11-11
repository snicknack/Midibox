# encoders_sx1509.py
from smbus2 import SMBus
import RPi.GPIO as GPIO

I2C_BUS = 1

# --- SX1509 registers (subset) ---
REG_INPUT_DISABLE_B = 0x00
REG_INPUT_DISABLE_A = 0x01
REG_PULL_UP_B       = 0x06
REG_PULL_UP_A       = 0x07
REG_DIR_B           = 0x0E
REG_DIR_A           = 0x0F
REG_DATA_B          = 0x10
REG_DATA_A          = 0x11
REG_INT_MASK_B      = 0x12
REG_INT_MASK_A      = 0x13
REG_SENSE_LOW_B     = 0x16
REG_SENSE_HIGH_B    = 0x17
REG_SENSE_LOW_A     = 0x14
REG_SENSE_HIGH_A    = 0x15
REG_INT_SRC_B       = 0x18
REG_INT_SRC_A       = 0x19

class SX1509Encoders:
    """
    Interrupt-driven SX1509 encoder reader.
    Callbacks:
      on_step(enc_idx:int, delta:int)  # +1 / -1
    """
    def __init__(self, i2c_addr=0x3E, int_pin=17, pairs=None):
        self.addr = i2c_addr
        self.int_pin = int_pin
        self.pairs = pairs or [(0,1),(3,4),(6,7),(9,10),(12,13)]
        self.last_state = [0]*len(self.pairs)
        self.on_step = None

    # --- low-level helpers ---
    def _wr(self, reg, val):
        with SMBus(I2C_BUS) as bus:
            bus.write_byte_data(self.addr, reg, val & 0xFF)

    def _rd(self, reg):
        with SMBus(I2C_BUS) as bus:
            return bus.read_byte_data(self.addr, reg)

    def _read_ports(self):
        a = self._rd(REG_DATA_A)
        b = self._rd(REG_DATA_B)
        return a | (b<<8)

    # --- init ---
    def begin(self):
        # all inputs
        self._wr(REG_DIR_A, 0xFF)
        self._wr(REG_DIR_B, 0xFF)
        # enable input buffers
        self._wr(REG_INPUT_DISABLE_A, 0x00)
        self._wr(REG_INPUT_DISABLE_B, 0x00)
        # pull-ups ON (A/B idle high)
        self._wr(REG_PULL_UP_A, 0xFF)
        self._wr(REG_PULL_UP_B, 0xFF)

        # INT mask (0 = enabled) only on used pins
        mask_a, mask_b = 0xFF, 0xFF
        for a,b in self.pairs:
            (mask_a, mask_b) = (
                mask_a & ~(1<<a) if a<=7 else mask_a,
                mask_b & ~(1<<(a-8)) if a>=8 else mask_b
            )
            (mask_a, mask_b) = (
                mask_a & ~(1<<b) if b<=7 else mask_a,
                mask_b & ~(1<<(b-8)) if b>=8 else mask_b
            )
        self._wr(REG_INT_MASK_A, mask_a)
        self._wr(REG_INT_MASK_B, mask_b)

        # set BOTH edges for all used pins (2 bits per pin)
        def set_both_edge(reg_low, reg_high, pins):
            low  = self._rd(reg_low)
            high = self._rd(reg_high)
            for p in pins:
                if p < 4:
                    s = p*2
                    low  = (low  & ~(0b11<<s)) | (0b11<<s)
                else:
                    s = (p-4)*2
                    high = (high & ~(0b11<<s)) | (0b11<<s)
            self._wr(reg_low, low); self._wr(reg_high, high)

        pinsA = sorted({p for ab in self.pairs for p in ab if p<=7})
        pinsB = sorted({p-8 for ab in self.pairs for p in ab if p>=8})
        set_both_edge(REG_SENSE_LOW_A,  REG_SENSE_HIGH_A,  pinsA)
        set_both_edge(REG_SENSE_LOW_B,  REG_SENSE_HIGH_B,  pinsB)

        # clear ints, seed last_state
        _ = self._rd(REG_INT_SRC_A); _ = self._rd(REG_INT_SRC_B)
        p = self._read_ports()
        for i,(a,b) in enumerate(self.pairs):
            self.last_state[i] = ((p>>a)&1)<<1 | ((p>>b)&1)

        # INT pin on Pi
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.int_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.int_pin, GPIO.FALLING, callback=self._on_int, bouncetime=1)

    def on_step_callback(self, fn):
        self.on_step = fn

    def _decode(self, i, a_bit, b_bit, port16):
        a = (port16 >> a_bit) & 1
        b = (port16 >> b_bit) & 1
        st  = (a<<1) | b
        prev = self.last_state[i]
        lut = { (0,1):+1,(1,3):+1,(3,2):+1,(2,0):+1,
                (0,2):-1,(2,3):-1,(3,1):-1,(1,0):-1 }
        delta = lut.get((prev,st),0)
        self.last_state[i] = st
        return delta

    def _on_int(self, _ch):
        # latch sources (reading clears), then sample once
        _ = self._rd(REG_INT_SRC_A); _ = self._rd(REG_INT_SRC_B)
        ports = self._read_ports()
        for i,(a,b) in enumerate(self.pairs):
            d = self._decode(i,a,b,ports)
            if d and self.on_step:
                self.on_step(i, d)

    def close(self):
        try:
            GPIO.remove_event_detect(self.int_pin)
        except Exception:
            pass
        GPIO.cleanup(self.int_pin)
