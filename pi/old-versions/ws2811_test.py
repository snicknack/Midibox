import time
import board
import neopixel

# Use GPIO18 (pin 12) for data
pixel_pin = board.D18
num_pixels = 1  # you only have 1 pixel on that breakout

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5, auto_write=True)

print("Lighting WS2811 pixel...")

try:
    while True:
        pixels[0] = (255, 0, 0)   # Red
        time.sleep(0.5)
        pixels[0] = (0, 255, 0)   # Green
        time.sleep(0.5)
        pixels[0] = (0, 0, 255)   # Blue
        time.sleep(0.5)
except KeyboardInterrupt:
    pixels[0] = (0, 0, 0)        # Off on exit
    print("Stopped")
