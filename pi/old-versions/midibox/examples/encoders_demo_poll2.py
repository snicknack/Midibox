# midibox/examples/encoders_demo_poll2.py
import time
from midibox.io.encoders_sx1509_poll import SX1509EncodersPoll

def main():
    encs = SX1509EncodersPoll(address=0x3E, enc_maps=[{"name":"ENC1","a":8,"b":9  ,"sw":10. }])
    print("Polling enc… Ctrl+C to quit")
    while True:
        for name, steps, pressed in encs.read_and_zero():
            if steps: print(f"{name}: {steps:+d}")
            # if pressed: print("SW held")  # level, not edge
        time.sleep(0.01)

if __name__=="__main__":
    main()

