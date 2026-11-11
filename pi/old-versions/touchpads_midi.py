#!/usr/bin/env python3
import time, board, digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.ili9341 as ili9341
import mido

# ---------- FT6236 minimal reader (I2C addr 0x38) ----------
try:
    from smbus import SMBus          # from python3-smbus
except ImportError:
    from smbus2 import SMBus         # fallback

I2C_BUS = 1
FT_ADDR = 0x38
REG_TD_STATUS = 0x02  # number of touches
def ft_read_first_touch(bus):
    # Read 7 bytes: TD_STATUS + first touch block (0x02..0x08)
    d = bus.read_i2c_block_data(FT_ADDR, REG_TD_STATUS, 7)
    n = d[0] & 0x0F
    if n < 1:
        return None
    xh, xl, yh, yl = d[1], d[2], d[3], d[4]
    event = (xh >> 6) & 0x03  # 0:down 1:up 2:contact
    x = ((xh & 0x0F) << 8) | xl
    y = ((yh & 0x0F) << 8) | yl
    return {"x": x, "y": y, "event": event}

# ---------- Display setup ----------
spi = board.SPI()
cs  = digitalio.DigitalInOut(board.CE0)   # GPIO8  (LCD_CS)
dc  = digitalio.DigitalInOut(board.D24)   # GPIO24 (LCD_RS/DC)
rst = digitalio.DigitalInOut(board.D25)   # GPIO25 (LCD_RST)
disp = ili9341.ILI9341(spi, cs=cs, dc=dc, rst=rst,
                       baudrate=32000000, rotation=180)
W, H = disp.width, disp.height

# ---------- Touch calibration (tweak if needed) ----------
SWAP_XY   = False   # set True if axes are swapped
INVERT_X  = True   # set True to flip X
INVERT_Y  = True   # set True to flip Y
RAW_MAX_X = 239     # FT6236 raw range for this panel
RAW_MAX_Y = 319

def map_touch_to_screen(tx, ty):
    # optional axis swap
    if SWAP_XY:
        tx, ty = ty, tx
    # optional flips
    if INVERT_X:
        tx = RAW_MAX_X - tx
    if INVERT_Y:
        ty = RAW_MAX_Y - ty
    # clamp & scale to screen pixels
    tx = max(0, min(RAW_MAX_X, tx))
    ty = max(0, min(RAW_MAX_Y, ty))
    sx = int(tx * (W - 1) / RAW_MAX_X)
    sy = int(ty * (H - 1) / RAW_MAX_Y)
    return sx, sy

# ---------- MIDI ----------
out = mido.open_output("TouchPads MIDI", virtual=True)
BASE_NOTES = [60, 62, 64, 67]  # C4, D4, E4, G4 for pads TL,TR,BL,BR
VEL = 110

# ---------- UI layout ----------
font = ImageFont.load_default()
STATUS_H = 28
PAD_GAP  = 6

# pad rects (x0,y0,x1,y1): 2x2 grid below status bar
halfW = W // 2
halfH = (H - STATUS_H) // 2
pads = [
    ((PAD_GAP, STATUS_H + PAD_GAP,
      halfW - PAD_GAP, STATUS_H + halfH - PAD_GAP), "C"),              # TL
    ((halfW + PAD_GAP, STATUS_H + PAD_GAP,
      W - PAD_GAP,     STATUS_H + halfH - PAD_GAP), "D"),              # TR
    ((PAD_GAP, STATUS_H + halfH + PAD_GAP,
      halfW - PAD_GAP, H - PAD_GAP),                    "E"),          # BL
    ((halfW + PAD_GAP, STATUS_H + halfH + PAD_GAP,
      W - PAD_GAP,     H - PAD_GAP),                    "G"),          # BR
]

def point_in(r, x, y):
    x0,y0,x1,y1 = r
    return x0 <= x < x1 and y0 <= y < y1

# ---------- Draw full UI ----------
def draw_ui(active_pad_idx=None, flash_led=False):
    img = Image.new("RGB", (W, H), (28,28,32))
    d = ImageDraw.Draw(img)

    # status bar
    d.rectangle((0,0,W-1,STATUS_H-1), fill=(0,60,100))
    d.text((8, 8), "TouchPads -> MIDI", font=font, fill=(255,255,255))
    if flash_led:
        d.ellipse((W-18, 6, W-8, 16), fill=(0,255,0))
    else:
        d.ellipse((W-18, 6, W-8, 16), outline=(100,100,100))

    # pads
    for idx, (rect, label) in enumerate(pads):
        x0,y0,x1,y1 = rect
        hi = (idx == active_pad_idx)
        fill = (60,60,72) if hi else None
        d.rectangle((x0,y0,x1-1,y1-1), outline=(220,220,220), fill=fill)
        tw = d.textlength(label, font=font)
        d.text(((x0+x1)//2 - tw//2, (y0+y1)//2 - 6), label,
               font=font, fill=(240,240,240))

    disp.image(img)

# ---------- Main loop ----------
bus = SMBus(I2C_BUS)
last_active = None   # index of pad currently down
flash_until = 0.0

print("Running: tap the 4 pads to send MIDI notes. Ctrl+C to exit.")
draw_ui()

try:
    while True:
        t = ft_read_first_touch(bus)
        now = time.time()

        if t is None:
            # no touch: if a pad was held, send its note_off now
            if last_active is not None:
                note = BASE_NOTES[last_active]
                out.send(mido.Message('note_off', note=note, velocity=0))
                last_active = None
                draw_ui(flash_led=(now < flash_until))
            time.sleep(0.01)
            continue

        # map raw FT6236 coords to screen coords
        sx, sy = map_touch_to_screen(t["x"], t["y"])

        # which pad?
        active = None
        for idx, (rect, _) in enumerate(pads):
            if point_in(rect, sx, sy):
                active = idx
                break

        # handle changes
        if active is not None and active != last_active:
            # release previous pad
            if last_active is not None:
                out.send(mido.Message('note_off',
                                      note=BASE_NOTES[last_active], velocity=0))
            # press new pad
            out.send(mido.Message('note_on',
                                  note=BASE_NOTES[active], velocity=VEL))
            flash_until = now + 0.12
            last_active = active
            draw_ui(active_pad_idx=active, flash_led=True)

        # redraw LED decay occasionally
        if now >= flash_until and last_active is None:
            draw_ui()

        time.sleep(0.01)

except KeyboardInterrupt:
    pass
finally:
    if last_active is not None:
        out.send(mido.Message('note_off', note=BASE_NOTES[last_active], velocity=0))
    bus.close()
