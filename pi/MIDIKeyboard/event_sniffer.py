#!/usr/bin/env python3
# event_sniffer.py — no CS. Capture one burst whenever SCLK ticks.

import pigpio, time, sys, statistics as stats

PIN_SCLK = 23
PIN_DATA = 24
WATCHDOG_US = 500   # end frame if no clocks for 20 ms (tweak if needed)
GLITCH_US   = 0       # 0 = no filter; try 1-2 if you see ringing

def pack(bits, msb_first=True):
    out, b = [], 0
    if msb_first:
        for i, bit in enumerate(bits):
            b = (b << 1) | (bit & 1)
            if (i & 7) == 7:
                out.append(b); b = 0
        if len(bits) & 7:
            out.append(b << (8 - (len(bits) & 7)))
    else:
        # LSB-first per byte
        for i, bit in enumerate(bits):
            b |= ((bit & 1) << (i % 8))
            if (i & 7) == 7:
                out.append(b); b = 0
        if len(bits) & 7:
            out.append(b)
    return out

def main():
    pi = pigpio.pi()
    if not pi.connected:
        print("Start pigpio: sudo pigpiod", file=sys.stderr); sys.exit(1)

    for p in (PIN_SCLK, PIN_DATA):
        pi.set_mode(p, pigpio.INPUT)
        pi.set_pull_up_down(p, pigpio.PUD_OFF)
        pi.set_glitch_filter(p, GLITCH_US)

    bits_rise, bits_fall = [], []
    times = []
    capturing = False
    last_tick = None

    def end_frame():
        nonlocal bits_rise, bits_fall, times, capturing
        if not times:
            capturing = False
            return
        dur_us = times[-1] - times[0] if len(times) > 1 else 0
        periods = [t2 - t1 for t1, t2 in zip(times, times[1:])]
        hz = (1_000_000 / stats.mean(periods)) if periods else 0
        def hx(bits, msb): return " ".join(f"{x:02X}" for x in pack(bits, msb_first=msb))
        print(f"\nedges={len(times)}  dur={dur_us/1000:.3f} ms  f≈{hz/1000:.3f} kHz")
        print(" raw bits (rise):", "".join(str(b) for b in bits_rise[:64]), "…" if len(bits_rise)>64 else "")
        print(" raw bits (fall):", "".join(str(b) for b in bits_fall[:64]), "…" if len(bits_fall)>64 else "")
        print(" rise  MSB:", hx(bits_rise, True))
        print(" rise  LSB:", hx(bits_rise, False))
        print(" fall  MSB:", hx(bits_fall, True))
        print(" fall  LSB:", hx(bits_fall, False))
        # reset
        bits_rise.clear(); bits_fall.clear(); times.clear(); capturing=False

    def on_clk(gpio, level, tick):
        nonlocal capturing, last_tick
        if level == 2:             # watchdog timeout => end frame
            if capturing: end_frame()
            return
        if not capturing:
            capturing = True
            bits_rise.clear(); bits_fall.clear(); times.clear()
        # sample both edges so we can decide later
        if level == 1:  # rising
            bits_rise.append(pi.read(PIN_DATA))
        else:           # falling
            bits_fall.append(pi.read(PIN_DATA))
        times.append(tick)
        pi.set_watchdog(PIN_SCLK, WATCHDOG_US)
        last_tick = tick

    cb = pi.callback(PIN_SCLK, pigpio.EITHER_EDGE, on_clk)
    print("Listening for bursts. Press keys, move aftertouch. Ctrl+C to stop.")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        pi.set_watchdog(PIN_SCLK, 0)
        cb.cancel()
        pi.stop()

if __name__ == "__main__":
    main()
