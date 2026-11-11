#!/usr/bin/env python3
# event_zero_mapper.py — no CS. Shows positions and run-lengths of 0-bits.

import pigpio, time, sys, statistics as stats, datetime as dt

SCLK = 23    # BCM
DATA = 24    # BCM
WATCHDOG_US = 800     # frame ends when no SCLK for this long (us)
GLITCH_US   = 0       # don't filter; set 1–2 if ringing

SHOW_BITS = 256       # preview window
LOG = "zero_runs.log"

pi = pigpio.pi()
if not pi.connected:
    print("Start pigpio: sudo pigpiod", file=sys.stderr); sys.exit(1)

for p in (SCLK, DATA):
    pi.set_mode(p, pigpio.INPUT)
    pi.set_pull_up_down(p, pigpio.PUD_OFF)
    pi.set_glitch_filter(p, GLITCH_US)

bits = []
ticks = []
capturing = False

def summarize(bits):
    # indices of zeros and zero run-lengths (value:count tuples)
    zero_idx = [i for i,b in enumerate(bits) if b == 0]
    runs = []
    if bits:
        cur = bits[0]; n = 1
        for b in bits[1:]:
            if b == cur: n += 1
            else:
                runs.append((cur, n)); cur, n = b, 1
        runs.append((cur, n))
    zero_runs = [n for v,n in runs if v == 0]
    one_runs  = [n for v,n in runs if v == 1]
    return zero_idx, zero_runs, one_runs

def pack_msb(bits):
    out, b = [], 0
    for i, bit in enumerate(bits):
        b = (b << 1) | bit
        if (i & 7) == 7:
            out.append(b); b = 0
    if len(bits) & 7:
        out.append(b << (8 - (len(bits) & 7)))
    return out

def end_frame():
    global bits, ticks, capturing
    if not bits:
        capturing = False; return

    # timing
    dur_us = ticks[-1] - ticks[0] if len(ticks) > 1 else 0
    periods = [t2 - t1 for t1,t2 in zip(ticks, ticks[1:])]
    f_khz = (1_000_000 / (sum(periods)/len(periods))) / 1000 if periods else 0

    zero_idx, zero_runs, one_runs = summarize(bits)
    by = pack_msb(bits)
    ts = dt.datetime.now().isoformat(timespec="milliseconds")

    preview = "".join("0" if b==0 else "1" for b in bits[:SHOW_BITS])
    hexline = " ".join(f"{x:02X}" for x in by[:min(32,len(by))])

    print(f"\n[{ts}] edges={len(ticks)}  dur={dur_us/1000:.3f} ms  f≈{f_khz:.3f} kHz")
    print("bits[0:256]:", preview + (" …" if len(bits) > SHOW_BITS else ""))
    print("zero idx   :", zero_idx[:40], ("…" if len(zero_idx)>40 else ""))
    print("zero runs  :", zero_runs[:20], ("…" if len(zero_runs)>20 else ""))
    print("one  runs  :", one_runs[:20], ("…" if len(one_runs)>20 else ""))
    print("hex (MSB)  :", hexline)

    with open(LOG,"a") as f:
        f.write(f"{ts},edges={len(ticks)},dur_ms={dur_us/1000:.3f},"
                f"zeros={len(zero_idx)},zero_runs={zero_runs},one_runs={one_runs}\n")

    bits.clear(); ticks.clear(); capturing=False

def on_clk(gpio, level, tick):
    global capturing
    if level == 2:
        if capturing: end_frame()
        return
    if level != 1:  # sample on rising edge
        return
    if not capturing:
        capturing = True
        bits.clear(); ticks.clear()
    bits.append(pi.read(DATA))
    ticks.append(tick)
    pi.set_watchdog(SCLK, WATCHDOG_US)

cb = pi.callback(SCLK, pigpio.EITHER_EDGE, on_clk)

print(f"Logging zero-run bursts to {LOG}. Press keys / move AT. Ctrl+C to stop.")
try:
    while True: time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    pi.set_watchdog(SCLK, 0); cb.cancel(); pi.stop()
