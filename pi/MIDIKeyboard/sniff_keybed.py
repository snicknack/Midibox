#!/usr/bin/env python3
# Sniffs an external, board-generated SCLK and samples DATA (MOSI) on each rising edge.
# Segments frames either by a SYNC pin edge or by a quiet gap on SCLK.

import pigpio, time

# === BCM pins ===
PIN_SCLK = 24   # input: board SCLK
PIN_DATA = 25   # input: board MOSI (data out)
PIN_SYNC = 22   # input: board SYNC/enable (optional; set to None if unused)

# Frame segmentation settings
USE_SYNC      = False       # set False if you don't have the sync wire
SYNC_ACTIVE   = 1          # try 0 (active-low), if wrong try 1
GAP_US        = 2000       # no SCLK for > this → end frame (tune: 800–3000 us)
MAX_BITS      = 100000       # safety cap

pi = pigpio.pi()
assert pi.connected, "pigpio daemon not running (sudo pigpiod)."

# Configure inputs, light glitch filter to tame ringing
for pin in [PIN_SCLK, PIN_DATA] + ([] if PIN_SYNC is None else [PIN_SYNC]):
    pi.set_mode(pin, pigpio.INPUT)
    pi.set_pull_up_down(pin, pigpio.PUD_OFF)
pi.set_glitch_filter(PIN_SCLK, 50)
pi.set_glitch_filter(PIN_DATA, 50)
if PIN_SYNC is not None:
    pi.set_glitch_filter(PIN_SYNC, 50)

bits = []
in_frame = False
last_clk = pi.get_current_tick()

def end_frame():
    global bits, in_frame
    if not bits:
        return
    # pack MSB-first into bytes
    out = []
    b = 0
    for i, bit in enumerate(bits):
        b = (b << 1) | (bit & 1)
        if (i & 7) == 7:
            out.append(b)
            b = 0
    if len(bits) & 7:
        out.append(b << (8 - (len(bits) & 7)))

    print(f"{len(bits):4d} bits  ->", " ".join(f"{x:02X}" for x in out))
    bits.clear()
    in_frame = False

def on_clk_rise(gpio, level, tick):
    global last_clk, bits, in_frame
    last_clk = tick
    if not in_frame:
        return
    bits.append(pi.read(PIN_DATA))
    if len(bits) >= MAX_BITS:
        end_frame()

def on_sync_edge(gpio, level, tick):
    # Start/end frames based on SYNC level
    global in_frame, bits
    active = (level == SYNC_ACTIVE)
    if active:
        # starting a frame
        bits.clear()
        in_frame = True
    else:
        # ending a frame
        end_frame()

clk_cb  = pi.callback(PIN_SCLK, pigpio.RISING_EDGE, on_clk_rise)

if USE_SYNC and PIN_SYNC is not None:
    sync_cb = pi.callback(PIN_SYNC, pigpio.EITHER_EDGE, on_sync_edge)
    print("Sniffer running (SYNC-gated). Press Ctrl+C to stop.")
else:
    sync_cb = None
    print("Sniffer running (gap-gated). Press Ctrl+C to stop.")

try:
    while True:
        if not USE_SYNC:
            # end a frame if SCLK has been quiet long enough
            if bits:
                if pigpio.tickDiff(last_clk, pi.get_current_tick()) > GAP_US:
                    end_frame()
            else:
                # auto-start on first clock edge after a gap
                if pigpio.tickDiff(last_clk, pi.get_current_tick()) <= GAP_US:
                    # we’re seeing clocks → start capturing
                    bits.clear()
                    in_frame = True
        time.sleep(0.001)
except KeyboardInterrupt:
    pass
finally:
    clk_cb.cancel()
    if sync_cb: sync_cb.cancel()
    pi.stop()
