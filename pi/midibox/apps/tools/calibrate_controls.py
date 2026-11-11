#!/usr/bin/env python3
"""
Unified calibration:
  - Infinium Fader 1 (UART)
  - Infinium Fader 2 (UART)
  - Pitch/Mod via ADS1115Reader (auto-detected getter)

Run:
  PYTHONPATH=. python3 -m apps.tools.calibrate_controls \
    --f1 /dev/ttyAMA2 --f2 /dev/ttyAMA3 \
    --ads-addr 0x48 --pitch-ch 0 --mod-ch 1 \
    --out config/calibration.json
"""

import argparse, json, os, sys, time
from statistics import median

# ensure repo root on path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from drivers.faders.infinium_x1_serial import (
    InfiniumX1Serial, InfiniumSerialConfig, SerialConfig,
    FilterConfig, CurveConfig, PickupConfig, GestureConfig, MappingLayers
)

# Your ADS class
from midio.ads1115_reader import ADS1115Reader as ADSReader


# -------- helpers --------

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

def iter_fader_norm(fader: InfiniumX1Serial):
    while True:
        ev = fader.process()
        yield float(ev["norm"])

def pick_ads_getter(ads_obj):
    """
    Find a callable to read a single channel from ADS.
    Tries common method names; prints which one is used.
    """
    names = (
        "read",            # (ch) or ()
        "read_channel",    # (ch)
        "read_voltage",    # (ch) or ()
        "read_raw",        # (ch)
        "read_adc",        # (ch)
        "read_scaled",     # (ch)
        "read_norm",       # (ch)
    )
    methods = [(n, getattr(ads_obj, n)) for n in names if hasattr(ads_obj, n)]
    if not methods:
        raise RuntimeError("ADS object exposes none of: " + ", ".join(names))

    def wrap(method):
        def call(ch):
            try:
                return float(method(ch))
            except TypeError:
                return float(method())
        return call

    # choose the first that works once
    for name, m in methods:
        try:
            fn = wrap(m)
            _ = fn(0)  # probe
            print(f"[cal] Using ADS getter: {name}(ch?)")
            return fn
        except Exception:
            continue

    # fallback to first name anyway
    name, m = methods[0]
    print(f"[cal] Fallback ADS getter: {name}")
    return wrap(m)

def iter_ads(reader, getter, ch: int):
    while True:
        try:
            yield getter(ch)
        except Exception:
            yield None

def track_min_max(sample_iter, seconds: float = 5.0):
    print(f"  >> Move full travel for {seconds:.1f}s …")
    t0 = time.time()
    vals = []
    vmin, vmax = float("+inf"), float("-inf")
    while time.time() - t0 < seconds:
        v = next(sample_iter, None)
        if v is None:
            time.sleep(0.001); continue
        vmin = v if vmin == float("+inf") else min(vmin, v)
        vmax = v if vmax == float("-inf") else max(vmax, v)
        vals.append(v)
        time.sleep(0.002)
    if not vals:
        return 0.0, 1.0, 0.5
    vmid = median(vals)
    print(f"     min={vmin:.3f}  mid~={vmid:.3f}  max={vmax:.3f}")
    return float(vmin), float(vmax), float(vmid)


# -------- main --------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--f1", default=None, help="UART for Fader 1 (/dev/ttyAMA2)")
    ap.add_argument("--f2", default=None, help="UART for Fader 2 (/dev/ttyAMA3)")
    ap.add_argument("--ads-addr", default="0x48", help="ADS1115 I2C address")
    ap.add_argument("--pitch-ch", type=int, default=None, help="ADS channel for Pitch (0..3)")
    ap.add_argument("--mod-ch", type=int, default=None, help="ADS channel for Mod (0..3)")
    ap.add_argument("--out", default="config/calibration.json")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    cal = {}

    # Faders
    if args.f1:
        f1 = make_fader(args.f1)
        print("\nCalibrating Fader 1")
        m1, M1, _ = track_min_max(iter_fader_norm(f1))
        cal["fader1"] = {"min": m1, "max": M1}

    if args.f2:
        f2 = make_fader(args.f2)
        print("\nCalibrating Fader 2")
        m2, M2, _ = track_min_max(iter_fader_norm(f2))
        cal["fader2"] = {"min": m2, "max": M2}

    # ADS (Pitch/Mod)
    ads = None
    getter = None
    try:
        # try constructor with addr, else no-arg
        try:
            ads = ADSReader(addr=int(args.ads_addr, 16))
        except TypeError:
            ads = ADSReader()
        getter = pick_ads_getter(ads)
    except Exception as e:
        print("[cal] Skipping ADS calibration:", e)

    if ads and getter and args.pitch_ch is not None:
        print("\nCalibrating Pitch (ADS)")
        mp, Mp, _ = track_min_max(iter_ads(ads, getter, args.pitch_ch))
        cal["pitch"] = {"min": mp, "max": Mp}

    if ads and getter and args.mod_ch is not None:
        print("\nCalibrating Mod (ADS)")
        mm, Mm, _ = track_min_max(iter_ads(ads, getter, args.mod_ch))
        cal["mod"] = {"min": mm, "max": Mm}

    with open(args.out, "w") as f:
        json.dump(cal, f, indent=2)
    print(f"\n✅ Saved calibration → {args.out}\n{json.dumps(cal, indent=2)}")

if __name__ == "__main__":
    main()
