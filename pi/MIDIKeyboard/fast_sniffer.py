#!/usr/bin/env python3
# Pulses /CS low, samples DATA on each SCLK edge, prints hex bytes per frame.

import pigpio, time, sys

# ==== Pins (BCM) ====
PIN_SCLK = 23      # input: board SCLK
PIN_DATA = 25      # input: board DATA (board->Pi)
PIN_CS   = 22      # output: drives 2N3904 to pull /CS low (active)

# ==== Tunables ====
SAMPLE_ON_RISING = False     # False = sample on falling edges
WATCHDOG_US      = 2500     # end frame if no SCLK edges for this long
CS_LOW_MS        = 100       # keep /CS low long enough to cover the burst
INTER_FRAME_MS   = 500       # pause between triggers

def pack_bits_to_bytes(bits):
    out, b = [], 0
    for i, bit in enumerate(bits):
        b = (b << 1) | (bit & 1)
        if (i & 7) == 7:
            out.append(b); b = 0
    if len(bits) & 7:
        out.append(b << (8 - (len(bits) & 7)))
    return out

def main():
    pi = pigpio.pi()
    if not pi.connected:
        print("pigpio daemon not running. Start with: sudo pigpiod", file=sys.stderr)
        sys.exit(1)

    # Inputs
    for p in (PIN_SCLK, PIN_DATA):
        pi.set_mode(p, pigpio.INPUT)
        pi.set_pull_up_down(p, pigpio.PUD_OFF)
        pi.set_glitch_filter(p, 50)   # tame ringing

    # /CS output (idle HIGH)
    pi.set_mode(PIN_CS, pigpio.OUTPUT)
    pi.write(PIN_CS, 1)

    bits = []
    capturing = False

    def end_frame():
        nonlocal bits, capturing
        if not bits:
            capturing = False
            return
        by = pack_bits_to_bytes(bits)
        print(f"{len(bits):4d} bits -> " + " ".join(f"{x:02X}" for x in by))
        bits.clear()
        capturing = False

    def on_clk(gpio, level, tick):
        # level: 0=falling, 1=rising, 2=watchdog timeout
        nonlocal capturing
        if level == 2:
            if capturing:
                end_frame()
            return
        want = 1 if SAMPLE_ON_RISING else 0
        if capturing and level == want:
            bits.append(pi.read(PIN_DATA))
            # refresh watchdog while clocks arrive
            pi.set_watchdog(PIN_SCLK, WATCHDOG_US)

    cb = pi.callback(PIN_SCLK, pigpio.EITHER_EDGE, on_clk)

    try:
        print("Sniffer running. Pulsing /CS low; sampling on SCLK. Ctrl+C to stop.")
        while True:
            # arm capture BEFORE asserting /CS so we don’t miss first bits
            bits.clear()
            capturing = True
            pi.set_watchdog(PIN_SCLK, WATCHDOG_US)

            # assert /CS (active LOW) long enough for entire burst
            pi.write(PIN_CS, 0)
            time.sleep(CS_LOW_MS / 1000.0)
            pi.write(PIN_CS, 1)

            # let watchdog close the frame; small idle before next trigger
            time.sleep(INTER_FRAME_MS / 1000.0)

    except KeyboardInterrupt:
        pass
    finally:
        pi.set_watchdog(PIN_SCLK, 0)
        cb.cancel()
        pi.stop()

if __name__ == "__main__":
    main()
