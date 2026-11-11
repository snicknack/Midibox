# midibox/io/sx1509.py
from smbus2 import SMBus
import time

# SX1509 registers (subset)
REG_INPUT_DISABLE_B = 0x00
REG_INPUT_DISABLE_A = 0x01
REG_PULL_UP_B       = 0x06
REG_PULL_UP_A       = 0x07
REG_PULL_DOWN_B     = 0x08
REG_PULL_DOWN_A     = 0x09
REG_OPEN_DRAIN_B    = 0x0A
REG_OPEN_DRAIN_A    = 0x0B
REG_DIR_B           = 0x0E
REG_DIR_A           = 0x0F
REG_DATA_B          = 0x10
REG_DATA_A          = 0x11
REG_INTERRUPT_MASK_B= 0x12
REG_INTERRUPT_MASK_A= 0x13
REG_SENSE_HIGH_B    = 0x14
REG_SENSE_LOW_B     = 0x15
REG_SENSE_HIGH_A    = 0x16
REG_SENSE_LOW_A     = 0x17
REG_INTERRUPT_SRC_B = 0x18
REG_INTERRUPT_SRC_A = 0x19
REG_EVENT_STATUS_B  = 0x1A
REG_EVENT_STATUS_A  = 0x1B
REG_DEBOUNCE_CONFIG = 0x22
REG_DEBOUNCE_ENABLE_B=0x23
REG_DEBOUNCE_ENABLE_A=0x24
REG_KEY_CONFIG_1    = 0x25
REG_KEY_CONFIG_2    = 0x26
REG_RESET           = 0x7D
REG_CLOCK           = 0x1E

def _lo(n): return n & 0xFF
def _hi(n): return (n>>8) & 0xFF

class SX1509:
    def __init__(self, i2c_bus=1, address=0x3E, rst_gpio=None):
        self.addr = address
        self.bus = SMBus(i2c_bus)
        self.rst_gpio = rst_gpio
        if self.rst_gpio is not None:
            # optional: export/toggle with gpiozero/RPi.GPIO if you like
            pass
        self.reset()
        self._init_clock()

    def reset(self):
        # 2-step unlock per datasheet
        self._write(REG_RESET, 0x12)
        self._write(REG_RESET, 0x34)
        time.sleep(0.001)

    def _init_clock(self):
        # Internal 2MHz, no divider
        self._write(REG_CLOCK, 0b01000000)

    def _read(self, reg):
        return self.bus.read_byte_data(self.addr, reg)

    def _write(self, reg, val):
        self.bus.write_byte_data(self.addr, reg, val)

    def _read_pair(self, reg_lo):
        lo = self._read(reg_lo)
        hi = self._read(reg_lo + 1)
        return lo | (hi<<8)

    def _write_pair(self, reg_lo, value16):
        self._write(reg_lo, _lo(value16))
        self._write(reg_lo + 1, _hi(value16))

    # --- GPIO setup helpers ---
    def set_dir_inputs(self, mask16):
        # 1 = input, 0 = output
        self._write_pair(REG_DIR_B, mask16)

    def enable_pullups(self, mask16):
        self._write_pair(REG_PULL_UP_B, mask16)

    def disable_input_buffer(self, mask16):
        self._write_pair(REG_INPUT_DISABLE_B, mask16)

    def set_interrupt_mask(self, mask16):
        # 1 = masked (disabled), 0 = enabled
        self._write_pair(REG_INTERRUPT_MASK_B, mask16)

    def set_edge_sense(self, mask_rising16, mask_falling16):
        # Sense registers encode per-pin edge config (00=none 01=rising 10=falling 11=both)
        def build_sense(low_reg, high_reg, rising, falling):
            val = 0
            for pin in range(0,8):
                both = ((rising>>pin)&1)<<0 | ((falling>>pin)&1)<<1
                val |= (both & 0x3) << (pin*2)
            self._write(low_reg, val & 0xFF)
            self._write(high_reg, (val>>8) & 0xFF)

        build_sense(REG_SENSE_LOW_B, REG_SENSE_HIGH_B, mask_rising16, mask_falling16)
        build_sense(REG_SENSE_LOW_A, REG_SENSE_HIGH_A, mask_rising16>>8, mask_falling16>>8)

    def set_debounce(self, enable_mask16, time_sel=0b100):  # ~2ms @ 2MHz
        self._write(REG_DEBOUNCE_CONFIG, time_sel & 0x07)
        self._write_pair(REG_DEBOUNCE_ENABLE_B, enable_mask16)

    def read_inputs(self):
        # returns 16-bit (P0 = bit0 … P15 = bit15), 1=HIGH
        return self._read_pair(REG_DATA_B)

    def clear_interrupts(self):
        # read to clear
        _ = self._read_pair(REG_INTERRUPT_SRC_B)
        _ = self._read_pair(REG_EVENT_STATUS_B)
