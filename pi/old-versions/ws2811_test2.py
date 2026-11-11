# ws2811_test.py
import time, board, neopixel

pixel_pin = board.D21       # PCM pin (no conflict with audio)
num_pixels = 1

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5, auto_write=True)

try:
    while True:
        pixels[0] = (255, 0, 0); time.sleep(0.5)  # Red
        pixels[0] = (0, 255, 0); time.sleep(0.5)  # Green
        pixels[0] = (0, 0, 255); time.sleep(0.5)  # Blue
except KeyboardInterrupt:
    pixels[0] = (0, 0, 0)
