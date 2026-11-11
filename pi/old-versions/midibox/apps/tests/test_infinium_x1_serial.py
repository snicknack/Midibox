# apps/tests/test_infinium_x1_serial.py
# Minimal, quiet test for the Infinium serial fader using pair-to-CC parsing.
# Run from project root:
#   python3 -m apps.tests.test_infinium_x1_serial --port /dev/ttyS0

import argparse
import time

# If you prefer running directly (not as a module), uncomment:
# import os, sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from drivers.faders.infinium_x1_serial import (
    InfiniumX1Serial,
    InfiniumSerialConfig,
    SerialConfig,
    FilterConfig,
    CurveConfig,
    PickupConfig,
    GestureConfig,
    MappingLayers,
    DualMapping,
    Zone,
)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="/dev/serial0", help="Serial port for the fader (e.g., /dev/ttyS0)")
    ap.add_argument("--mode", choices=["single", "dual", "zones"], default="single")
    args = ap.parse_args()

    layers = MappingLayers(
        pages={
            "A": {"cc": 74},  # keep simple during bring-up
        },
        default_page="A"
    )

    cfg = InfiniumSerialConfig(
        serial=SerialConfig(port=args.port, baud=31250, timeout=0.001),
        filters=FilterConfig(smoothing_ms=6, rate_hz=500),
        curve=CurveConfig(kind="linear"),            # linear while debugging
        pickup=PickupConfig(enabled=False),          # pickup OFF for bring-up
        gesture=GestureConfig(velocity_scale=0.0, accel_scale=0.0,
                              throw_threshold=0.95, throw_window_s=0.2, throw_note=None),
        fourteen_bit=False,
        midi_channel=1,
        layers=layers,
        prefer_pitchbend=False,
        learn_cc=None
    )

    if args.mode == "dual":
        cfg.dual = DualMapping(bottom_cc=74, top_cc=91, split=0.5)
    elif args.mode == "zones":
        cfg.zones = [
            Zone(0.00, 0.25, cc=91),
            Zone(0.25, 0.50, cc=74),
            Zone(0.50, 0.75, cc=94),
            Zone(0.75, 1.00, cc=7),
        ]

    fader = InfiniumX1Serial(cfg)

    print(f"Reading {args.port} @31250… move the fader. (mode={args.mode})")

    last_val = None
    try:
        while True:
            ev = fader.process()
            # Only print when the main CC value changes by >= 1
            if ev["cc_events"]:
                cur = ev["cc_events"][0][1]
                if last_val is None or abs(cur - last_val) >= 1:
                    print(f"norm={ev['norm']:.3f} {'LATCHED' if ev['latched'] else '(pickup)'}  "
                          f"CC:{ev['cc_events']}  NOTE:{ev['note_events']}")
                    last_val = cur
            time.sleep(1.0 / fader.cfg.filters.rate_hz)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
