#!/usr/bin/env python3
# Pulse CS (active-LOW) to trigger a frame, sample DATA on each rising SCLK, print hex.

import pigpio, time

PIN_SCLK = 23   # input: board clock out
PIN_DATA = 24   # input: board data out
PIN_CS   = 25   # output: CS/enable to board (active-LOW)

# Tuning
GAP_US   = 1500     # end frame if no SCLK for > this (adjust 800–3000)
PULSE_US = 10000    # CS low time in microseconds (adjust as needed)
REST_MS  = 10       # delay between frames

pi = pigpio.pi()
assert pi.connected, "Start with: sudo pigpiod"

# Configure pins
pi.set_mode(PIN_SCLK, pigpio.INPUT)
pi.set_mode(PIN_DATA, pigpio.INPUT)
pi.set_mode(PIN_CS,   pigpio.OUTPUT)
pi.set_pull_up_down(PIN_SCLK, pigpio.PUD_OFF)
pi.set_pull_up_down(PIN_DATA, pigpio.PUD_OFF)
pi.write(PIN_CS, 1)  # idle HIGH (inactive)

# Clean edges
pi.set_glitch_filter(PIN_SCLK, 50)
pi.set_glitch_filter(PIN_DATA, 50)

bits = []
last_clk = pi.get_current_tick()
in_capture = False

def end_frame():
    global bits, in_capture
    if not bits:
        return
    # Pack MSB-first into bytes
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

def on_clk_rise(gpio, level, tick):
    global last_clk, bits, in_capture
    last_clk = tick
    if in_capture:
        bits.append(pi.read(PIN_DATA))

clk_cb = pi.callback(PIN_SCLK, pigpio.RISING_EDGE, on_clk_rise)

try:
    print("Pulsing CS low; sampling on each SCLK↑. Ctrl+C to stop.")
    while True:
        # Start a new capture
        bits.clear()
        in_capture = True

        # Assert CS (active-LOW), hold for PULSE_US
        pi.write(PIN_CS, 0)
        time.sleep(PULSE_US / 1_000_000.0)
        pi.write(PIN_CS, 1)

        # Wait for the frame to end (quiet gap on SCLK)
        start_wait = pi.get_current_tick()
        while True:
            if pigpio.tickDiff(last_clk, pi.get_current_tick()) > GAP_US:
                break
            # safety: don’t wait forever if nothing clocks
            if pigpio.tickDiff(start_wait, pi.get_current_tick()) > (GAP_US * 10):
                break
            time.sleep(0.0002)

        end_frame()
        time.sleep(REST_MS / 1000.0)

except KeyboardInterrupt:
    pass
finally:
    clk_cb.cancel()
    pi.stop()
