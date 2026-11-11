import time, board, busio
import adafruit_mpr121
import mido

# ---- MPR121 (I2C) ----
i2c = busio.I2C(board.SCL, board.SDA)
mpr = adafruit_mpr121.MPR121(i2c)

# ---- MIDI out ----
# 1) Create a virtual ALSA MIDI port on the Pi
#    Other apps on the Pi can connect to it (FluidSynth, a DAW, etc.)
out = mido.open_output("MPR121 Pads", virtual=True)

# If instead you want to send to a specific connected USB MIDI device,
# comment the line above and uncomment one of these, adjusting the name:
# print(mido.get_output_names())
# out = mido.open_output('USB MIDI Interface  MIDI 1')

# ---- Mapping ----
BASE_NOTE = 60          # C4
CHANNEL   = 0           # MIDI channel 1 (0-based)
FIXED_VEL = 100         # velocity if you don’t want “sensitivity” calc

# Track previous touch state to send Note Off on release
prev = [False]*12

print("MIDI port 'MPR121 Pads' is live. Touch pads to play notes.")
try:
    while True:
        for i in range(12):
            cur = mpr[i].value
            if cur != prev[i]:
                note = BASE_NOTE + i

                if cur:
                    # Optional: derive a crude velocity from raw delta
                    # (difference between baseline and filtered)
                    try:
                        delta = max(0, mpr.baseline_data(i) - mpr.filtered_data(i))
                        vel = max(1, min(127, int(delta/2)))  # tune divisor to taste
                    except Exception:
                        vel = FIXED_VEL

                    out.send(mido.Message('note_on', note=note, velocity=vel, channel=CHANNEL))
                    # print(f"Pad {i} ON  note={note} vel={vel}")
                else:
                    out.send(mido.Message('note_off', note=note, velocity=0, channel=CHANNEL))
                    # print(f"Pad {i} OFF note={note}")

                prev[i] = cur
        time.sleep(0.005)   # ~5 ms scan
except KeyboardInterrupt:
    pass
