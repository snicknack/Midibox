#!/usr/bin/env python3
# encoders_test.py — SuperCore encoder + RGBW ring (clean)
import sys, os, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from midio.encoders_sx1509_driver import SX1509Encoders

import time
import math
import neopixel
import board

# ---- CONFIG ----
PIN = board.D13                 # we picked GPIO 13 earlier
NUM_PIXELS = 12                 # your ring is 12 LED SK6812 (RGBW)
PIXEL_ORDER = neopixel.GRBW     # proven for your ring
BPP = 4                         # RGBW
BRIGHTNESS = 0.02               # eye-friendly default
MODE = "dot"                    # "dot" or "bar"
TOP_OFFSET = 0                  # rotate if your "top" isn't at index 0

VMIN = 50                       # tempo lower bound
VMAX = 200                      # tempo upper bound

# Pick your colour (RGBW order). Examples:
#  - Cyan: (0, 160, 255, 0)
#  - Magenta: (255, 0, 255, 0)
#  - Yellow: (255, 255, 0, 0)
#  - Red: (255, 0, 0, 0)
RING_COLOR = (0, 160, 255, 0)   # "SuperCore Cyan" (RGBW)

ENCODER_NAME = "uic_t1Arc5Tempo"  # locked to your SuperCore encoder

# ---- RING DRIVER ----
class RingMeter:
    def __init__(self,
                 pin=PIN,
                 num_pixels=NUM_PIXELS,
                 brightness=BRIGHTNESS,
                 mode=MODE,
                 top_offset=TOP_OFFSET,
                 vmin=VMIN, vmax=VMAX,
                 pixel_order=PIXEL_ORDER,
                 bpp=BPP,
                 color=RING_COLOR):
        self.n = int(num_pixels)
        self.mode = mode
        self.top = int(top_offset) % self.n
        self.vmin, self.vmax = int(vmin), int(vmax)
        self.color = tuple(color)  # (R,G,B,W) for RGBW
        self.value = self.vmin

        self.pixels = neopixel.NeoPixel(
            pin,
            self.n,
            brightness=brightness,
            auto_write=False,
            pixel_order=pixel_order,
            bpp=bpp
        )
        self.clear(show=True)

    def _idx(self, i):
        return (self.top + i) % self.n

    def clear(self, show=False):
        self.pixels.fill((0, 0, 0, 0))
        if show:
            self.pixels.show()

    def set_value(self, v):
        # clamp + store
        v = max(self.vmin, min(self.vmax, int(v)))
        self.value = v

        # fraction of scale → LEDs lit
        span = max(1, (self.vmax - self.vmin))
        frac = (v - self.vmin) / span
        lit = max(0, min(self.n, int(round(frac * self.n))))

        # draw
        self.pixels.fill((0, 0, 0, 0))
        if self.mode == "bar":
            for i in range(lit):
                self.pixels[self._idx(i)] = self.color
        else:  # "dot"
            if lit:
                self.pixels[self._idx(lit - 1)] = self.color

        self.pixels.show()

# ---- ENCODER POLL LOOP ----
def main():
    # lazy import so you can run this file standalone if needed
    import encoders_sx1509_poll2 as enc  # your existing driver

    ring = RingMeter(
        pin=PIN,
        num_pixels=NUM_PIXELS,
        brightness=BRIGHTNESS,
        mode=MODE,
        top_offset=TOP_OFFSET,
        vmin=VMIN, vmax=VMAX,
        pixel_order=PIXEL_ORDER,
        bpp=BPP,
        color=RING_COLOR
    )

    print("SuperCore encoder test running…")
    print(f"- Listening for: {ENCODER_NAME}")
    print(f"- Ring: {NUM_PIXELS} x RGBW @ {PIN}, order={PIXEL_ORDER}, bpp={BPP}")
    print(f"- Range: {VMIN}..{VMAX}, mode={MODE}, color(RGBW)={RING_COLOR}")

    try:
        for name, val in enc().poll():  # expects generator yielding (name, value)
            if name == ENCODER_NAME:
                # clamp + update ring
                tempo = max(VMIN, min(VMAX, int(val)))
                ring.set_value(tempo)

                # console feedback
                print(f"[SuperCore] {name} -> {tempo}")

            # (optional) small snooze to keep CPU happy
            # time.sleep(0.001)

    except KeyboardInterrupt:
        pass
    finally:
        ring.clear(show=True)
        print("Exiting cleanly. LEDs off.")

if __name__ == "__main__":
    main()
