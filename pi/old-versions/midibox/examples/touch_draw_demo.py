#!/usr/bin/env python3
"""
Midibox touch draw demo with independent screen/touch calibration.

Screen rotation:
  ROTATION in {0, 90, 180, 270}

Touch calibration (independent of screen):
  TOUCH_ROTATION in {0, 90, 180, 270}
  TOUCH_SWAP_XY: swap axes if your controller reports them swapped
  TOUCH_INVERT_X / TOUCH_INVERT_Y: flip axes if directions are reversed

Drivers:
  from midibox.drivers.tft import Display
  from midibox.drivers.touch_ft6236 import Touch
"""

import time
from collections import deque
from PIL import Image, ImageDraw, ImageFont

from midibox.drivers.tft import Display
from midibox.drivers.touch_ft6236 import Touch

# ====== CONFIG ======
ROTATION = 0            # screen rotation you like: 0/90/180/270

# Touch calibration (start with these; adjust below based on behavior)
TOUCH_ROTATION = 0        # 0/90/180/270 applied to raw touch
TOUCH_SWAP_XY  = False    # swap axes
TOUCH_INVERT_X = True     # <-- for "opposites both ways", set True
TOUCH_INVERT_Y = True     # <-- for "opposites both ways", set True
# =====================


def get_display_size(disp):
    if hasattr(disp, "size") and callable(getattr(disp, "size")):
        try:
            w, h = disp.size()
            if isinstance(w, int) and isinstance(h, int):
                return w, h
        except Exception:
            pass
    w = getattr(disp, "width", None)
    h = getattr(disp, "height", None)
    if isinstance(w, int) and isinstance(h, int):
        return w, h
    return 240, 320


def load_font():
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ):
        try:
            return ImageFont.truetype(path, 12)
        except Exception:
            pass
    return ImageFont.load_default()


def blank_frame(W, H, font, ascii_only=False):
    bg = (0, 0, 0)
    bar = (28, 30, 36)
    ink = (235, 235, 245)
    header = "Midibox - Touch Demo (tap & drag)" if ascii_only else "Midibox • Touch Demo (tap & drag)"
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 18), fill=bar)
    try:
        d.text((6, 3), header, fill=ink, font=font)
    except Exception:
        d.text((6, 3), "Midibox - Touch Demo (tap & drag)", fill=ink, font=font)
    return img, d


def normalize_touch_payload(p):
    pid, x, y, ev = 0, 0, 0, None
    if isinstance(p, dict):
        pid = int(p.get("id", 0) or 0)
        x = int(p.get("x", 0) or 0)
        y = int(p.get("y", 0) or 0)
        ev = p.get("event", None)
    elif isinstance(p, (list, tuple)):
        if len(p) == 2:
            x, y = int(p[0]), int(p[1])
        elif len(p) == 3:
            pid, x, y = int(p[0]), int(p[1]), int(p[2])
        elif len(p) >= 4:
            pid, x, y, ev = int(p[0]), int(p[1]), int(p[2]), p[3]

    if isinstance(ev, str):
        ev_l = ev.lower()
        if "down" in ev_l or "start" in ev_l or "press" in ev_l:
            ev_str = "down"
        elif "up" in ev_l or "end" in ev_l or "release" in ev_l:
            ev_str = "up"
        else:
            ev_str = "move"
    elif isinstance(ev, bool):
        ev_str = "down" if ev else "up"
    elif isinstance(ev, int):
        ev_str = "up" if ev == 0 else ("down" if ev == 1 else "move")
    else:
        ev_str = "move"

    return pid, x, y, ev_str


# --- Rotation/mapping helpers -------------------------------------------------

def rotate_xy(x, y, W, H, rotation):
    if rotation == 0:
        return x, y
    elif rotation == 90:
        return y, (W - 1 - x)
    elif rotation == 180:
        return (W - 1 - x), (H - 1 - y)
    elif rotation == 270:
        return (H - 1 - y), x
    return x, y


def apply_touch_calibration(x, y, W, H):
    # 1) optional swap
    if TOUCH_SWAP_XY:
        x, y = y, x

    # 2) rotation of touch independently of screen rotation
    x, y = rotate_xy(x, y, W, H, TOUCH_ROTATION)

    # 3) optional axis inversions
    if TOUCH_INVERT_X:
        x = (W - 1 - x)
    if TOUCH_INVERT_Y:
        y = (H - 1 - y)

    # clamp
    if x < 0: x = 0
    if y < 0: y = 0
    if x >= W: x = W - 1
    if y >= H: y = H - 1
    return x, y


def rotate_image(img, rotation):
    if rotation == 0:
        return img
    elif rotation == 90:
        return img.rotate(90, expand=False)
    elif rotation == 180:
        return img.rotate(180, expand=False)
    elif rotation == 270:
        return img.rotate(270, expand=False)
    return img


def main():
    disp = Display()
    touch = Touch()

    W, H = get_display_size(disp)
    font = load_font()
    ascii_only = (font is ImageFont.load_default())

    # Try hardware rotation if supported
    use_software_image_rotation = True
    if hasattr(disp, "set_rotation"):
        try:
            disp.set_rotation(ROTATION)
            use_software_image_rotation = False
        except Exception:
            use_software_image_rotation = True

    trails: dict[int, deque] = {}
    max_trail_len = 24
    ink = (235, 235, 245)
    accent = (120, 200, 255)

    img, d = blank_frame(W, H, font, ascii_only=ascii_only)
    frame_to_show = rotate_image(img, ROTATION) if use_software_image_rotation else img
    disp.show(frame_to_show)

    last_draw = 0.0
    min_frame_dt = 1 / 40.0

    try:
        while True:
            pts = touch.read_touches() or []
            changed = False

            for p in pts:
                pid, x_raw, y_raw, ev = normalize_touch_payload(p)

                # Apply touch calibration independent of screen orientation
                x, y = apply_touch_calibration(x_raw, y_raw, W, H)

                if ev in ("down", "move"):
                    trails.setdefault(pid, deque(maxlen=max_trail_len)).append((x, y))
                    changed = True
                elif ev == "up":
                    changed = True

            now = time.time()
            if changed and (now - last_draw) >= min_frame_dt:
                img, d = blank_frame(W, H, font, ascii_only=ascii_only)

                for pid, q in trails.items():
                    if not q:
                        continue
                    if len(q) == 1:
                        x, y = q[0]
                        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=ink)
                    else:
                        pts_xy = list(q)
                        d.line(pts_xy, fill=ink, width=3)
                        x, y = pts_xy[-1]
                        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=accent)

                frame_to_show = rotate_image(img, ROTATION) if use_software_image_rotation else img
                disp.show(frame_to_show)
                last_draw = now

            time.sleep(0.005)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
