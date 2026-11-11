# drv2605l_test_fixed.py
import time, board, busio
import adafruit_drv2605 as drvlib

i2c = busio.I2C(board.SCL, board.SDA)
drv = drvlib.DRV2605(i2c, address=0x5A)

# LRA (linear resonant) mode
drv.use_ERM()
drv.library = 1  # LRA waveform set

# helper to fire a single ROM effect by ID
def play_effect(effect_id):
    drv.sequence[0] = drvlib.Effect(effect_id)
    # clear any remaining slots (optional hygiene)
    for i in range(1, 8):
        drv.sequence[i] = drvlib.Pause(0)
    drv.play()
    # tiny settle delay
    time.sleep(0.05)

print("Single strong click…")
for _ in range(20):
    play_effect(47)   # Sharp Click
    time.sleep(0.40)

print("Three sharp ticks…")
for _ in range(20):
    play_effect(1)   # Sharp Click
    time.sleep(0.12)

print("Confirm (double click)…")
for _ in range(20):
    play_effect(15)   # Sharp Click
    time.sleep(0.50)

drv.stop()
print("Done.")
