# ads1115_mod.py
import time
from threading import Thread, Event
from smbus2 import SMBus
# If you already use Adafruit library, you can swap this block for it.
# The stub below just shows the callable API from main.

I2C_BUS = 1
ADS_ADDR = 0x48  # change if A0 tied

class ADS1115Reader:
    """
    Polls ADS1115 channels in a background thread and calls:
      on_sample(channel:int, value:int)  # raw ADC
    You can scale to volts in main if needed (FSR depends on PGA).
    """
    def __init__(self, addr=ADS_ADDR, rate_hz=200, channels=(0,1,2,3)):
        self.addr = addr
        self.rate_hz = rate_hz
        self.channels = channels
        self.on_sample = None
        self._t = None
        self._stop = Event()

    def on_sample_callback(self, fn):
        self.on_sample = fn

    # ---- minimal register ops (single-ended, PGA=±4.096V, DR=250SPS) ----
    REG_CONV = 0x00
    REG_CONF = 0x01

    def _wr16(self, reg, val):
        with SMBus(I2C_BUS) as bus:
            bus.write_i2c_block_data(self.addr, reg, [(val>>8)&0xFF, val&0xFF])

    def _rd16(self, reg):
        with SMBus(I2C_BUS) as bus:
            b = bus.read_i2c_block_data(self.addr, reg, 2)
            return (b[0]<<8) | b[1]

    def _start_single(self, ch):
        mux = {0:0b100,1:0b101,2:0b110,3:0b111}[ch]  # AINx vs GND
        conf =  (1<<15) | (mux<<12) | (0b001<<9) | (0b000<<8) | (0b100<<5) | (1<<8)
        # OS=1 (start), MUX, PGA=±4.096V, MODE=single, DR=250SPS, COMP disabled
        self._wr16(self.REG_CONF, conf)

    def _read_single(self, ch):
        self._start_single(ch)
        time.sleep(1/250.0 + 0.001)  # tiny margin
        v = self._rd16(self.REG_CONV)
        if v & 0x8000: v -= 1<<16  # sign
        return v

    # ---- thread loop ----
    def begin(self):
        if self._t and self._t.is_alive(): return
        self._stop.clear()
        self._t = Thread(target=self._run, daemon=True)
        self._t.start()

    def _run(self):
        period = 1.0 / float(self.rate_hz)
        while not self._stop.is_set():
            t0 = time.time()
            for ch in self.channels:
                val = self._read_single(ch)
                if self.on_sample:
                    self.on_sample(ch, val)
            dt = time.time() - t0
            if dt < period:
                time.sleep(period - dt)

    def close(self):
        self._stop.set()
        if self._t: self._t.join(timeout=1.0)
