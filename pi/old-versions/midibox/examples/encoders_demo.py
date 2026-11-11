# midibox/examples/encoders_demo.py
import time
from midibox.io.encoders_sx1509 import SX1509Encoders

def main():
    encs = SX1509Encoders(
        address=0x3E, i2c_bus=1, int_gpio=22, rst_gpio=None,
        enc_maps=[
            {"name":"ENC1","a":8,"b":9,"sw":10},
            {"name":"ENC2","a":3,"b":4,"sw":5},
            {"name":"ENC3","a":6,"b":7,"sw":8},
            {"name":"ENC4","a":9,"b":10,"sw":11},
        ],
    )
    print("Rotate/press encoders… Ctrl+C to quit.")
    while True:
        for name, steps, pressed in encs.read_and_zero():
            if steps:
                print(f"{name}: {'+' if steps>0 else ''}{steps}")
            # pressed is level (True when held); emit on edge if you prefer
        time.sleep(0.01)

if __name__ == "__main__":
    main()
