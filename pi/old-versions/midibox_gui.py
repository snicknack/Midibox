#!/usr/bin/env python3
import time, json, os, board, digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.ili9341 as ili9341
import mido

# ---------------- FT6236 minimal (I2C 0x38) ----------------
try:
    from smbus import SMBus
except ImportError:
    from smbus2 import SMBus

I2C_BUS = 1
FT_ADDR = 0x38
REG_TD_STATUS = 0x02

def ft_read_touches(bus):
    """Return list of touches: [{'id':int,'x':int,'y':int,'event':int}]"""
    # First 7 bytes for touch1; next 6 bytes start at 0x09 for touch2
    d1 = bus.read_i2c_block_data(FT_ADDR, REG_TD_STATUS, 7)
    n = d1[0] & 0x0F
    out = []
    if n >= 1:
        xh, xl, yh, yl = d1[1], d1[2], d1[3], d1[4]
        event = (xh >> 6) & 0x03
        x = ((xh & 0x0F) << 8) | xl
        y = ((yh & 0x0F) << 8) | yl
        tid = d1[5] & 0x0F
        out.append({"id": tid, "x": x, "y": y, "event": event})
    if n >= 2:
        d2 = bus.read_i2c_block_data(FT_ADDR, 0x09, 6)
        xh, xl, yh, yl = d2[0], d2[1], d2[2], d2[3]
        event = (xh >> 6) & 0x03
        x = ((xh & 0x0F) << 8) | xl
        y = ((yh & 0x0F) << 8) | yl
        tid = d2[4] & 0x0F
        out.append({"id": tid, "x": x, "y": y, "event": event})
    return out

# ---------------- Display setup ----------------
spi = board.SPI()
cs  = digitalio.DigitalInOut(board.CE0)   # GPIO8
dc  = digitalio.DigitalInOut(board.D24)   # GPIO24
rst = digitalio.DigitalInOut(board.D25)   # GPIO25
disp = ili9341.ILI9341(spi, cs=cs, dc=dc, rst=rst, baudrate=32000000, rotation=180)
W, H = disp.width, disp.height

# ---------------- Touch calibration ----------------
# You rotated 180, so invert both axes by default:
SWAP_XY   = False
INVERT_X  = True
INVERT_Y  = True
RAW_MAX_X = 239
RAW_MAX_Y = 319

def map_touch(tx, ty):
    if SWAP_XY:
        tx, ty = ty, tx
    if INVERT_X:
        tx = RAW_MAX_X - tx
    if INVERT_Y:
        ty = RAW_MAX_Y - ty
    tx = max(0, min(RAW_MAX_X, tx))
    ty = max(0, min(RAW_MAX_Y, ty))
    sx = int(tx * (W-1) / RAW_MAX_X)
    sy = int(ty * (H-1) / RAW_MAX_Y)
    return sx, sy

# ---------------- MIDI ----------------
midi_out = mido.open_output("Touch GUI", virtual=True)
def midi_note_on(note, vel=110, ch=0): midi_out.send(mido.Message('note_on',  note=note, velocity=vel, channel=ch))
def midi_note_off(note, ch=0):         midi_out.send(mido.Message('note_off', note=note, velocity=0,   channel=ch))
def midi_cc(cc, val, ch=0):            midi_out.send(mido.Message('control_change', control=cc, value=val, channel=ch))

# ---------------- UI helpers ----------------
font = ImageFont.load_default()
STATUS_H = 28

def safe_round_rect(d, rect, r, fill=None, outline=None, width=1):
    # try rounded rectangle, fallback to normal if Pillow is too old
    try:
        d.rounded_rectangle(rect, radius=r, fill=fill, outline=outline, width=width)
    except Exception:
        d.rectangle(rect, fill=fill, outline=outline, width=width)

def draw_button(d, rect, label, pressed=False):
    x0,y0,x1,y1 = rect
    fill = (70,72,84) if pressed else (48,50,58)
    outline = (255,255,255) if pressed else (210,210,210)
    safe_round_rect(d, (x0,y0,x1-1,y1-1), 10, fill=fill, outline=outline, width=2)
    tw = d.textlength(label, font=font)
    d.text(((x0+x1)//2 - tw//2, (y0+y1)//2 - 6), label, font=font, fill=(240,240,240))

def draw_led(d, x, y, on):
    if on: d.ellipse((x-5,y-5,x+5,y+5), fill=(0,255,120))
    else:  d.ellipse((x-5,y-5,x+5,y+5), outline=(110,110,110))

def point_in(rect, x, y):
    x0,y0,x1,y1 = rect
    return x0 <= x < x1 and y0 <= y < y1

# ---------------- Page framework ----------------
class PageBase:
    name = "Page"
    def draw(self, d): ...
    def touch_down(self, x,y, tid): ...
    def touch_move(self, x,y, tid): ...
    def touch_up(self,   x,y, tid): ...

# ---- Pads page ----
class PadsPage(PageBase):
    name = "Pads"
    def __init__(self):
        gap = 6
        halfW = W//2
        halfH = (H-STATUS_H)//2
        self.pads = [
            ((gap, STATUS_H+gap, halfW-gap, STATUS_H+halfH-gap), 60, "C"),
            ((halfW+gap, STATUS_H+gap, W-gap, STATUS_H+halfH-gap), 62, "D"),
            ((gap, STATUS_H+halfH+gap, halfW-gap, H-gap), 64, "E"),
            ((halfW+gap, STATUS_H+halfH+gap, W-gap, H-gap), 67, "G"),
        ]
        self.active_by_tid = {}  # tid -> pad index
        self.flash_until = 0

    def draw(self, d):
        # status bar
        d.rectangle((0,0,W-1,STATUS_H-1), fill=(0,60,100))
        d.text((8, 8), "Pads -> MIDI", font=font, fill=(255,255,255))
        draw_led(d, W-12, 12, on=(time.time()<self.flash_until))
        # pads
        for i,(rect,note,label) in enumerate(self.pads):
            pressed = (i in self.active_by_tid.values())
            draw_button(d, rect, label, pressed)

    def _pad_at(self, x, y):
        for i,(rect,_,_) in enumerate(self.pads):
            if point_in(rect, x, y): return i
        return None

    def touch_down(self, x,y, tid):
        idx = self._pad_at(x,y)
        if idx is None: return False
        self.active_by_tid[tid] = idx
        note = self.pads[idx][1]
        midi_note_on(note)
        self.flash_until = time.time()+0.12
        return True

    def touch_move(self, x,y, tid):
        # If finger slides into a different pad, switch notes
        if tid not in self.active_by_tid: return False
        cur = self.active_by_tid[tid]
        now_idx = self._pad_at(x,y)
        if now_idx is None or now_idx == cur: return False
        # release old, press new
        midi_note_off(self.pads[cur][1])
        self.active_by_tid[tid] = now_idx
        midi_note_on(self.pads[now_idx][1])
        self.flash_until = time.time()+0.12
        return True

    def touch_up(self, x,y, tid):
        if tid not in self.active_by_tid: return False
        idx = self.active_by_tid.pop(tid)
        midi_note_off(self.pads[idx][1])
        return True

# ---- Sliders page ----
class SlidersPage(PageBase):
    name = "Sliders"
    def __init__(self):
        self.sliders = [
            {"rect": None, "cc":1,  "label":"Mod", "val":64, "tid":None, "last_sent":-1},
            {"rect": None, "cc":74, "label":"Brt", "val":64, "tid":None, "last_sent":-1},
        ]
        self._layout()

    def _layout(self):
        gap = 14
        track_w = (W - gap*3) // 2
        x0 = gap
        for s in self.sliders:
            s["rect"] = (x0, STATUS_H + gap, x0+track_w, H - gap)
            x0 += track_w + gap

    def draw_slider(self, d, rect, val, label, active=False):
        x0,y0,x1,y1 = rect
        # track
        safe_round_rect(d, (x0,y0,x1,y1), 12, fill=(40,42,50), outline=(200,200,200))
        # thumb
        # map val(0..127) to y
        yh = y1 - 8
        yl = y0 + 8
        ythumb = int(yh - (val/127.0)*(yh-yl))
        safe_round_rect(d, (x0+6, ythumb-10, x1-6, ythumb+10), 10,
                        fill=(80,180,255) if active else (96,98,110),
                        outline=(255,255,255) if active else (210,210,210), width=2)
        # label + value
        txt = f"{label} {val:3d}"
        tw = d.textlength(txt, font=font)
        d.text(( (x0+x1)//2 - tw//2, y0-18), txt, font=font, fill=(240,240,240))

    def draw(self, d):
        d.rectangle((0,0,W-1,STATUS_H-1), fill=(0,60,100))
        d.text((8,8), "Sliders -> CC", font=font, fill=(255,255,255))
        for s in self.sliders:
            active = (s["tid"] is not None)
            self.draw_slider(d, s["rect"], s["val"], s["label"], active)

    def _which(self, x,y):
        for i,s in enumerate(self.sliders):
            if point_in(s["rect"], x,y): return i
        return None

    def _y_to_val(self, rect, y):
        x0,y0,x1,y1 = rect
        yh = y1 - 8
        yl = y0 + 8
        y = max(yl, min(yh, y))
        # invert so top is 127
        return int(round(127 * (yh - y) / (yh - yl)))

    def touch_down(self, x,y, tid):
        i = self._which(x,y)
        if i is None: return False
        s = self.sliders[i]
        s["tid"] = tid
        s["val"] = self._y_to_val(s["rect"], y)
        if s["val"] != s["last_sent"]:
            midi_cc(s["cc"], s["val"])
            s["last_sent"] = s["val"]
        return True

    def touch_move(self, x,y, tid):
        for s in self.sliders:
            if s["tid"] == tid:
                newv = self._y_to_val(s["rect"], y)
                if newv != s["val"]:
                    s["val"] = newv
                    if newv != s["last_sent"]:
                        midi_cc(s["cc"], newv)
                        s["last_sent"] = newv
                return True
        return False

    def touch_up(self, x,y, tid):
        for s in self.sliders:
            if s["tid"] == tid:
                s["tid"] = None
                return True
        return False

# ---------------- App: pages + event loop ----------------
class App:
    def __init__(self):
        self.pages = [PadsPage(), SlidersPage()]
        self.pi = 0
        self.active = self.pages[self.pi]
        self.bus = SMBus(I2C_BUS)
        # small page button (top-right)
        self.page_btn = (W-42, 2, W-2, STATUS_H-2)

    def draw(self):
        img = Image.new("RGB", (W, H), (28,28,32))
        d = ImageDraw.Draw(img)
        self.active.draw(d)
        draw_button(d, self.page_btn, "PG", pressed=False)
        disp.image(img)

    def switch_page(self):
        self.pi = (self.pi + 1) % len(self.pages)
        self.active = self.pages[self.pi]

    def run(self):
        self.draw()
        prev = {}  # tid -> (x,y)
        try:
            while True:
                touches = ft_read_touches(self.bus)
                cur_ids = set()
                if touches:
                    for t in touches:
                        tid = t["id"]; cur_ids.add(tid)
                        sx, sy = map_touch(t["x"], t["y"])
                        if tid not in prev:
                            # page button?
                            if point_in(self.page_btn, sx, sy):
                                self.switch_page()
                                self.draw()
                            else:
                                changed = self.active.touch_down(sx, sy, tid)
                                if changed: self.draw()
                        else:
                            px, py = prev[tid]
                            if (sx,sy) != (px,py):
                                changed = self.active.touch_move(sx, sy, tid)
                                if changed: self.draw()
                        prev[tid] = (sx,sy)
                # handle releases
                for tid in list(prev.keys()):
                    if tid not in cur_ids:
                        sx, sy = prev.pop(tid)
                        changed = self.active.touch_up(sx, sy, tid)
                        if changed: self.draw()

                time.sleep(0.015)
        except KeyboardInterrupt:
            pass
        finally:
            self.bus.close()

if __name__ == "__main__":
    App().run()
