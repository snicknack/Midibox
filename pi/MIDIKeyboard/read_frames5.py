#!/usr/bin/env python3
import spidev, time

spi = spidev.SpiDev()
spi.open(0, 0)            # <— CE0 = GPIO8
spi.max_speed_hz = 500000
spi.mode = 0
spi.no_cs = False         # let driver toggle CS
spi.cshigh = False        # CS active LOW

print("Watch GPIO8/CE0 – it should pulse LOW during each transfer.")
try:
    while True:
        spi.xfer2([0x00]*8)
        time.sleep(0.1)
except KeyboardInterrupt:
    spi.close()
