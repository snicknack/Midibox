from PIL import Image, ImageDraw, ImageFont, Image
from .widgets import draw_button, draw_led, safe_round_rect, point_in
from midi.router import MIDI, MIDI_CHANNEL, TRANSPOSE

font = ImageFont.load_default()

class PageBase:
    name = "Page"
    def __init__(self, W, H, STATUS_H):
        self.W, self.H, self.STATUS_H = W, H, STATUS_H

    def base_header(self, d, title: str):
        d.rectangle((0,0,self.W-1,self.STATUS_H-1), fill=(0,60,100))
        d.text((8,8), title, font=font, fill=(255,255,255))

    def render_frame(self, page_label, page_btn_rect):
        img = Image.new("RGB", (self.W, self.H), (28,28,32))
        d = ImageDraw.Draw(img)
        self.draw(d)
        draw_button(d, page_btn_rect, page_label, pressed=False)
        return img

    # virtuals
    def draw(self, d): ...
    def touch_down(self, x,y, tid): ...
    def touch_move(self, x,y, tid): ...
    def touch_up(self,   x,y, tid): ...

# ---------------- Pads ----------------
class PadsPage(PageBase):
    name = "Pads"
    def __init__(self, W, H, STATUS_H):
        super().__init__(W,H,STATUS_H)
        gap = 6; halfW = W//2; halfH = (H-STATUS_H)//2
        self.pads = [
            ((gap, STATUS_H+gap, halfW-gap, STATUS_H+halfH-gap), 60, "C"),
            ((halfW+gap, STATUS_H+gap, W-gap, STATUS_H+halfH-gap), 62, "D"),
            ((gap, STATUS_H+halfH+gap, halfW-gap, H-gap), 64, "E"),
            ((halfW+gap, STATUS_H+halfH+gap, W-gap, H-gap), 67, "G"),
        ]
        self.active_by_tid = {}
        self.flash_until = 0

    def draw(self, d):
        self.base_header(d, f"Pads  CH {MIDI_CHANNEL:02d}  TR {TRANSPOSE:+d}")
        import time
        draw_led(d, self.W-12, 12, on=(time.time()<self.flash_until))
        for i,(rect,note,label) in enumerate(self.pads):
            pressed = (i in self.active_by_tid.values())
            draw_button(d, rect, label, pressed)

    def _pad_at(self, x,y):
        for i,(rect,_,_) in enumerate(self.pads):
            if point_in(rect, x, y): return i
        return None

    def touch_down(self, x,y, tid):
        idx = self._pad_at(x,y)
        if idx is None: return False
        self.active_by_tid[tid] = idx
        note = self.pads[idx][1] + TRANSPOSE
        MIDI.note_on(note, ch=MIDI_CHANNEL-1)
        import time; self.flash_until = time.time()+0.12
        return True

    def touch_move(self, x,y, tid):
        if tid not in self.active_by_tid: return False
        cur = self.active_by_tid[tid]
        now = self._pad_at(x,y)
        if now is None or now == cur: return False
        MIDI.note_off(self.pads[cur][1] + TRANSPOSE, ch=MIDI_CHANNEL-1)
        self.active_by_tid[tid] = now
        MIDI.note_on(self.pads[now][1] + TRANSPOSE, ch=MIDI_CHANNEL-1)
        import time; self.flash_until = time.time()+0.12
        return True

    def touch_up(self, x,y, tid):
        if tid not in self.active_by_tid: return False
        idx = self.active_by_tid.pop(tid)
        MIDI.note_off(self.pads[idx][1] + TRANSPOSE, ch=MIDI_CHANNEL-1)
        return True

# ---------------- Sliders (CC) ----------------
class SlidersPage(PageBase):
    name = "Sliders"
    def __init__(self, W, H, STATUS_H):
        super().__init__(W,H,STATUS_H)
        self.sliders = [
            {"rect": None, "cc":1,  "label":"Mod", "val":64, "tid":None, "last_sent":-1},
            {"rect": None, "cc":74, "label":"Brt", "val":64, "tid":None, "last_sent":-1},
        ]
        self._layout()

    def _layout(self):
        gap = 14; track_w = (self.W - gap*3)//2; x0 = gap
        for s in self.sliders:
            s["rect"] = (x0, self.STATUS_H+gap, x0+track_w, self.H-gap)
            x0 += track_w + gap

    def _y_to_7(self, rect, y):
        x0,y0,x1,y1 = rect; yl, yh = y0+8, y1-8
        y = max(yl, min(yh, y))
        return int(round(127 * (yh - y) / (yh - yl)))

    def _draw_slider(self, d, rect, val, label, active=False):
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
        self.base_header(d, f"Sliders  CH {MIDI_CHANNEL:02d}")
        for s in self.sliders:
            self._draw_slider(d, s["rect"], s["val"], s["label"], active=(s["tid"] is not None))

    def touch_down(self, x,y, tid):
        for s in self.sliders:
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

# ---------------- Performance (Pitch/Mod) ----------------
class PerformancePage(PageBase):
    name = "Perf"
    def __init__(self, W, H, STATUS_H):
        super().__init__(W,H,STATUS_H)
        self.pb_val = 8192
        self.mod_val = 0
        self._layout()

    def _layout(self):
        gap = 14; track_w = (self.W - gap*3)//2
        self.pb_rect  = (gap, self.STATUS_H+gap, gap+track_w, self.H-gap)
        self.mod_rect = (gap*2+track_w, self.STATUS_H+gap, self.W-gap, self.H-gap)

    def _y_to_14(self, rect, y):
        x0,y0,x1,y1 = rect; yl, yh = y0+8, y1-8
        y = max(yl, min(yh, y))
        return int(round(16383 * (yh - y) / (yh - yl)))

    def _y_to_7(self, rect, y):
        x0,y0,x1,y1 = rect; yl, yh = y0+8, y1-8
        y = max(yl, min(yh, y))
        return int(round(127 * (yh - y) / (yh - yl)))

    def draw(self, d):
        self.base_header(d, f"Perf  CH {MIDI_CHANNEL:02d}  TR {TRANSPOSE:+d}")
        # Pitchbend slider
        x0,y0,x1,y1 = self.pb_rect
        safe_round_rect(d, (x0,y0,x1,y1), 12, fill=(40,42,50), outline=(200,200,200))
        yl, yh = y0+8, y1-8
        ythumb = int(yh - (self.pb_val/16383.0)*(yh-yl))
        safe_round_rect(d, (x0+6, ythumb-12, x1-6, ythumb+12), 10,
                        fill=(80,180,255), outline=(255,255,255), width=2)
        cy = int((yl+yh)//2)
        d.line((x0+8, cy, x1-8, cy), fill=(140,140,140))
        txt = f"Pitch {self.pb_val:5d}"
        tw = d.textlength(txt, font=font)
        d.text(((x0+x1)//2 - tw//2, y0-18), txt, font=font, fill=(240,240,240))

        # Mod slider
        x0,y0,x1,y1 = self.mod_rect
        safe_round_rect(d, (x0,y0,x1,y1), 12, fill=(40,42,50), outline=(200,200,200))
        yl, yh = y0+8, y1-8
        ythumb = int(yh - (self.mod_val/127.0)*(yh-yl))
        safe_round_rect(d, (x0+6, ythumb-10, x1-6, ythumb+10), 10,
                        fill=(80,255,140), outline=(255,255,255), width=2)
        txt = f"Mod {self.mod_val:3d}"
        tw = d.textlength(txt, font=font)
        d.text(((x0+x1)//2 - tw//2, y0-18), txt, font=font, fill=(240,240,240))

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

# ---------------- Settings ----------------
class SettingsPage(PageBase):
    name = "Settings"
    def __init__(self, W, H, STATUS_H, app):
        super().__init__(W,H,STATUS_H)
        self.app = app
        self.items = []
        self._layout()

    def _layout(self):
        self.items.clear()
        btn_h, gap = 36, 6
        x, y = 6, self.STATUS_H + 6
        rows = [
            ("CH -", lambda: self._ch(-1)),
            ("CH +", lambda: self._ch(+1)),
            ("TR -", lambda: self._tr(-1)),
            ("TR +", lambda: self._tr(+1)),
            ("Reload Ports", self._reload_ports),
            ("Select Port ...", self._goto_ports),
        ]
        for label, act in rows:
            rect = (x, y, x+160, y+btn_h)
            self.items.append((rect, label, act))
            y += btn_h + gap

        # footer
        cur = MIDI.port_name or "Virtual (Touch GUI)"
        rect = (6, self.H - btn_h - 6, self.W - 6, self.H - 6)
        self.items.append((rect, f"Selected: {cur}", lambda: None))

    def _ch(self, d):
        global MIDI_CHANNEL
        new = MIDI_CHANNEL + d
        if new < 1: new = 16
        if new > 16: new = 1
        MIDI_CHANNEL = new

    def _tr(self, d):
        global TRANSPOSE
        TRANSPOSE = max(-36, min(36, TRANSPOSE + d))

    def _reload_ports(self):
        MIDI.ensure_port()
        self._layout()

    def _goto_ports(self):
        self.app.switch_to("Ports")

    def draw(self, d):
        self.base_header(d, f"Settings  CH {MIDI_CHANNEL:02d}  TR {TRANSPOSE:+d}")
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
            self._layout()
            return True
        return False

    def touch_move(self, x,y, tid): return False
    def touch_up(self, x,y, tid):   return False

# ---------------- Ports ----------------
class PortsPage(PageBase):
    name = "Ports"
    PAGE_SIZE = 6

    def __init__(self, W, H, STATUS_H, app):
        super().__init__(W,H,STATUS_H)
        self.app = app
        self.ports = MIDI.list_ports()
        self.page = 0
        self.rows = []
        self._layout()

    def _layout(self):
        self.rows.clear()
        btn_h, gap = 36, 6
        y = self.STATUS_H + 6
        start = self.page * self.PAGE_SIZE
        view = self.ports[start:start + self.PAGE_SIZE]
        for p in view:
            rect = (6, y, self.W-6, y+btn_h)
            self.rows.append((rect, p, lambda name=p: self._select(name)))
            y += btn_h + gap
        nav_y = self.H - btn_h - 6
        prev_rect = (6, nav_y, 6 + 100, nav_y + btn_h)
        next_rect = (self.W - 106, nav_y, self.W - 6, nav_y + btn_h)
        self.rows.append((prev_rect, "Prev", self._prev))
        self.rows.append((next_rect, "Next", self._next))

    def _select(self, name):
        MIDI.set_port(name)
        self.app.switch_to("Settings")

    def _prev(self):
        if self.page > 0:
            self.page -= 1
            self._layout()

    def _next(self):
        max_page = max(0, (len(self.ports)-1)//self.PAGE_SIZE)
        if self.page < max_page:
            self.page += 1
            self._layout()

    def draw(self, d):
        self.base_header(d, "Select Output Port")
        cur = MIDI.port_name or "Virtual (Touch GUI)"
        # draw rows
        for rect, label, _ in self.rows:
            draw_button(d, rect, label, pressed=False)

    def _hit(self, x,y):
        for rect, label, action in self.rows:
            if point_in(rect, x,y): return action
        return None

    def touch_down(self, x,y, tid):
        act = self._hit(x,y)
        if act:
            act()
            self._layout()
            return True
        return False

    def touch_move(self, x,y, tid): return False
    def touch_up(self, x,y, tid):   return False
