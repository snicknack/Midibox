# NeoPixel ring driver for SuperCore
# - PWM backend on GPIO13 (run with sudo)
# - Call ring.update_by_delta(+1/-1) from your encoder tick
# - Or ring.set_value(0..127) if you have an absolute value

import time
import board
import neopixel

class RingMeter:
    def __init__(self,
                 pin=board.D13,          # GPIO13 PWM
                 num_pixels=16,
                 brightness=0.35,
                 order=neopixel.GRB,
                 mode="bar",             # "bar" or "dot"
                 top_offset=0,           # rotate so pixel 0 = 12 o'clock
                 min_val=0,
                 max_val=127):
        self.n = num_pixels
        self.min = min_val
        self.max = max_val
        self.mode = mode
        self.offset = top_offset % num_pixels
        self.value = 0

        self.pixels = neopixel.NeoPixel(
            pin, num_pixels,
            brightness=brightness,
            auto_write=False,
            pixel_order=order
        )
        self.clear(show=True)

    def clear(self, show=False):
        self.pixels.fill((0,0,0))
        if show:
            self.pixels.show()

    # simple palette: low=cyan, mid=magenta, hi=yellow (nice and bright)
    def _color_for_level(self, frac):
        # frac 0..1
        if frac < 0.33:
            return (0, 255, 255)   # cyan
        elif frac < 0.66:
            return (255, 0, 255)   # magenta
        else:
            return (255, 255, 0)   # yellow

    def _idx(self, i):
        # apply top offset
        return (i + self.offset) % self.n

    def set_value(self, v):
        self.value = max(self.min, min(self.max, int(v)))
        self._render()

    def update_by_delta(self, d):
        self.set_value(self.value + d)

    def _render(self):
        # map value 0..max to 0..n
        frac = (self.value - self.min) / (self.max - self.min or 1)
        lit = max(0, min(self.n, int(round(frac * self.n))))
        col = self._color_for_level(frac)

        if self.mode == "bar":
            for i in range(self.n):
                self.pixels[self._idx(i)] = col if i < lit else (0,0,0)
        else:  # "dot"
            for i in range(self.n):
                self.pixels[self._idx(i)] = (0,0,0)
            self.pixels[self._idx(max(0, min(self.n-1, lit-1)))] = col

        self.pixels.show()

# quick standalone test
if __name__ == "__main__":
    ring = RingMeter(top_offset=0, num_pixels=16, mode="bar")
    try:
        for v in range(0, 128, 4):
            ring.set_value(v); time.sleep(0.03)
        for v in range(127, -1, -4):
            ring.set_value(v); time.sleep(0.03)
    finally:
        ring.clear(show=True)
