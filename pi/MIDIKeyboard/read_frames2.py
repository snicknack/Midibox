#!/usr/bin/env python3
import spidev, RPi.GPIO as GPIO, time

BUS, DEV = 0, 0
SPI_SPEED_HZ = 250_000
FRAME_BYTES  = 32
CS_GPIO      = 7          # choose any free GPIO; BCM numbering (e.g., 7)

GPIO.setmode(GPIO.BCM)
GPIO.setup(CS_GPIO, GPIO.OUT, initial=GPIO.HIGH)

spi = spidev.SpiDev()
spi.open(BUS, DEV)
spi.mode = 1
spi.max_speed_hz = SPI_SPEED_HZ
spi.bits_per_word = 8

def read_frame(nbytes=FRAME_BYTES):
    GPIO.output(CS_GPIO, GPIO.LOW)
    rx = spi.xfer2([0x00]*nbytes)
    GPIO.output(CS_GPIO, GPIO.HIGH)
    return rx

print("Reading frames with manual CS… Ctrl+C to stop.")
prev = None
try:
    while True:
        rx = read_frame()
        if rx != prev:
            print(" ".join(f"{b:02X}" for b in rx))
            prev = rx
        time.sleep(0.01)
except KeyboardInterrupt:
    pass
finally:
    spi.close()
    GPIO.cleanup()
