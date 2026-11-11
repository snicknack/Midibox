#!/usr/bin/env python3
import spidev, time

# SPI0 CE0 : SCLK=GPIO11, MISO=GPIO9, MOSI=GPIO10 (unused), CS=GPIO8
BUS, DEV = 0, 0

# Start with conservative clock. You can try 200_000 → 500_000 → 1_000_000
SPI_SPEED_HZ = 250_000
FRAME_BYTES  = 32          # tweak if you count a different length
SLEEP_BETWEEN_FRAMES = 0.010  # 10 ms

spi = spidev.SpiDev()
spi.open(BUS, DEV)
spi.mode = 0               # CPOL=0, CPHA=0
spi.max_speed_hz = SPI_SPEED_HZ
spi.bits_per_word = 8
spi.lsbfirst = False

print(f"SPI opened @ {SPI_SPEED_HZ} Hz, mode {spi.mode}. Reading {FRAME_BYTES} bytes per frame…")
prev = None
try:
    while True:
        # Send dummy bytes; read back on MISO (wired to board’s MOSI)
        rx = spi.xfer2([0x00] * FRAME_BYTES)
        # pretty print
        line = " ".join(f"{b:02X}" for b in rx)
        if rx != prev:
            print(line)
            prev = rx
        time.sleep(SLEEP_BETWEEN_FRAMES)
except KeyboardInterrupt:
    pass
finally:
    spi.close()
