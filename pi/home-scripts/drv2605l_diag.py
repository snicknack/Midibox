import time, board, busio
import adafruit_drv2605 as d

i2c = busio.I2C(board.SCL, board.SDA)
h = d.DRV2605(i2c, address=0x5A)

# Force LRA mode + LRA library
h.use_LRM()
h.library = 6  # LRA library

# Test 1: ROM effect
print("Effect test…")
h.sequence[0] = d.Effect(47)  # Strong click 100%
for i in range(1, 8):
    h.sequence[i] = d.Pause(0)
h.play()
time.sleep(0.4)

# Test 2: Real-time playback (direct drive)
print("Realtime test (should buzz for ~1s)…")
h.mode = h.MODE_REALTIME  # <-- fixed constant reference
h.realtime_value = 100    # 0–127 = amplitude
time.sleep(1)
h.realtime_value = 0
h.stop()
print("Done.")
