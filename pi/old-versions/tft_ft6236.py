import board
import busio
import adafruit_touchscreen

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize touchscreen
touch = adafruit_ft6236.Adafruit_FT6236(i2c)

print("Touchscreen test - touch the display!")

while True:
    if touch.touched:
        point = touch.touch_point
        if point:
            print(f"Touch at x={point['x']}, y={point['y']}")
