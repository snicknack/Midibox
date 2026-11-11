#!/usr/bin/env python3
# Open-drain /CS + edge-driven SCLK sniffer (pigpio)

import pigpio, time, sys, datetime

PIN_CS   = 22   # open-drain emulated on this GPIO
PIN_SCLK = 23   # input: board SCLK
PIN_DATA = 24   # input: board DATA (board->Pi)

SAMPLE_ON_RISING = False   # flip to False if bytes look wrong
CS_LOW_MS        = 100     # keep /CS asserted this long
PERIOD_S         = 1    # pulse period (once per second)
WATCHDOG_US      = 3000   # end frame if no SCLK edges for this long

def pack_bits_to_bytes(bits):
    out, b = [], 0
    for i, bit in enumerate(bits):
        b = (b << 1) | (bit & 1)        # MSB-first
        if (i & 7) == 7:
            out.append(b); b = 0
    if len(bits) & 7:
        out.append(b << (8 - (len(bits) & 7)))
    return out

def cs_assert(pi):
    # emulate open-drain: OUTPUT LOW sinks CS
    pi.set_mode(PIN_CS, pigpio.OUTPUT)
    pi.write(PIN_CS, 0)

def cs_release(pi):
    # emulate open-drain: INPUT = Hi-Z, board pull-up releases CS
    pi.set_mode(PIN_CS, pigpio.INPUT)

def main():
    pi = pigpio.pi()
    if not pi.connected:
        print("Start pigpio: sudo pigpiod", file=sys.stderr); sys.exit(1)

    # inputs
    for p in (PIN_SCLK, PIN_DATA):
        pi.set_mode(p, pigpio.INPUT)
        pi.set_pull_up_down(p, pigpio.PUD_OFF)
        pi.set_glitch_filter(p, 50)  # tame ringing

    cs_release(pi)  # idle released

    bits = []
    capturing = False

    def end_frame():
        nonlocal bits, capturing
        if not bits:
            capturing = False; return
        by = pack_bits_to_bytes(bits)
        toggles = sum(1 for a,b in zip(bits, bits[1:]) if a!=b)
        ts = datetime.datetime.now().isoformat(timespec="milliseconds")
        print(f"[{ts}] {len(bits):4d} bits, {len(by):3d} bytes, {toggles:4d} toggles -> "
              + " ".join(f"{x:02X}" for x in by))
        bits.clear(); capturing = False

    def on_clk(gpio, level, tick):
        # 0=falling, 1=rising, 2=watchdog timeout
        nonlocal capturing
        if level == 2:
            if capturing: end_frame()
            return
        want = 1 if SAMPLE_ON_RISING else 0
        if capturing and level == want:
            bits.append(pi.read(PIN_DATA))
            pi.set_watchdog(PIN_SCLK, WATCHDOG_US)

    cb = pi.callback(PIN_SCLK, pigpio.EITHER_EDGE, on_clk)

    try:
        print("Sniffer running (open-drain CS). Ctrl+C to stop.")
        while True:
            # arm capture BEFORE asserting CS
            bits.clear(); capturing = True
            pi.set_watchdog(PIN_SCLK, WATCHDOG_US)

            cs_assert(pi)                          # CS low
            time.sleep(CS_LOW_MS/1000.0)
            cs_release(pi)                         # release

            time.sleep(PERIOD_S)                   # next pulse
    except KeyboardInterrupt:
        pass
    finally:
        pi.set_watchdog(PIN_SCLK, 0)
        cb.cancel()
        cs_release(pi)
        pi.stop()

if __name__ == "__main__":
    main()
