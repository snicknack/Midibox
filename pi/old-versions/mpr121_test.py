import time, board, busio
import adafruit_mpr121

# Initialize I2C and MPR121
i2c = busio.I2C(board.SCL, board.SDA)
mpr121 = adafruit_mpr121.MPR121(i2c)

print("Touch the pads! Ctrl+C to stop.")
while True:
    for i in range(12):   # MPR121 has 12 inputs
        if mpr121[i].value:
            print(f"Pad {i} touched")
    time.sleep(0.05)
