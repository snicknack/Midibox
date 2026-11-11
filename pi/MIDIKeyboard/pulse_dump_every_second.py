#!/usr/bin/env python3
"""
Pulses /CS once per second, samples DATA on each SCLK edge,
packs bits into bytes, prints summary, and logs frames to a file.

Assumes:
  PIN_CS   = 22 (BCM)  -> drives NPN/MOSFET to pull /CS low (active)
  PIN_SCLK = 23 (BCM)  -> input from board SCLK
  PIN_DATA = 24 (BCM)  -> input from board DATA (board->Pi)
"""

import pigpio, time, sys, datetime

# === Pins (BCM) ===
PIN_CS   = 22
PIN_SCLK = 23
PIN_DATA = 24

# === Tunables ===
SAMPLE_ON_RISING = True   # False => sample on falling edges
WATCHDOG_US      = 3000   # end frame if no SCLK edges for this long
CS_LOW_MS        = 24     # keep /CS asserted long enough for the burst
PERIOD_S         = 0.5    # pulse once per second
LOG_PATH         = "frames_log.txt"

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

    # Configure pins
    for p in (PIN_SCLK, PIN_DATA):
        pi.set_mode(p, pigpio.INPUT)
        pi.set_pull_up_down(p, pigpio.PUD_OFF)
        pi.set_glitch_filter(p, 50)  # tame ringing / bounce

    pi.set_mode(PIN_CS, pigpio.OUTPUT)
    pi.write(PIN_CS, 1)             # idle HIGH (inactive)

    bits = []
    capturing = False

    def end_frame():
        nonlocal bits, capturing
        if not bits:
            capturing = False
            return
        by = pack_bits_to_bytes(bits)
        transitions = sum(1 for a, b in zip(bits, bits[1:]) if a != b)
        ts = datetime.datetime.now().isoformat(timespec="milliseconds")
        hexline = " ".join(f"{x:02X}" for x in by)
        summary = f"[{ts}] {len(bits):4d} bits, {len(by):3d} bytes, {transitions:4d} toggles -> {hexline}"
        print(summary)
        with open(LOG_PATH, "a") as f:
            f.write(summary + "\n")
        bits.clear()
        capturing = False

    def on_clk(gpio, level, tick):
        # level 0=falling, 1=rising, 2=watchdog timeout
        nonlocal capturing
        if level == 2:
            if capturing:
                end_frame()
            return
        want = 1 if SAMPLE_ON_RISING else 0
        if capturing and level == want:
            bits.append(pi.read(PIN_DATA))
            pi.set_watchdog(PIN_SCLK, WATCHDOG_US)

    cb = pi.callback(PIN_SCLK, pigpio.EITHER_EDGE, on_clk)

    print(f"Logging to {LOG_PATH}")
    print("Pulsing /CS every 1 s; sampling on SCLK. Ctrl+C to stop.")
    try:
        while True:
            # Arm capture BEFORE asserting /CS so we don't miss first clocks
            bits.clear()
            capturing = True
            pi.set_watchdog(PIN_SCLK, WATCHDOG_US)

            # Assert /CS (active-LOW) for CS_LOW_MS
            pi.write(PIN_CS, 0)
            time.sleep(CS_LOW_MS / 1000.0)
            pi.write(PIN_CS, 1)

            # Give watchdog time to end the frame if clocks continue briefly
            time.sleep(PERIOD_S)
    except KeyboardInterrupt:
        pass
    finally:
        pi.set_watchdog(PIN_SCLK, 0)
        cb.cancel()
        pi.stop()

if __name__ == "__main__":
    main()
