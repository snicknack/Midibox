# midibox/examples/encoders_demo_poll.py
import time
from midibox.io.sx1509 import SX1509

_Q = {0b0001:+1,0b0011:+1,0b0110:+1,0b0100:+1,0b0010:-1,0b0111:-1,0b1110:-1,0b1100:-1}

def main():
    a,b,sw = 8,9,10  # <-- your actual P#s
    ic = SX1509(address=0x3E)
    mask = (1<<a)|(1<<b)|(1<<sw)
    ic.set_dir_inputs(mask); ic.enable_pullups(mask)
    prev_ab = ((ic.read_inputs()>>a)&1)|(((ic.read_inputs()>>b)&1)<<1)
    pressed = (ic.read_inputs()>>sw)&1
    count = 0
    print("Polling enc… Ctrl+C to quit")
    while True:
        port = ic.read_inputs()
        ab = ((port>>a)&1)|(((port>>b)&1)<<1)
        if ab != prev_ab:
            count += _Q.get((prev_ab<<2)|ab, 0)
            prev_ab = ab
            if count:
                print(f"ENC1: {count:+d}")
                count = 0
        sw_now = (port>>sw)&1
        if sw_now != pressed:
            pressed = sw_now
            print("SW: " + ("DOWN" if pressed==0 else "UP"))
        time.sleep(0.001)

if __name__ == "__main__":
    main()
