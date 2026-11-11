import time, board, digitalio
from PIL import Image, ImageDraw
import adafruit_rgb_display.ili9341 as ili9341

# ---- Pins / SPI ----
cs  = digitalio.DigitalInOut(board.CE0)   # GPIO8
dc  = digitalio.DigitalInOut(board.D24)   # GPIO24
rst = digitalio.DigitalInOut(board.D25)   # GPIO25
spi = board.SPI()

BAUD = 32000000      # try 16e6, then 12e6, 8e6 if needed
ROT  = 180           # keep your orientation

disp = ili9341.ILI9341(spi, cs=cs, dc=dc, rst=rst, baudrate=BAUD, rotation=ROT)

W, H = disp.width, disp.height

def show_solid(rgb, hold=0.6):
    img = Image.new("RGB", (W, H), rgb)
    disp.image(img)
    time.sleep(hold)

def show_stripes(width=4, hold=1.0):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for x in range(0, W, width):
        c = (40,40,40) if (x//width)%2==0 else (200,200,200)
        d.rectangle((x, 0, min(x+width-1, W-1), H-1), fill=c)
    disp.image(img)
    time.sleep(hold)

def show_moving_bar(hold=2.0):
    img = Image.new("RGB", (W, H), (20,20,20))
    d = ImageDraw.Draw(img)
    t0 = time.time()
    while time.time() - t0 < hold:
        for x in range(0, W):
            d.rectangle((0,0,W-1,H-1), fill=(20,20,20))
            d.rectangle((x,0,min(x+2,W-1),H-1), fill=(255,255,0))
            disp.image(img)

# --- Test sequence ---
# solids
for c in [(0,0,0),(48,48,48),(200,200,200),(255,0,0),(0,255,0),(0,0,255)]:
    show_solid(c)

# patterns
show_stripes(width=2)
show_stripes(width=1)   # single-pixel stripes expose stuck columns
show_moving_bar()
