#!/usr/bin/env python3
# Minimal FT6236/FT6206 touch reader via I2C (addr 0x38)

import time
try:
    from smbus import SMBus          # from python3-smbus (apt)
except ImportError:
    from smbus2 import SMBus         # fallback if you used pip install smbus2

I2C_BUS = 1           # Pi's GPIO2/3 bus
ADDR    = 0x38

# FT6236 registers
REG_TD_STATUS = 0x02  # number of touches (0..2)
REG_TOUCH1    = 0x03  # XH, XL, YH, YL, then weight, misc

def read_touch(bus):
    """Returns list of touches: [{'x':int,'y':int,'event':int}]"""
    # Read 7 bytes starting at 0x02: TD_STATUS + first touch block
    data = bus.read_i2c_block_data(ADDR, REG_TD_STATUS, 7)
    n = data[0] & 0x0F
    touches = []
    if n >= 1:
        xh = data[1]; xl = data[2]; yh = data[3]; yl = data[4]
        event = (xh >> 6) & 0x03     # 0:down 1:up 2:contact 3:reserved
        x = ((xh & 0x0F) << 8) | xl
        y = ((yh & 0x0F) << 8) | yl
        touches.append({"x": x, "y": y, "event": event})
    # (Chip can report a 2nd touch at 0x09..0x0E if needed)
    return touches

if __name__ == "__main__":
    bus = SMBus(I2C_BUS)
    print("FT6236 minimal test. Tap the screen (Ctrl+C to quit).")
    try:
        while True:
            t = read_touch(bus)
            if t:
                # If your axes are flipped/rotated, tweak here:
                # x, y = t[0]['y'], t[0]['x']         # swap axes
                # x, y = 239 - x, 319 - y            # invert
                print(f"touch: x={t[0]['x']:4d}  y={t[0]['y']:4d}  event={t[0]['event']}")
                time.sleep(0.02)
            else:
                time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        bus.close()
