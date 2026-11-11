import time, board, busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

# Setup I2C and ADC
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)  # old versions default to single-shot mode

# Define channels
channels = [
    AnalogIn(ads, ADS1115.P0),
    AnalogIn(ads, ADS1115.P1),
    AnalogIn(ads, ADS1115.P2),
    AnalogIn(ads, ADS1115.P3)
]

print("Reading ADS1115 channels 0–3 ... Ctrl+C to stop\n")

while True:
    values = [ch.value for ch in channels]
    volts = [ch.voltage for ch in channels]
    print(f"RAW: {values} | VOLTS: {[round(v,3) for v in volts]}")
    time.sleep(0.2)
