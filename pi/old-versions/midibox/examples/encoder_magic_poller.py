python3 - <<'PY'
from time import sleep
from midibox.io.sx1509 import SX1509

# --- YOUR REAL P NUMBERS HERE ---
A,B,SW = 8,9,10     # EC11: A–C–B; C->GND, SW1->GND, SW2->P10

# 4x quadrature table
Q = {0b0001:+1,0b0011:+1,0b0110:+1,0b0100:+1,
     0b0010:-1,0b0111:-1,0b1110:-1,0b1100:-1}

ic = SX1509(address=0x3E)     # or address=None to auto-scan
mask = (1<<A)|(1<<B)|(1<<SW)
ic.set_dir_inputs(mask)
ic.enable_pullups(mask)

port = ic.read_inputs()
ab_prev = ((port>>A)&1) | (((port>>B)&1)<<1)
sw_prev = (port>>SW)&1  # 1=idle (pull-up), 0=pressed

print("Polling enc + switch… Ctrl+C to quit")
while True:
    port = ic.read_inputs()
    ab = ((port>>A)&1) | (((port>>B)&1)<<1)
    if ab != ab_prev:
        step = Q.get((ab_prev<<2)|ab, 0)
        if step: print(f"ENC: {step:+d}")
        ab_prev = ab
    sw = (port>>SW)&1
    if sw != sw_prev:
        print("SW:", "DOWN" if sw==0 else "UP")
        sw_prev = sw
    sleep(0.001)
PY
