#!/usr/bin/env python3
import spidev, RPi.GPIO as GPIO, time

# SPI0 (SCLK=GPIO11, MISO=GPIO9). MOSI from Pi is unused.
BUS, DEV = 0, 0
SPI_SPEED_HZ = 250_000
FRAME_BYTES  = 32

# Choose a free GPIO for CS:
CS_GPIO = 25   # BCM 25 (pin 22)

GPIO.setmode(GPIO.BCM)
GPIO.setup(CS_GPIO, GPIO.OUT, initial=GPIO.HIGH)

spi = spidev.SpiDev()
spi.open(BUS, DEV)          # /dev/spidev0.0
spi.mode = 3                # Mode-0
spi.max_speed_hz = SPI_SPEED_HZ
spi.bits_per_word = 8
spi.no_cs = True            # IMPORTANT: driver will NOT touch CE0

def read_frame(n=FRAME_BYTES):
    GPIO.output(CS_GPIO, GPIO.LOW)       # assert CS (active-low)
    rx = spi.xfer2([0x00]*n)             # Pi provides SCLK; reads board MOSI on MISO
    GPIO.output(CS_GPIO, GPIO.HIGH)      # deassert CS
    return rx

print("Manual-CS reader running. Ctrl+C to stop.")
prev = None
try:
    while True:
        rx = read_frame()
        if prev != rx:
            print(" ".join(f"{b:02X}" for b in rx))
            prev = rx
        time.sleep(0.01)
except KeyboardInterrupt:
    pass
finally:
    spi.close()
    GPIO.cleanup()
