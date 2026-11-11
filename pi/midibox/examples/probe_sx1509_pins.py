# probe_sx1509_pins.py
from time import sleep
from midibox.io.sx1509 import SX1509

ic = SX1509(address=0x3E)      # or address=None to auto-scan 0x3E/0x3F
ic.set_dir_inputs(0xFFFF)      # all inputs
ic.enable_pullups(0xFFFF)      # pull-ups ON (active-high idle)

print("Touch/short pins to GND. Changes will print as P#: HIGH/LOW")
last = ic.read_inputs()
print(f"Start: {last:016b}")
while True:
    val = ic.read_inputs()
    diff = val ^ last
    if diff:
        for p in range(16):
            if diff & (1<<p):
                state = "HIGH" if (val>>p)&1 else "LOW"
                print(f"P{p}: {state}")
        last = val
    sleep(0.01)

