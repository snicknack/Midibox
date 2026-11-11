#!/usr/bin/env python3
import pigpio, time, sys

PIN_SCLK = 23      # input: board SCLK
PIN_DATA = 24      # input: board DATA (board->Pi)
PIN_CS   = 22      # output: 2N3904 base (sinks /CS)

TRIGGER_MODE   = "level_low"   # "level_low" or "pulse_low_release"
SAMPLE_ON_RISE = True
WATCHDOG_US    = 3000          # frame ends if no clocks for this long
CS_LOW_MS      = 5000
INTER_MS       = 1000

def pack(bits):
    out, b = [], 0
    for i, bit in enumerate(bits):
        b = (b << 1) | (bit & 1)
        if (i & 7) == 7:
            out.append(b); b = 0
    if len(bits) & 7:
        out.append(b << (8 - (len(bits) & 7)))
    return out

pi = pigpio.pi()
assert pi.connected, "sudo pigpiod"

for p in (PIN_SCLK, PIN_DATA):
    pi.set_mode(p, pigpio.INPUT)
    pi.set_pull_up_down(p, pigpio.PUD_OFF)
    pi.set_glitch_filter(p, 50)

pi.set_mode(PIN_CS, pigpio.OUTPUT)
pi.write(PIN_CS, 1)  # idle HIGH (transistor off → /CS released)

bits, capturing = [], False

def end_frame():
    global bits, capturing
    if not bits: capturing = False; return
    by = pack(bits)
    print(f"{len(bits):4d} bits -> " + " ".join(f"{x:02X}" for x in by))
    bits.clear(); capturing = False

def on_clk(gpio, level, tick):
    global capturing
    if level == 2:
        if capturing: end_frame()
        return
    want = 1 if SAMPLE_ON_RISE else 0
    if capturing and level == want:
        bits.append(pi.read(PIN_DATA))
        pi.set_watchdog(PIN_SCLK, WATCHDOG_US)

cb = pi.callback(PIN_SCLK, pigpio.EITHER_EDGE, on_clk)

print("Sniffer running. Ctrl+C to stop.")
try:
    while True:
        bits.clear(); capturing = True
        pi.set_watchdog(PIN_SCLK, WATCHDOG_US)

        if TRIGGER_MODE == "level_low":
            # Assert LOW and keep it LOW while we expect clocks
            pi.write(PIN_CS, 0)
            time.sleep(CS_LOW_MS/1000.0)
            pi.write(PIN_CS, 1)
        else:  # "pulse_low_release"
            # Short LOW pulse, burst occurs after release
            pi.write(PIN_CS, 0)
            time.sleep(0.002)       # 2 ms low
            pi.write(PIN_CS, 1)
            time.sleep(CS_LOW_MS/1000.0)

        time.sleep(INTER_MS/1000.0)

except KeyboardInterrupt:
    pass
finally:
    pi.set_watchdog(PIN_SCLK, 0)
    cb.cancel()
    pi.stop()
