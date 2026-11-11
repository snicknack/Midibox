# main.py  —  Raspberry Pi I/O service (no TFT)

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from midiio.pi_pitch_mod_reader import PitchModReader
from midiio.ads1115_mod import ADS1115Reader
from midiio.encoders_sx1509 import SX1509Encoders
import time

def main():
    # --- ADS1115 setup ---
    ads = ADS1115Reader(addr=0x48, rate_hz=100, channels=(0,1,2,3))
    ads.begin()

    # --- SX1509 setup ---
    enc = SX1509Encoders(
        i2c_addr=0x3E, int_pin=17,
        pairs=[(0,1),(3,4),(6,7),(9,10),(12,13)]
    )
    enc.begin()

    print("Running headless I/O service – press Ctrl+C to stop")
    try:
        while True:
            # Read encoders
            for idx, delta, pressed in enc.read_and_zero():
                if delta:
                    print(f"Encoder {idx}: Δ{delta}")

            # Read ADS channels
            vals = ads.values_cc  # dict {ch: value0-127}
            print("ADS:", vals)

            # Later: send these to ESP32 over UART or network
            time.sleep(0.05)

    except KeyboardInterrupt:
        enc.close()
        ads.close()
        print("Clean exit.")

if __name__ == "__main__":
    main()
