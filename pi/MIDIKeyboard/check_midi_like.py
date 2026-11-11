#!/usr/bin/env python3
import pigpio, time, sys

SCLK=23
DATA=24
WATCHDOG_US=500
GLITCH_US=0

MIDI_STATUS = {
    0x80:"Note Off", 0x90:"Note On", 0xA0:"Poly AT",
    0xB0:"Control", 0xC0:"ProgChg", 0xD0:"Chan AT",
    0xE0:"PitchBend", 0xF0:"System"
}

pi=pigpio.pi()
if not pi.connected:
    print("start pigpiod", file=sys.stderr)
    sys.exit(1)

for p in (SCLK,DATA):
    pi.set_mode(p,pigpio.INPUT)
    pi.set_pull_up_down(p,pigpio.PUD_OFF)
    pi.set_glitch_filter(p,GLITCH_US)

bits=[]; ticks=[]; capturing=False

def pack(bits):
    out, b = [], 0
    for i, bit in enumerate(bits):
        b = (b<<1)|(bit&1)
        if (i&7)==7: out.append(b); b=0
    if len(bits)&7: out.append(b<<(8-(len(bits)&7)))
    return out

def end_frame():
    global bits,ticks,capturing
    if not bits: capturing=False; return
    bytes_ = pack(bits)
    print("\n--- Burst ---")
    print("Hex:", " ".join(f"{x:02X}" for x in bytes_))
    # Interpret as MIDI if possible
    for b in bytes_:
        if b >= 0x80:
            desc = MIDI_STATUS.get(b & 0xF0, "Data/Unknown")
            print(f" {b:02X} ({desc})")
        else:
            print(f" {b:02X} (data)")
    bits.clear(); ticks.clear(); capturing=False

def on_clk(g,l,t):
    global capturing
    if l==2:
        if capturing: end_frame()
        return
    if l!=1: return
    if not capturing:
        capturing=True
        bits.clear(); ticks.clear()
    bits.append(pi.read(DATA))
    ticks.append(t)
    pi.set_watchdog(SCLK,WATCHDOG_US)

cb=pi.callback(SCLK,pigpio.EITHER_EDGE,on_clk)

print("Listening... press a few keys. Ctrl+C to stop.")
try:
    while True: time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    pi.set_watchdog(SCLK,0); cb.cancel(); pi.stop()
