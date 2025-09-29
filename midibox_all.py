#!/usr/bin/env python3
import time, board, digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.ili9341 as ili9341
import mido

# ---------------- FT6236 minimal (I2C 0x38) ----------------
try:
    from smbus import SMBus
except ImportError:
    from smbus2 import SMBus  # fallback if smbus not available

I2C_BUS = 1
FT_ADDR = 0x38
REG_TD_STATUS = 0x02

def ft_read_touches(bus):
    """Return list of touches: [{'id':int,'x':int,'y':int,'event':int}] (up to 2)"""
    d1 = bus.read_i2c_block_data(FT_ADDR, REG_TD_STATUS, 7)
    n = d1[0] & 0x0F
    out = []
    if n >= 1:
        xh, xl, yh, yl = d1[1], d1[2], d1[3], d1[4]
        event = (xh >> 6) & 0x03  # 0:down 1:up 2:contact
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

# ---------------- Display setup (ILI9341 over SPI) ----------------
spi = board.SPI()  # SCK=GPIO11, MOSI=GPIO10, MISO=GPIO9 (MISO not required for display)
cs  = digitalio.DigitalInOut(board.CE0)   # GPIO8  (LCD_CS)
dc  = digitalio.DigitalInOut(board.D24)   # GPIO24 (LCD_RS/DC)
rst = digitalio.DigitalInOut(board.D25)   # GPIO25 (LCD_RST)

# rotation=180 because your panel is mounted upside down
disp = ili9341.ILI9341(spi, cs=cs, dc=dc, rst=rst, baudrate=32000000, rotation=180)
W, H = disp.width, disp.height

# ---------------- Touch calibration ----------------
# With rotation=180, these flips usually align touch to screen:
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

# ---------------- MIDI routing ----------------
class MidiRouter:
    def __init__(self):
        self.port_name = None  # real ALSA port name, or None for virtual
        self.out = None
        self.ensure_port()

    def ensure_port(self):
        try:
            if self.port_name:
                if self.out: self.out.close()
                self.out = mido.open_output(self.port_name)
                return
        except Exception as e:
            print("Failed to open MIDI port:", self.port_name, e)
        # Fallback to virtual port
        if self.out: self.out.close()
        self.out = mido.open_output("Touch GUI", virtual=True)
        self.port_name = None

    def list_ports(self):
        return mido.get_output_names()

    def set_port(self, name):
        self.port_name = name
        self.ensure_port()

    def note_on(self, note, vel=110, ch=0):
        self.out.send(mido.Message('note_on', note=note, velocity=vel, channel=ch))
    def note_off(self, note, ch=0):
        self.out.send(mido.Message('note_off', note=note, velocity=0, channel=ch))
    def cc(self, cc, val, ch=0):
        self.out.send(mido.Message('control_change', control=cc, value=val, channel=ch))
    def pitchbend(self, value, ch=0):
        # value 0..16383, center=8192; mido pitch is -8192..+8191
        self.out.send(mido.Message('pitchwheel', pitch=int(value)-8192, channel=ch))

MIDI = MidiRouter()
MIDI_CHANNEL = 1   # 1..16
TRANSPOSE    = 0   # -36..+36

# ---------------- UI helpers ----------------
font = ImageFont.load_default()
STATUS_H = 28

def safe_round_rect(d, rect, r, fill=None, outline=None, width=1):
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
    if on:
        d.ellipse((x-5,y-5,x+5,y+5), fill=(0,255,120))
    else:
        d.ellipse((x-5,y-5,x+5,y+5), outline=(110,110,110))

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
        # (rect, note, label)
        self.pads = [
            ((gap, STATUS_H+gap, halfW-gap, STATUS_H+halfH-gap), 60, "C"),
            ((halfW+gap, STATUS_H+gap, W-gap, STATUS_H+halfH-gap), 62, "D"),
            ((gap, STATUS_H+halfH+gap, halfW-gap, H-gap), 64, "E"),
            ((halfW+gap, STATUS_H+halfH+gap, W-gap, H-gap), 67, "G"),
        ]
        self.active_by_tid = {}  # tid -> pad index
        self.flash_until = 0

    def draw(self, d):
        d.rectangle((0,0,W-1,STATUS_H-1), fill=(0,60,100))
        d.text((8, 8), f"Pads  CH {MIDI_CHANNEL:02d}  TR {TRANSPOSE:+d}", font=font, fill=(255,255,255))
        draw_led(d, W-12, 12, on=(time.time()<self.flash_until))
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
        note = self.pads[idx][1] + TRANSPOSE
        MIDI.note_on(note, ch=MIDI_CHANNEL-1)
        self.flash_until = time.time()+0.12
        return True

    def touch_move(self, x,y, tid):
        if tid not in self.active_by_tid: return False
        cur = self.active_by_tid[tid]
        now_idx = self._pad_at(x,y)
        if now_idx is None or now_idx == cur: return False
        # switch notes
        MIDI.note_off(self.pads[cur][1] + TRANSPOSE, ch=MIDI_CHANNEL-1)
        self.active_by_tid[tid] = now_idx
        MIDI.note_on(self.pads[now_idx][1] + TRANSPOSE, ch=MIDI_CHANNEL-1)
        self.flash_until = time.time()+0.12
        return True

    def touch_up(self, x,y, tid):
        if tid not in self.active_by_tid: return False
        idx = self.active_by_tid.pop(tid)
        MIDI.note_off(self.pads[idx][1] + TRANSPOSE, ch=MIDI_CHANNEL-1)
        return True

# ---- Sliders page (two CCs) ----
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

    def _y_to_7(self, rect, y):
        x0,y0,x1,y1 = rect
        yl, yh = y0+8, y1-8
        y = max(yl, min(yh, y))
        return int(round(127 * (yh - y) / (yh - yl)))

    def draw_slider(self, d, rect, val, label, active=False):
        x0,y0,x1,y1 = rect
        safe_round_rect(d, (x0,y0,x1,y1), 12, fill=(40,42,50), outline=(200,200,200))
        yl, yh = y0+8, y1-8
        ythumb = int(yh - (val/127.0)*(yh-yl))
        safe_round_rect(d, (x0+6, ythumb-10, x1-6, ythumb+10), 10,
                        fill=(80,180,255) if active else (96,98,110),
                        outline=(255,255,255) if active else (210,210,210), width=2)
        txt = f"{label} {val:3d}"
        tw = d.textlength(txt, font=font)
        d.text(((x0+x1)//2 - tw//2, y0-18), txt, font=font, fill=(240,240,240))

    def draw(self, d):
        d.rectangle((0,0,W-1,STATUS_H-1), fill=(0,60,100))
        d.text((8,8), f"Sliders  CH {MIDI_CHANNEL:02d}", font=font, fill=(255,255,255))
        for s in self.sliders:
            active = (s["tid"] is not None)
            self.draw_slider(d, s["rect"], s["val"], s["label"], active)

    def touch_down(self, x,y, tid):
        for i,s in enumerate(self.sliders):
            if point_in(s["rect"], x,y):
                s["tid"] = tid
                s["val"] = self._y_to_7(s["rect"], y)
                if s["val"] != s["last_sent"]:
                    MIDI.cc(s["cc"], s["val"], ch=MIDI_CHANNEL-1)
                    s["last_sent"] = s["val"]
                return True
        return False

    def touch_move(self, x,y, tid):
        for s in self.sliders:
            if s["tid"] == tid:
                newv = self._y_to_7(s["rect"], y)
                if newv != s["val"]:
                    s["val"] = newv
                    if newv != s["last_sent"]:
                        MIDI.cc(s["cc"], newv, ch=MIDI_CHANNEL-1)
                        s["last_sent"] = newv
                return True
        return False

    def touch_up(self, x,y, tid):
        for s in self.sliders:
            if s["tid"] == tid:
                s["tid"] = None
                return True
        return False

# ---- Performance page (Pitch Bend 14-bit + Mod) ----
class PerformancePage(PageBase):
    name = "Perf"
    def __init__(self):
        self.pb_val = 8192   # 0..16383
        self.mod_val = 0     # 0..127
        self.pb_rect  = None
        self.mod_rect = None
        self._layout()

    def _layout(self):
        gap = 14
        track_w = (W - gap*3) // 2
        self.pb_rect  = (gap,          STATUS_H + gap, gap+track_w, H - gap)
        self.mod_rect = (gap*2+track_w,STATUS_H + gap, W - gap,     H - gap)

    def _y_to_14(self, rect, y):
        x0,y0,x1,y1 = rect; yl, yh = y0+8, y1-8
        y = max(yl, min(yh, y))
        return int(round(16383 * (yh - y) / (yh - yl)))

    def _y_to_7(self, rect, y):
        x0,y0,x1,y1 = rect; yl, yh = y0+8, y1-8
        y = max(yl, min(yh, y))
        return int(round(127 * (yh - y) / (yh - yl)))

    def _draw_slider14(self, d, rect, val14, label, active=False):
        x0,y0,x1,y1 = rect
        safe_round_rect(d, (x0,y0,x1,y1), 12, fill=(40,42,50), outline=(200,200,200))
        yl, yh = y0+8, y1-8
        ythumb = int(yh - (val14/16383.0)*(yh-yl))
        safe_round_rect(d, (x0+6, ythumb-12, x1-6, ythumb+12), 10,
                        fill=(80,180,255) if active else (96,98,110),
                        outline=(255,255,255) if active else (210,210,210), width=2)
        cy = int((yl+yh)//2)
        d.line((x0+8, cy, x1-8, cy), fill=(140,140,140))
        txt = f"{label} {val14:5d}"
        tw = d.textlength(txt, font=font)
        d.text(((x0+x1)//2 - tw//2, y0-18), txt, font=font, fill=(240,240,240))

    def _draw_slider7(self, d, rect, val7, label, active=False):
        x0,y0,x1,y1 = rect
        safe_round_rect(d, (x0,y0,x1,y1), 12, fill=(40,42,50), outline=(200,200,200))
        yl, yh = y0+8, y1-8
        ythumb = int(yh - (val7/127.0)*(yh-yl))
        safe_round_rect(d, (x0+6, ythumb-10, x1-6, ythumb+10), 10,
                        fill=(80,255,140) if active else (96,110,98),
                        outline=(255,255,255) if active else (210,210,210), width=2)
        txt = f"{label} {val7:3d}"
        tw = d.textlength(txt, font=font)
        d.text(((x0+x1)//2 - tw//2, y0-18), txt, font=font, fill=(240,240,240))

    def draw(self, d):
        d.rectangle((0,0,W-1,STATUS_H-1), fill=(0,60,100))
        d.text((8,8), f"Perf  CH {MIDI_CHANNEL:02d}  TR {TRANSPOSE:+d}", font=font, fill=(255,255,255))
        self._draw_slider14(d, self.pb_rect,  self.pb_val,  "Pitch", active=False)
        self._draw_slider7 (d, self.mod_rect, self.mod_val, "Mod",   active=False)

    def touch_down(self, x,y, tid):
        if point_in(self.pb_rect, x,y):
            self.pb_val = self._y_to_14(self.pb_rect, y)
            MIDI.pitchbend(self.pb_val, ch=MIDI_CHANNEL-1)
            return True
        if point_in(self.mod_rect, x,y):
            self.mod_val = self._y_to_7(self.mod_rect, y)
            MIDI.cc(1, self.mod_val, ch=MIDI_CHANNEL-1)
            return True
        return False

    def touch_move(self, x,y, tid):
        return self.touch_down(x,y,tid)

    def touch_up(self, x,y, tid):
        return False

# ---- Settings page (channel/transpose/output selection) ----
class SettingsPage(PageBase):
    name = "Settings"
    def __init__(self):
        self.items = []    # list of (rect, text, action)
        self._layout()

    def _layout(self):
        self.items.clear()
        btn_h = 36; gap=6
        # Channel / Transpose
        rows = [
            ("CH -", lambda: self._ch(-1)),
            ("CH +", lambda: self._ch(+1)),
            ("TR -", lambda: self._tr(-1)),
            ("TR +", lambda: self._tr(+1)),
            ("Reload Ports", self._reload_ports),
        ]
        x = 6; y = STATUS_H + 6
        for label, act in rows:
            rect = (x, y, x+120, y+btn_h)
            self.items.append((rect, label, act))
            y += btn_h + gap

        # Output ports
        y += 6
        for p in MIDI.list_ports():
            rect = (6, y, W-6, y+btn_h)
            self.items.append((rect, f"Port: {p}", lambda name=p: MIDI.set_port(name)))
            y += btn_h + 4

        # Footer: current selection
        rect = (6, H- btn_h - 6, W-6, H-6)
        cur = MIDI.port_name or "Virtual (Touch GUI)"
        self.items.append((rect, f"Selected: {cur}", lambda: None))

    def _ch(self, delta):
        global MIDI_CHANNEL
        new = MIDI_CHANNEL + delta
        if new < 1: new = 16
        if new > 16: new = 1
        MIDI_CHANNEL = new

    def _tr(self, delta):
        global TRANSPOSE
        TRANSPOSE = max(-36, min(36, TRANSPOSE + delta))

    def _reload_ports(self):
        self._layout()

    def draw(self, d):
        d.rectangle((0,0,W-1,STATUS_H-1), fill=(0,60,100))
        d.text((8,8), f"Settings  CH {MIDI_CHANNEL:02d}  TR {TRANSPOSE:+d}", font=font, fill=(255,255,255))
        for rect, label, _ in self.items:
            draw_button(d, rect, label, pressed=False)

    def _hit(self, x,y):
        for rect, label, action in self.items:
            if point_in(rect, x,y): return action
        return None

    def touch_down(self, x,y, tid):
        act = self._hit(x,y)
        if act:
            act()
            # If ports changed, rebuild items to reflect new selection
            if act == self._reload_ports:
                self._layout()
            return True
        return False

    def touch_move(self, x,y, tid): return False
    def touch_up(self, x,y, tid):   return False

# ---------------- App: pages + event loop ----------------
class App:
    def __init__(self):
        self.pages = [PadsPage(), SlidersPage(), PerformancePage(), SettingsPage()]
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
