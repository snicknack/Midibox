# apps/tests/test_infinium_dual_faders.py
# Test script for TWO Infinium X1 faders:
#   Fader 1 -> /dev/ttyAMA2
#   Fader 2 -> /dev/ttyAMA3

import time
from drivers.faders.infinium_x1_serial import (
    InfiniumX1Serial,
    InfiniumSerialConfig,
    SerialConfig,
    FilterConfig,
    CurveConfig,
    PickupConfig,
    GestureConfig,
    MappingLayers,
)

def make_fader(port: str, name: str) -> InfiniumX1Serial:
    layers = MappingLayers(pages={"A": {"cc": 74}}, default_page="A")

    cfg = InfiniumSerialConfig(
        serial=SerialConfig(port=port, baud=31250, timeout=0.001),
        filters=FilterConfig(smoothing_ms=6, rate_hz=500),
        curve=CurveConfig(kind="linear"),
        pickup=PickupConfig(enabled=False),
        gesture=GestureConfig(velocity_scale=0.0, accel_scale=0.0),
        fourteen_bit=False,
        midi_channel=1,
        layers=layers,
    )

    fader = InfiniumX1Serial(cfg)
    print(f"[OK] {name} initialized on {port}")
    return fader


def main():
    fader1 = make_fader("/dev/ttyAMA2", "FADER 1")
    fader2 = make_fader("/dev/ttyAMA3", "FADER 2")

    print("Move both faders!  Ctrl-C to exit.\n")

    last1 = last2 = None
    try:
        while True:
            ev1 = fader1.process()
            ev2 = fader2.process()

            # Only print when either changes
            v1 = ev1["cc_events"][0][1] if ev1["cc_events"] else last1
            v2 = ev2["cc_events"][0][1] if ev2["cc_events"] else last2
            if (v1 != last1) or (v2 != last2):
                print(f"F1={ev1['norm']:.3f} ({v1:3})   F2={ev2['norm']:.3f} ({v2:3})")
                last1, last2 = v1, v2

            time.sleep(1.0 / 500)  # 500 Hz loop
    except KeyboardInterrupt:
        print("\nExiting dual-fader test.")


if __name__ == "__main__":
    main()
