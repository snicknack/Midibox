#!/usr/bin/env python3
# fast_sniffer_od_fixed.py — open-drain /CS + edge-driven capture (no heavy glitch filter)

import pigpio, time, sys, datetime

PIN_CS   = 22   # open-drain emulation: OUTPUT LOW = assert, INPUT = release
PIN_SCLK = 24   # input: board SCLK
PIN_DATA = 25   # input: board DATA (board->Pi)

SAMPLE_ON_RISING = False
CS_LOW_MS        = 20      # assert time; try 8–20 ms
PERIOD_S         = 2.0     # trigger every 1 s
WATCHDOG_US      = 3000     # frame ends if no SCLK edges for this long
GLITCH_US        = 0        # <<<<< was 50; 0 disables, or try 1–2 us

def pack_bits_to_bytes(bits):
    out, b = [], 0
    for i, bit in enumerate(bits):
        b = (b << 1) | (bit & 1)
        if (i & 7) == 7:
            out.append(b); b = 0
    if len(bits) & 7:
        out.append(b << (8 - (len(bits) & 7)))
    return out

def cs_assert(pi):
    pi.set_mode(PIN_CS, pigpio.OUTPUT)
    pi.write(PIN_CS, 0)   # sink /CS

def cs_release(pi):
    pi.set_mode(PIN_CS, pigpio.INPUT)  # hi-Z, board pull-up releases /CS

def main():
    pi = pigpio.pi()
    if not pi.connected:
        print("Start pigpio: sudo pigpiod", file=sys.stderr); sys.exit(1)

    # Inputs
    for p in (PIN_SCLK, PIN_DATA):
        pi.set_mode(p, pigpio.INPUT)
        pi.set_pull_up_down(p, pigpio.PUD_OFF)
        pi.set_glitch_filter(p, GLITCH_US)   # <<<<< no heavy filtering

    cs_release(pi)

    bits = []
    capturing = False
    clk_edges_this_frame = 0

    def end_frame():
        nonlocal bits, capturing, clk_edges_this_frame
        if not bits:
            capturing = False
            clk_edges_this_frame = 0
            return
        by = pack_bits_to_bytes(bits)
        toggles = sum(1 for a,b in zip(bits, bits[1:]) if a!=b)
        ts = datetime.datetime.now().isoformat(timespec="milliseconds")
        print(f"[{ts}] edges={clk_edges_this_frame:4d}, bits={len(bits):4d}, "
              f"bytes={len(by):3d}, toggles={toggles:4d} -> "
              + " ".join(f"{x:02X}" for x in by))
        bits.clear()
        capturing = False
        clk_edges_this_frame = 0

    def on_clk(gpio, level, tick):
        nonlocal capturing, clk_edges_this_frame
        if level == 2:                      # watchdog timeout
            if capturing: end_frame()
            return
        clk_edges_this_frame += 1
        want = 1 if SAMPLE_ON_RISING else 0
        if capturing and level == want:
            bits.append(pi.read(PIN_DATA))
            pi.set_watchdog(PIN_SCLK, WATCHDOG_US)

    cb = pi.callback(PIN_SCLK, pigpio.EITHER_EDGE, on_clk)

    try:
        print("Sniffer running (open-drain CS, no heavy filter). Ctrl+C to stop.")
        while True:
            bits.clear(); capturing = True
            pi.set_watchdog(PIN_SCLK, WATCHDOG_US)

            cs_assert(pi)
            time.sleep(CS_LOW_MS/1000.0)
            cs_release(pi)

            time.sleep(PERIOD_S)
    except KeyboardInterrupt:
        pass
    finally:
        pi.set_watchdog(PIN_SCLK, 0)
        cb.cancel()
        cs_release(pi)
        pi.stop()

if __name__ == "__main__":
    main()
