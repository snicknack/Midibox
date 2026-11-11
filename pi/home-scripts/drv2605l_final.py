import time, board, busio
import adafruit_drv2605 as drv

i2c = busio.I2C(board.SCL, board.SDA)
h = drv.DRV2605(i2c, address=0x5A)

# select the LRA library
h.use_ERM()
h.library = 1  # LRA waveform set

print("Effect test…")
h.sequence[0] = drv.Effect(3)  # strong click 100%
for i in range(1, 7):
    h.sequence[i] = drv.Pause(0)
h.play()
time.sleep(0.4)

# --- Real-time mode (direct drive) ---
print("Realtime test (should buzz for ~1s)…")
# the constants live in the drv module in some versions
if hasattr(drv, "DRV2605_MODE_REALTIME"):
    h.mode = drv.DRV2605_MODE_REALTIME
else:
    # fall back to numeric register value for realtime playback
    h.mode = 5

h.realtime_value = 100     # 0–127 amplitude
time.sleep(1.0)
h.realtime_value = 0
h.stop()
print("Done.")
