#!/usr/bin/env python3
import time
from drivers.tft import Display
from drivers.touch_ft6236 import Touch
from midi.router import MIDI, MIDI_CHANNEL, TRANSPOSE
from ui.pages import PadsPage, SlidersPage, PerformancePage, SettingsPage, PortsPage
from gestures import SwipeDetector
# --- I/O modules ---
from midibox.io.encoders_sx1509 import SX1509Encoders   # :contentReference[oaicite:0]{index=0}
from midibox.io.ads1115_reader import ADS1115Reader     # :contentReference[oaicite:1]{index=1}


STATUS_H = 28  # keep in sync with widgets/text heights

class App:
    def __init__(self):
        # hardware
        self.disp = Display(rotation=180, baud=32_000_000)
        self.touch = Touch(rotation_180=True)  # invert both axes for your mount
        self.W, self.H = self.disp.size()

        # pages
        self.pages = {
            "Pads": PadsPage(self.W, self.H, STATUS_H),
            "Sliders": SlidersPage(self.W, self.H, STATUS_H),
            "Perf": PerformancePage(self.W, self.H, STATUS_H),
            "Settings": SettingsPage(self.W, self.H, STATUS_H, self),
            "Ports": PortsPage(self.W, self.H, STATUS_H, self),
        }
        self.order = ["Pads", "Sliders", "Perf", "Settings", "Ports"]
        self.pi = 0
        self.active = self.pages[self.order[self.pi]]

        # UI rect for page button (top-right)
        self.page_btn = (self.W-54, 2, self.W-2, STATUS_H-2)

        # input state
        self.prev = {}           # tid -> (x,y)
        self.swipe = SwipeDetector(min_dist=50, max_time=0.6)

    def draw(self):
        img = self.active.render_frame(self.order[self.pi], self.page_btn)
        self.disp.show(img)

    def switch_page(self):
        self.pi = (self.pi + 1) % len(self.order)
        self.active = self.pages[self.order[self.pi]]
        self.draw()

    def switch_to(self, name: str):
        if name in self.pages:
            self.pi = self.order.index(name)
            self.active = self.pages[name]
            self.draw()

    def run(self):
        self.draw()
        try:
            while True:
                touches = self.touch.read_touches()  # list of dicts with id,x,y,event
                current_ids = set()
                if touches:
                    for t in touches:
                        tid = t["id"]; current_ids.add(tid)
                        x, y = self.touch.map_to_screen(t["x"], t["y"], self.W, self.H)

                        if tid not in self.prev:
                            # start swipe tracking
                            self.swipe.start(tid, x, y)
                            # page button?
                            if inside(self.page_btn, x, y):
                                self.switch_page()
                            else:
                                if self.active.touch_down(x, y, tid):
                                    self.draw()
                        else:
                            px, py = self.prev[tid]
                            if (x, y) != (px, py):
                                self.swipe.move(tid, x, y)
                                if self.active.touch_move(x, y, tid):
                                    self.draw()
                        self.prev[tid] = (x, y)

                # handle releases (and detect swipe)
                for tid in list(self.prev.keys()):
                    if tid not in current_ids:
                        x, y = self.prev.pop(tid)
                        swipe = self.swipe.end(tid, x, y)
                        if swipe is not None:
                            dx, dy, dt = swipe
                            if abs(dx) > abs(dy) and dt <= self.swipe.max_time:
                                # horizontal swipe → page nav
                                self.pi = (self.pi - 1) % len(self.order) if dx > 0 else (self.pi + 1) % len(self.order)
                                self.active = self.pages[self.order[self.pi]]
                                self.draw()
                                continue
                        if self.active.touch_up(x, y, tid):
                            self.draw()

                time.sleep(0.015)
        except KeyboardInterrupt:
            pass

def inside(rect, x, y):
    x0, y0, x1, y1 = rect
    return x0 <= x < x1 and y0 <= y < y1

if __name__ == "__main__":
    App().run()
