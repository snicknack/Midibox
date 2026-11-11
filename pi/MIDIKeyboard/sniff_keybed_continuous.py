#!/usr/bin/env python3
# sniff_keybed_continuous.py
# Capture STM32 keybed output (continuous serial bursts via SCLK + MOSI)

import pigpio, time, datetime, sys

PIN_SCLK = 23
PIN_MOSI = 24
SAMPLE_ON_RISING = True
WATCHDOG_US = 5000   # defines frame gap (no clock for 2 ms -> new frame)

def pack_bits_to_bytes(bits):
    out, b = [], 0
    for i, bit in enumerate(bits):
        b = (b << 1) | (bit & 1)
        if (i & 7) == 7:
            out.append(b)
            b = 0
    if len(bits) % 8:
        out.append(b << (8 - (len(bits) % 8)))
    return out

def main():
    pi = pigpio.pi()
    if not pi.connected:
        print("Start pigpio with: sudo pigpiod", file=sys.stderr)
        sys.exit(1)

    for p in (PIN_SCLK, PIN_MOSI):
        pi.set_mode(p, pigpio.INPUT)
        pi.set_pull_up_down(p, pigpio.PUD_OFF)
        pi.set_glitch_filter(p, 1)  # very short filter

    bits = []
    capturing = False
    clk_edges = 0

    def end_frame():
        nonlocal bits, capturing, clk_edges
        if not bits:
            capturing = False
            return
        data = pack_bits_to_bytes(bits)
        ts = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{ts}] {len(bits):4d} bits, {len(data):3d} bytes -> "
              + " ".join(f"{x:02X}" for x in data))
        bits.clear()
        capturing = False
        clk_edges = 0

    def on_clk(gpio, level, tick):
        nonlocal capturing, clk_edges
        if level == 2:  # watchdog timeout: end of burst
            if capturing:
                end_frame()
            return

        if not capturing:
            capturing = True
            bits.clear()
            clk_edges = 0

        want = 1 if SAMPLE_ON_RISING else 0
        if level == want:
            bits.append(pi.read(PIN_MOSI))
            clk_edges += 1
            pi.set_watchdog(PIN_SCLK, WATCHDOG_US)

    cb = pi.callback(PIN_SCLK, pigpio.EITHER_EDGE, on_clk)

    print("Listening for bursts... (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        pi.set_watchdog(PIN_SCLK, 0)
        cb.cancel()
        pi.stop()

if __name__ == "__main__":
    main()
