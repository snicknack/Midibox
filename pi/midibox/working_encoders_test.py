# encoders_test.py - uses the new polling driver + ADS1115 (optional)
import sys, os, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from midio.encoders_sx1509_poll2 import SX1509Encoders
import time, board, busio
import adafruit_drv2605 as drv

# --- SuperCore NeoPixel ring helper ---
import time, board, neopixel

class RingMeter:
    def __init__(self, pin=board.D13, num_pixels=12, brightness=0.35,
                 mode="bar", top_offset=0, vmin=0, vmax=200, color=(0,255, 255)):
        self.n = num_pixels
        self.mode = mode          # "bar" or "dot"
        self.off = top_offset % num_pixels
        self.vmin, self.vmax = vmin, vmax
        self.value = vmin
        self.color = color
        self.pixels = neopixel.NeoPixel(
            pin, num_pixels, brightness=brightness,
            auto_write=False, pixel_order=neopixel.GRBW, bpp=4
        )
        self.clear(True)

    def clear(self, show=False):
        self.pixels.fill((0,0,0,0))
        if show: self.pixels.show()

    def _idx(self, i): return (i + self.off) % self.n

    def _color(self, frac):
        # simple cyan→magenta→yellow palette
        #if frac < 0.33:  return (0,255,255)
        #if frac < 0.66:  return (255,0,255)
        print("Color, function called!")
        return (255,255,0, 0)

    def set_value(self, v):
        # clamp + render
        v = max(self.vmin, min(self.vmax, int(v)))
        self.value = v
        frac = (v - self.vmin) / max(1, (self.vmax - self.vmin))
        lit = max(0, min(self.n, int(round(frac * self.n))))
        col_fixed = (self.color)
        print("Ringmeter.set_value:", v, "FIXED", (255, 0, 0, 0))
        self.pixels.fill((0, 0, 0, 0))
        if self.mode == "bar":
            for i in range(self.n):
                self.pixels[self._idx(i)] = col_fixed if i < lit else (0,0,0,0)
        else:  # "dot"
            self.pixels.fill((0,0,0,0))
            if lit: self.pixels[self._idx(lit-1)] = col_fixed
        self.pixels.show()

# --- Haptics (DRV2605L) ---
i2c = busio.I2C(board.SCL, board.SDA)
hfx = drv.DRV2605(i2c, address=0x5A)
hfx.use_ERM()      # ERM for your current motor (switch to use_LRM() when LRA arrives)
hfx.library = 1    # ERM library set

# simple helpers + light rate limiting so we don't spam the driver
_last_tick = 0.0
def haptic_tick(min_interval=0.012):
    global _last_tick
    now = time.monotonic()
    if now - _last_tick < min_interval:
        return
    _last_tick = now
    hfx.sequence[0] = drv.Effect(1)   # Sharp Click 100% (nice for detents)
    for i in range(1,8): hfx.sequence[i] = drv.Pause(0)
    hfx.play()

def haptic_confirm():
    hfx.sequence[0] = drv.Effect(15)  # Double Strong Click (confirm/select)
    for i in range(1,8): hfx.sequence[i] = drv.Pause(0)
    hfx.play()

def haptic_endstop():
    # stronger pattern for min/max (click + short pause + click)
    hfx.sequence[0] = drv.Effect(11)  # Strong Click 100%
    hfx.sequence[1] = drv.Pause(10)
    hfx.sequence[2] = drv.Effect(11)
    for i in range(3,8): hfx.sequence[i] = drv.Pause(0)
    hfx.play()

# NeoPixel ring instance (edit these to taste)
ring = RingMeter(
    pin=board.D13,
    num_pixels=12,    # set to 12/16/24 to match your ring
    mode="bar",       # "bar" or "dot"
    top_offset=7,     # rotate so pixel 0 = top
    vmin=20, vmax=201,  # match uic_t1Arc5Tempo range
    brightness=0.05,
    color=(0, 160, 255, 0)
)

# If you want ADS values alongside, uncomment the next two lines:
# from midio.ads1115_mod import ADS1115Reader
# ads = ADS1115Reader(addr=0x48, rate_hz=100, channels=(0,1,2,3))

ENCODER_TO_WIDGET = {0:"uic_t1Arc1",1:"uic_t1Arc2",2:"uic_t1Arc3",3:"uic_t1Arc4",4:"uic_t1Arc5Tempo"}
params = {"uic_t1Arc1":64,"uic_t1Arc2":64,"uic_t1Arc3":64,"uic_t1Arc4":64,"uic_t1Arc5Tempo":120}

def apply_delta(w, d):
    if w == "uic_t1Arc5Tempo":
        params[w] = max(20, min(200, params[w] + d))
        # when you parse/get the updated value into tempo_val:
        ring.set_value(params[w])
        haptic_tick()                         # <- fire a small click each step
        if params[w] in (0, 201):
            haptic_endstop()                  # <- stronger bump at limits
    else:
        params[w] = max(0, min(127, params[w] + d))
    print(f"[GUI] {w} -> {params[w]}")

def main():
    enc = SX1509Encoders(addr=0x3E, pairs=[(0,1),(3,4),(6,7),(9,10),(12,13)], poll_hz=500).begin()
    # ads.begin()  # if using ADS
    
    print("Rotate encoders… Ctrl+C to exit.")
    try:
        while True:
            for idx, delta, _ in enc.read_and_zero():
                w = ENCODER_TO_WIDGET.get(idx)
                if w:
                    apply_delta(w, delta)
                else:
                    print(f"[ENC] {idx}: Δ{delta}")
            # print("ADS:", ads.values_cc)  # if using ADS
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        enc.close()
        # ads.close()
        print("Done.")

if __name__ == "__main__":
    main()
