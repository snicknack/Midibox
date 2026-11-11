# ads1115_reader.py — Clean, 4-channel I2C ADS1115 driver (single-ended)
# Works with Raspberry Pi + 3.3V logic

import time
import smbus2

class ADS1115Reader:
    """Simple ADS1115 16-bit ADC reader with single-ended channels A0–A3"""

    # Register addresses
    REG_CONVERT = 0x00
    REG_CONFIG = 0x01

    # Single-ended MUX configuration bits
    MUX_SINGLE = {
        0: 0b100,  # AIN0 to GND
        1: 0b101,  # AIN1 to GND
        2: 0b110,  # AIN2 to GND
        3: 0b111,  # AIN3 to GND
    }

    def __init__(self, address=0x48, busnum=1, gain=1, data_rate=0b111):
        self.bus = smbus2.SMBus(busnum)
        self.address = address
        self.gain = gain
        self.data_rate = data_rate
        self._last_ch = None

    def _write_config(self, mux_bits):
        """Write config for one-shot conversion"""
        config = (
            0x8000                                   # OS=1 (start single-shot)
            | (mux_bits << 12)                       # MUX
            | (0b001 << 9)                           # PGA ±4.096V
            | (1 << 8)                               # MODE = single-shot
            | (self.data_rate << 5)                  # DR bits
            | 0x0003                                 # comparator disable
        )
        # Write big-endian 16-bit value
        data = [(config >> 8) & 0xFF, config & 0xFF]
        self.bus.write_i2c_block_data(self.address, self.REG_CONFIG, data)

    def read_channel_raw(self, ch):
        """Return raw 16-bit signed integer from specified channel (0–3)."""
        if ch not in self.MUX_SINGLE:
            raise ValueError("Channel must be 0–3")

        mux_bits = self.MUX_SINGLE[ch]
        self._write_config(mux_bits)
        # Wait for conversion (~1.2ms @860SPS)
        time.sleep(0.002)
        result = self.bus.read_i2c_block_data(self.address, self.REG_CONVERT, 2)
        value = (result[0] << 8) | result[1]
        if value > 0x7FFF:
            value -= 0x10000
        return value

    def read_channel(self, ch):
        """Return normalized 0.0–1.0 value for 0–3.3V input"""
        raw = self.read_channel_raw(ch)
        return max(0.0, min(1.0, (raw + 32768) / 65535.0))

    def read_all_raw(self):
        """Return list of raw readings for all 4 channels"""
        return [self.read_channel_raw(i) for i in range(4)]

    def read_all(self):
        """Return normalized 0.0–1.0 for all 4 channels"""
        return [self.read_channel(i) for i in range(4)]


if __name__ == "__main__":
    adc = ADS1115Reader()
    print("Reading all channels (Ctrl+C to stop)...")
    while True:
        vals = adc.read_all()
        print([round(v, 3) for v in vals])
        time.sleep(0.1)
