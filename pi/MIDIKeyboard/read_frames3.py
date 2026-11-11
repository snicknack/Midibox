import spidev, RPi.GPIO as GPIO, time

BUS, DEV = 0, 0
CS_GPIO = 7  # pick any spare GPIO (e.g. BCM 7 = physical pin 26)

GPIO.setmode(GPIO.BCM)
GPIO.setup(CS_GPIO, GPIO.OUT, initial=GPIO.HIGH)

spi = spidev.SpiDev()
spi.open(BUS, DEV)
spi.mode = 0
spi.max_speed_hz = 250_000

def read_frame(n=32):
    GPIO.output(CS_GPIO, GPIO.LOW)   # drive LOW
    rx = spi.xfer2([0x00]*n)
    GPIO.output(CS_GPIO, GPIO.HIGH)  # back HIGH
    return rx

while True:
    rx = read_frame()
    print(" ".join(f"{b:02X}" for b in rx))
    time.sleep(0.05)
