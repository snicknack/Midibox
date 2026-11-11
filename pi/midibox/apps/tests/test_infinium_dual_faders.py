#!/usr/bin/env python3
# Two Infinium faders → scaled CC values using saved calibration JSON.

import time, json, os
from drivers.faders.infinium_x1_serial import (
    InfiniumX1Serial, InfiniumSerialConfig, SerialConfig, FilterConfig,
    CurveConfig, PickupConfig, GestureConfig, MappingLayers
)

CAL_PATH = "config/calibration.json"  # produced by calibrate_controls.py

def make_fader(port: str) -> InfiniumX1Serial:
    layers = MappingLayers(pages={"A": {"cc": 74}}, default_page="A")
    cfg = InfiniumSerialConfig(
        serial=SerialConfig(port=port, baud=31250, timeout=0.001),
        filters=FilterConfig(smoothing_ms=6, rate_hz=500),
        curve=CurveConfig(kind="linear"),
        pickup=PickupConfig(enabled=False),
        gesture=GestureConfig(velocity_scale=0.0, accel_scale=0.0),
        fourteen_bit=False, midi_channel=1, layers=layers,
        prefer_pitchbend=False, learn_cc=None
    )
    return InfiniumX1Serial(cfg)

def load_cal():
    if os.path.exists(CAL_PATH):
        with open(CAL_PATH) as f:
            return json.load(f)
    return {}

def scale_to_cc(x, cmin=0.0, cmax=1.0):
    # maps input x using learned min/max → 0..127
    if cmax <= cmin + 1e-9:
        return 0
    t = (x - cmin) / (cmax - cmin)
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    return int(round(t * 127))

def main():
    cal = load_cal()
    f1 = make_fader("/dev/ttyAMA2")
    f2 = make_fader("/dev/ttyAMA3")

    f1c = cal.get("fader1", {"min": 0.0, "max": 1.0})
    f2c = cal.get("fader2", {"min": 0.0, "max": 1.0})

    print("[OK] FADER 1 -> /dev/ttyAMA2")
    print("[OK] FADER 2 -> /dev/ttyAMA3")
    print(f"Using calibration: F1[{f1c['min']:.3f},{f1c['max']:.3f}]  "
          f"F2[{f2c['min']:.3f},{f2c['max']:.3f}]")
    print("Move both faders!  Ctrl-C to exit.\n")

    rate_hz = 500
    last1 = last2 = None
    try:
        while True:
            ev1 = f1.process()
            ev2 = f2.process()

            cc1 = scale_to_cc(ev1['norm'], f1c['min'], f1c['max'])
            cc2 = scale_to_cc(ev2['norm'], f2c['min'], f2c['max'])

            if cc1 != last1 or cc2 != last2:
                print(f"F1={ev1['norm']:.3f} ({cc1:3})   F2={ev2['norm']:.3f} ({cc2:3})")
                last1, last2 = cc1, cc2

            time.sleep(1.0 / rate_hz)
    except KeyboardInterrupt:
        print("\nExiting dual-fader scaled test.")

if __name__ == "__main__":
    main()
