#!/usr/bin/env python3
from PIL import Image, ImageDraw
from midibox.drivers.tft import TFT
from midibox.drivers.touch_ft6236 import FT6236

# Adjust if your TFT class exposes width/height differently
W, H = 240, 320
tft = TFT(width=W, height=H)
touch = FT6236(bus=1, addr=0x38)

img = Image.new("RGB", (W, H), (0, 0, 0))
d = ImageDraw.Draw(img)
d.text((8, 8), "Touch Test: tap & drag", fill=(220, 220, 240))
tft.show(img)

try:
    while True:
        pts = touch.read_touches()  # list of dicts: {id,x,y,event}
        if pts:
            for p in pts:
                x, y = p["x"], p["y"]
                ImageDraw.Draw(img).ellipse((x-3, y-3, x+3, y+3), fill=(255, 255, 255))
            tft.show(img)
except KeyboardInterrupt:
    pass
