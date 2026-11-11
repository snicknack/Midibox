# ~/midibox/pi_pitch_mod_reader.py
import time, json, serial, mido
from midibox.io.ads1115_reader import ADS1115Reader

CAL_PATH   = "/home/stephennicholson/midibox/config/ads1115_cal.json"
SERIAL_DEV = "/dev/serial0"
BAUD       = 115200

# Use your exact LVGL IDs
W_PITCH = "uic_pitchBar"
W_MOD   = "uic_ModBar"

FORCE_SEND_SECONDS = 10.0  # brief diagnostic burst

def to01(v, lo, hi, invert=False):
    if hi <= lo: return 0.0
    x = (v - lo) / (hi - lo)
    if x < 0.0: x = 0.0
    if x > 1.0: x = 1.0
    return 1.0 - x if invert else x

def to7(x):
    y = int(x * 127 + 0.5)
    return 0 if y < 0 else (127 if y > 127 else y)

def send_to_esp(ser, name, value):
    ser.write(f"{name}:{value}\n".encode())
    ser.flush()

def main():
    print("Starting pitch/mod reader…")
    ads = ADS1115Reader(address=0x48)

    # ------- Choose a reader that returns CC units (0..127) -------
    # Prefer read_cc() which returns a list of 4 channels
    if hasattr(ads, "read_cc"):
        def read_cc_idx(i):
            vals = ads.read_cc()          # list of 4 ints 0..127
            return int(vals[i])
        read_val = read_cc_idx
        reader_name = "read_cc()[idx]  (0..127)"
    # Fallback: read_channel(i) 0..1 -> convert to CC
    elif hasattr(ads, "read_channel"):
        def read_cc_idx(i):
            return int(ads.read_channel(i) * 127)
        read_val = read_cc_idx
        reader_name = "read_channel(i)*127 (cc)"
    # Fallback: read_channel_raw(i) (int) -> scale heuristically if cal looks CC
    elif hasattr(ads, "read_channel_raw"):
        # raw is device counts; we’ll normalize using calibration below,
        # but also scale to CC if calibration looks like CC
        read_val = ads.read_channel_raw
        reader_name = "read_channel_raw(i) (raw counts)"
    else:
        raise RuntimeError("ADS1115Reader needs read_cc()/read_channel()/read_channel_raw()")

    print(f"[ADS] using {reader_name}")

    # ------- Load calibration (keys '0' and '1') -------
    with open(CAL_PATH, "r") as f:
        cal = json.load(f)

    pcal = cal["0"]; mcal = cal["1"]
    pmin, pmax = pcal["min"], pcal["max"]
    mmin, mmax = mcal["min"], mcal["max"]
    pinv, minv = bool(pcal.get("invert", False)), bool(mcal.get("invert", False))
    pdead, mdead = int(pcal.get("deadband", 1)), int(mcal.get("deadband", 1))

    # Detect if calibration is CC-like (>= 0..100). We’ll treat values as CC units.
    cal_is_cc = (pmax > 10 or mmax > 10)
    print(f"[CAL] Pitch {pmin}..{pmax} inv={pinv} dead={pdead} | Mod {mmin}..{mmax} inv={minv} dead={mdead} | cal_is_cc={cal_is_cc}")

    ser  = serial.Serial(SERIAL_DEV, BAUD, timeout=1)
    mout = mido.open_output()

    lastP = lastM = None
    force_until = time.time() + FORCE_SEND_SECONDS

    while True:
        # Read current values
        pv = read_val(0)
        mv = read_val(1)

        # If reader returned raw counts and calibration looks CC, scale raw ~0..1→CC.
        # (Usually we won’t hit this branch because read_cc/read_channel were chosen.)
        if not cal_is_cc and isinstance(pv, int) and (pmax > 10 or mmax > 10):
            cal_is_cc = True  # once detected, stick with it

        # Normalize to 0..1 using calibration units (both sides now CC-like)
        p01 = to01(pv, pmin, pmax, pinv)
        m01 = to01(mv, mmin, mmax, minv)
        p7  = to7(p01)
        m7  = to7(m01)

        # Live diagnostics
        print(f"VAL P/M: {pv:5} {mv:5} | 0-1: {p01:0.3f} {m01:0.3f} | 7bit: {p7:3} {m7:3}", end="\r")

        # Force-send briefly so you can see GUI move instantly
        if time.time() < force_until:
            mout.send(mido.Message("pitchwheel", pitch=int(p01*16383) - 8192))
            send_to_esp(ser, W_PITCH, p7)
            mout.send(mido.Message("control_change", control=1, value=m7))
            send_to_esp(ser, W_MOD, m7)
            lastP, lastM = p7, m7
        else:
            if lastP is None or abs(p7 - lastP) >= pdead:
                mout.send(mido.Message("pitchwheel", pitch=int(p01*16383) - 8192))
                send_to_esp(ser, W_PITCH, p7); lastP = p7
            if lastM is None or abs(m7 - lastM) >= mdead:
                mout.send(mido.Message("control_change", control=1, value=m7))
                send_to_esp(ser, W_MOD, m7);   lastM = m7

        time.sleep(0.01)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
