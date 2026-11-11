#!/usr/bin/env python3
# pulse_cs_and_sniff.py
# GPIO23 pulses /CS (via 2N3904) once per second.
# Samples DATA on each SCLK↑, prints the frame, flashes LED on activity.

import pigpio, time

# === BCM pin map ===
PIN_CS   = 23   # OUTPUT: drives /CS transistor base (HIGH = /CS pulled LOW)
PIN_SCLK = 24   # INPUT : board SCLK
PIN_DATA = 25   # INPUT : board DATA (MOSI-out)
PIN_LED  = 17   # OUTPUT: activity LED

# === Tuning ===
PULSE_MS   = 10       # keep /CS asserted this long (ms)
FRAME_GAP_US = 1500   # end frame if no SCLK for > this (µs)
REST_MS    = 1000     # wait this long between CS pulses (ms)
LED_HOLD_MS = 80      # keep LED lit this long after last activity (ms)
MAX_BITS   = 4096     # safety cap

pi = pigpio.pi()
assert pi.connected, "Start pigpio with: sudo pigpiod"

# Configure pins
pi.set_mode(PIN_CS,   pigpio.OUTPUT); pi.write(PIN_CS, 0)  # idle LOW at GPIO → transistor OFF → /CS HIGH
pi.set_mode(PIN_SCLK, pigpio.INPUT)
pi.set_mode(PIN_DATA, pigpio.INPUT)
pi.set_mode(PIN_LED,  pigpio.OUTPUT); pi.write(PIN_LED, 0)

# Clean up edges (ns)
pi.set_glitch_filter(PIN_SCLK, 50)
pi.set_glitch_filter(PIN_DATA, 50)

bits = []
in_capture = False
last_clk = pi.get_current_tick()
last_activity = 0

def end_frame():
    global bits, in_capture, last_activity
    if not bits:
        return
    # pack MSB-first into bytes
    out = []
    b = 0
    for i, bit in enumerate(bits):
        b = (b << 1) | (bit & 1)
        if (i & 7) == 7:
            out.append(b); b = 0
    if len(bits) & 7:
        out.append(b << (8 - (len(bits) & 7)))

    print(f"{len(bits):4d} bits -> " + " ".join(f"{x:02X}" for x in out))
    bits.clear()
    in_capture = False
    # LED activity
    pi.write(PIN_LED, 1)
    last_activity = pi.get_current_tick()

def on_clk_rise(gpio, level, tick):
    global last_clk, in_capture, bits
    last_clk = tick
    if in_capture:
        bits.append(pi.read(PIN_DATA))
        if len(bits) >= MAX_BITS:
            end_frame()

clk_cb = pi.callback(PIN_SCLK, pigpio.RISING_EDGE, on_clk_rise)

try:
    print("Pulsing /CS via GPIO23; sampling DATA on SCLK↑. Ctrl+C to stop.")
    while True:
        # assert /CS: GPIO23 HIGH → transistor ON → /CS LOW
        bits.clear()
        in_capture = True
        pi.write(PIN_CS, 1)
        time.sleep(PULSE_MS / 1000.0)

        # release /CS: GPIO23 LOW → transistor OFF → /CS HIGH
        pi.write(PIN_CS, 0)

        # wait for frame to finish (quiet gap on SCLK)
        start_wait = pi.get_current_tick()
        while True:
            if bits and pigpio.tickDiff(last_clk, pi.get_current_tick()) > FRAME_GAP_US:
                end_frame()
                break
            if pigpio.tickDiff(start_wait, pi.get_current_tick()) > (FRAME_GAP_US * 10):
                # no clocks seen; abandon
                in_capture = False
                break
            time.sleep(0.0002)

        # auto-extinguish LED after LED_HOLD_MS
        if last_activity and pigpio.tickDiff(last_activity, pi.get_current_tick()) > LED_HOLD_MS * 1000:
            pi.write(PIN_LED, 0)

        # wait before next trigger
        time.sleep(REST_MS / 1000.0)

except KeyboardInterrupt:
    pass
finally:
    clk_cb.cancel()
    pi.write(PIN_LED, 0)
    pi.write(PIN_CS, 0)
    pi.stop()
