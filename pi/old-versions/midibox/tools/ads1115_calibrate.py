#!/usr/bin/env python3
import os, json, time
from midibox.io.ads1115_reader import ADS1115Reader

CAL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "ads1115_cal.json")

CHANNELS = [
    (0, "Pitch"),
    (1, "Mod"),
    (2, "FaderA"),
    (3, "FaderB"),
]

def prompt(msg):
    input(msg + "  Press Enter…")

def main():
    print("=== ADS1115 Calibration ===")
    ads = ADS1115Reader(address=0x48, channels=[c for c,_ in CHANNELS], cal_path=CAL_PATH, ema_alpha=0.1)
    cal = {}

    for ch, name in CHANNELS:
        print(f"\n-- {name} (AIN{ch}) --")
        prompt(f"Move {name} to its **MIN** (fully down/left). Hold steady.")
        time.sleep(0.3)
        rmins = []
        for _ in range(20):
            r = ads.read_cc()[ch]  # using pre-EMA 7-bit, fine for min/max capture
            rmins.append(r)
            time.sleep(0.02)
        vmin = min(rmins)

        prompt(f"Move {name} to its **MAX** (fully up/right). Hold steady.")
        time.sleep(0.3)
        rmaxs = []
        for _ in range(20):
            r = ads.read_cc()[ch]
            rmaxs.append(r)
            time.sleep(0.02)
        vmax = max(rmaxs)

        if vmax < vmin:
            vmin, vmax = vmax, vmin  # just in case
        invert = False
        if vmin > vmax:  # unlikely, but guard
            vmin, vmax = 0, 127
        print(f"Captured range for {name}: min={vmin}, max={vmax}")

        ans = input("Invert this control? (y/N): ").strip().lower()
        invert = (ans == "y")

        dead = input("Deadband (0–5 typical, Enter=0): ").strip()
        deadband = int(dead) if dead.isdigit() else 0

        cal[ch] = {"name": name, "min": int(vmin), "max": int(vmax), "invert": invert, "deadband": deadband}

    # merge with existing file (if any)
    if os.path.isfile(CAL_PATH):
        try:
            with open(CAL_PATH, "r") as f:
                existing = json.load(f)
        except Exception:
            existing = {}
    else:
        existing = {}

    existing.update({str(k): v for k, v in cal.items()})
    os.makedirs(os.path.dirname(CAL_PATH), exist_ok=True)
    with open(CAL_PATH, "w") as f:
        json.dump(existing, f, indent=2, sort_keys=True)

    print("\nSaved calibration to:", CAL_PATH)
    print(json.dumps(existing, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
