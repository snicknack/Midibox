import time, board, neopixel

NUM_PIXELS = 16          # set for your ring (12/ 16/24…)
BRIGHTNESS = 0.3
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    board.D13,           # <-- GPIO13 (pin 33)
    NUM_PIXELS,
    brightness=BRIGHTNESS,
    auto_write=False,
    pixel_order=ORDER
)

def clear():
    pixels.fill((0,0,0))
    pixels.show()

def color_wipe(color, wait=0.04):
    for i in range(NUM_PIXELS):
        pixels[i] = color
        pixels.show()
        time.sleep(wait)

def wheel(pos):
    if pos < 85:   return (pos*3, 255-pos*3, 0)
    if pos < 170:
        pos -= 85; return (255-pos*3, 0, pos*3)
    pos -= 170;    return (0, pos*3, 255-pos*3)

def rainbow_cycle(wait=0.02):
    for j in range(256):
        for i in range(NUM_PIXELS):
            idx = (i * 256 // NUM_PIXELS) + j
            pixels[i] = wheel(idx & 255)
        pixels.show()
        time.sleep(wait)

try:
    color_wipe((255,0,0))
    color_wipe((0,255,0))
    color_wipe((0,0,255))
    rainbow_cycle()
finally:
    clear()
