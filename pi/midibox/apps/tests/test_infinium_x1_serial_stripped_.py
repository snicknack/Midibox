# test_infinium_x1_serial.py
# Live test: reads /dev/serial0 at 31250 baud and prints interpreted outputs.

import sys, os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
import time, argparse
from midibox.drivers.faders.infinium_x1_serial import *

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="/dev/serial0")
    ap.add_argument("--learn-cc", type=int, default=None, help="Lock to a specific CC if your fader sends CCs")
    ap.add_argument("--prefer-pb", action="store_true", help="Prefer 14-bit pitch bend if present")
    ap.add_argument("--mode", choices=["single","dual","zones"], default="single")
    args = ap.parse_args()

    layers = MappingLayers(
        pages={
            "A":{"cc":74,},    # Filter + side modulation
            "B":{"cc":91,},    # Reverb + side modulation
        },
        default_page="A"
    )

    cfg = InfiniumSerialConfig(
        serial=SerialConfig(port=args.port, baud=31250, timeout=0.001),
        filters=FilterConfig(smoothing_ms=6, rate_hz=500),
        curve=CurveConfig(kind="s", s_strength=0.6),
        pickup=PickupConfig(enabled=False, deadband_cc=3),
        gesture=GestureConfig(velocity_scale=1.0, accel_scale=0.4, throw_threshold=0.9, throw_window_s=0.2, throw_note=60),
        fourteen_bit=True,
        midi_channel=1,
        layers=layers,
        prefer_pitchbend=args.prefer_pb,
        learn_cc=args.learn_cc
    )

    if args.mode == "dual":
        cfg.dual = DualMapping(bottom_cc=74, top_cc=91, split=0.5)
    elif args.mode == "zones":
        cfg.zones = [
            Zone(0.00,0.25, cc=91),  # Reverb
            Zone(0.25,0.50, cc=74),  # Filter
            Zone(0.50,0.75, cc=94),  # Delay feedback
            Zone(0.75,1.00, cc=7),   # Master volume
        ]

    fader = InfiniumX1Serial(cfg)
    fader.set_target_value_for_pickup(64)  # demo pickup target

    print("Reading serial... CTRL+C to stop.")
    try:
        while True:
            ev = fader.process()
            # Pretty print minimal info
            z = f" Z{ev['zone']}" if ev['zone'] is not None else ""
            latch = " LATCHED" if ev['latched'] else " (pickup)"
            if ev['cc_events'] or ev['note_events']:
                print(f"norm={ev['norm']:.3f}{z}{latch}  CC:{ev['cc_events']}  NOTE:{ev['note_events']}")
            time.sleep(1/ fader.cfg.filters.rate_hz)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
