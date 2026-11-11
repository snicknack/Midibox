# ~/midibox/pi_pitch_mod_reader.py
import time, json, serial, mido
from .ads1115_reader import ADS1115Reader
from rpi_ws281x import PixelStrip, Color

LED_COUNT      = 2        # 0: pitch, 1: mod
LED_PIN        = 18       # GPIO18 (PWM)
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 255      # master brightness
LED_INVERT     = False
LED_CHANNEL    = 0


CAL_PATH   = "/home/stephennicholson/midibox/config/ads1115_cal.json"
SERIAL_DEV = "/dev/serial0"
BAUD       = 115200

# Match your LVGL widget IDs
W_PITCH = "uic_pitchBar"
W_MOD   = "uic_ModBar"

FORCE_SEND_SECONDS = 10.0  # time to force output for diagnostics


def to01(v, lo, hi, invert=False):
    """Normalize v between lo..hi to 0..1."""
    if hi <= lo:
        return 0.0
    x = (v - lo) / (hi - lo)
    if x < 0.0:
        x = 0.0
    if x > 1.0:
        x = 1.0
    return 1.0 - x if invert else x


def to7(x):
    """Convert 0..1 float to 0..127 integer."""
    y = int(x * 127 + 0.5)
    return 0 if y < 0 else (127 if y > 127 else y)


def send_to_esp(ser, name, value):
    """Send a named value over serial to the ESP32."""
    ser.write(f"{name}:{value}\n".encode())
    ser.flush()


strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
                   LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()



def main():
    print("Starting pitch/mod reader…")
    ads = ADS1115Reader(address=0x48)

    # ------- Choose a reader that returns CC-like values (0..127) -------
    if hasattr(ads, "read_cc"):
        def read_cc_idx(i):
            vals = ads.read_cc()  # list of 4 ints 0..127
            return int(vals[i])
        read_val = read_cc_idx
        reader_name = "read_cc()[idx] (0..127)"
    elif hasattr(ads, "read_channel"):
        def read_cc_idx(i):
            return int(ads.read_channel(i) * 127)
        read_val = read_cc_idx
        reader_name = "read_channel(i)*127 (CC)"
    elif hasattr(ads, "read_channel_raw"):
        read_val = ads.read_channel_raw
        reader_name = "read_channel_raw(i)"
    else:
        raise RuntimeError("ADS1115Reader needs read_cc()/read_channel()/read_channel_raw()")

    print(f"[ADS] using {reader_name}")

    # ------- Load calibration file -------
    with open(CAL_PATH, "r") as f:
        cal = json.load(f)

    pcal = cal["0"]
    mcal = cal["1"]
    pmin, pmax = pcal["min"], pcal["max"]
    mmin, mmax = mcal["min"], mcal["max"]
    pinv, minv = bool(pcal.get("invert", False)), bool(mcal.get("invert", False))
    pdead, mdead = int(pcal.get("deadband", 1)), int(mcal.get("deadband", 1))

    print(f"[CAL] Pitch {pmin}..{pmax} inv={pinv} dead={pdead} | Mod {mmin}..{mmax} inv={minv} dead={mdead}")

    ser = serial.Serial(SERIAL_DEV, BAUD, timeout=1)
    mout = mido.open_output()

    lastP = lastM = None
    lastP01 = lastM01 = 0.0
    force_until = time.time() + FORCE_SEND_SECONDS

    # ==================== MAIN LOOP ====================
    while True:
        # Read ADC channels
        pv = read_val(0)
        mv = read_val(1)

        # --- Normalize to 0..1 ---
        p01 = to01(pv, pmin, pmax, pinv)
        m01 = to01(mv, mmin, mmax, minv)

        # --- Apply smoothing ---
        alpha = 0.7  # lower = smoother, higher = faster
        p01 = (1 - alpha) * lastP01 + alpha * p01
        m01 = (1 - alpha) * lastM01 + alpha * m01
        lastP01, lastM01 = p01, m01

        # --- Convert to MIDI 7-bit ---
        p7 = to7(p01)
        m7 = to7(m01)

        # --- Set the LEDS ---
        # --- PITCH LED: dual colour, bright at extremes ---
        centre = 64
        diff = p7 - centre

        # Brightness grows as you move away from 64
        bright = int((abs(diff) / 63) * 255)
    
        if diff > 0:
            # Pitch up  → green
            r, g, b = 0, bright, 0
        elif diff < 0:
            # Pitch down → red
            r, g, b = bright, 0, 0
        else:
            # Exactly centre → off
            r = g = b = 0
    
        strip.setPixelColor(0, Color(r, g, b))
        
        # --- Set the Mod Wheel ---
        m255 = int(m01 * 255)
        MIN_FLOOR = 40
        GAMMA = 2.5
        #   1.0  = linear (no correction)
        #   1.8–2.2 = normal human-eye response (standard gamma)
        #   3.0  = very steep curve (most of the change happens near the top)
        m_lin = m01
        m_gamma = m_lin ** GAMMA
        m255 = int(MIN_FLOOR + (255 - MIN_FLOOR) * m7 /127.0) 
        strip.setPixelColor(1, Color(0, 0, m255))
        strip.show()

        # --- Debug line ---
        print(
            f"VAL P/M: {pv:5} {mv:5} | 0-1: {p01:0.3f} {m01:0.3f} | 7bit: {p7:3} {m7:3}",
            end="\r",
        )

        # --- Force-send for first few seconds ---
        if time.time() < force_until:
            mout.send(mido.Message("pitchwheel", pitch=int(p01 * 16383) - 8192))
            send_to_esp(ser, W_PITCH, p7)
            mout.send(mido.Message("control_change", control=1, value=m7))
            send_to_esp(ser, W_MOD, m7)
            lastP, lastM = p7, m7
        else:
            # --- Only send when changed beyond deadband ---
            if lastP is None or abs(p7 - lastP) >= pdead:
                mout.send(mido.Message("pitchwheel", pitch=int(p01 * 16383) - 8192))
                send_to_esp(ser, W_PITCH, p7)
                lastP = p7

            if lastM is None or abs(m7 - lastM) >= mdead:
                mout.send(mido.Message("control_change", control=1, value=m7))
                send_to_esp(ser, W_MOD, m7)
                lastM = m7

        time.sleep(0.01)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
