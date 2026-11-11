#!/usr/bin/env python3
"""
sniff_and_decode.py
- Watches SCLK (GPIO23) and DATA (GPIO24) from the keybed board.
- Splits activity into bursts using a watchdog gap.
- Prints burst stats + hex preview.
- Feeds each burst to a per-key state machine (decoder layer).
"""

import pigpio, time, sys, datetime, statistics as stats

# ======== CONFIG (BCM numbering) ========
PIN_SCLK = 23        # input: keybed clock
PIN_DATA = 24        # input: keybed data (active-high line with brief lows)
WATCHDOG_US = 800    # new frame if no SCLK edges for this many microseconds
GLITCH_US   = 0      # leave 0 (or try 1–2 if you see ringing)
SHOW_BYTES  = 16     # hex preview bytes per burst
NUM_KEYS    = 88     # SL88 key count

# ======== UTIL ========
def now_s(): return time.time()

def pack_bits_msb(bits):
    """Pack bits (MSB-first within each byte) into a list of bytes."""
    out, b = [], 0
    for i, bit in enumerate(bits):
        b = (b << 1) | (bit & 1)
        if (i & 7) == 7:
            out.append(b); b = 0
    if len(bits) & 7:
        out.append(b << (8 - (len(bits) & 7)))
    return out

# ======== DECODER LAYER (skeleton – fill the TODOs) ========
class KeyState:
    def __init__(self):
        self.state = "UP"        # UP, DOWN, HOLD
        self.at_raw = 0
        self.at_filt = 0.0
        self.last_sent_at = 0
        self.last_event_t = 0.0
        self.velocity = 0

KEYS = [KeyState() for _ in range(NUM_KEYS)]

# Tunables for aftertouch smoothing / hysteresis
AT_DEADBAND = 3          # ignore tiny AT changes
AT_ALPHA = 0.25          # smoothing factor (0..1)
AT_MIN_INTERVAL = 0.010  # minimum seconds between AT sends
AT_ON_THRESH = 5         # treat AT >= this as "pressed"
AT_OFF_THRESH = 3        # treat AT <= this as "released"
OFF_HOLD_MS = 15         # require AT below OFF thresh for this long (ms)

# Simple off-timer bucket per key (debounce for release)
_off_until = [0.0] * NUM_KEYS

def decode_key_and_at(bits):
    """
    TODO: Replace with the real mapping once we finish reverse-engineering.
    Should return:
        (key_index:int 0..87, is_pressed:bool, at_value:int 0..127)
    For now we return (None, None, None) so the skeleton runs without errors.
    """
    return (None, None, None)

def estimate_velocity(bits):
    """
    TODO: Replace with velocity extraction logic (0..127).
    For now returns a constant placeholder for demonstration.
    """
    return 64

def emit(msg):
    """Print decoded events (later you can swap for MIDI send)."""
    print(msg)

def process_event(bits, t_s):
    """Call after each burst. Updates per-key state and emits events."""
    key_idx, pressed, at_val = decode_key_and_at(bits)
    if key_idx is None:
        return  # unknown/unmapped burst; ignore for now

    if at_val is None:
        at_val = 0
    if at_val < 0: at_val = 0
    if at_val > 127: at_val = 127

    ks = KEYS[key_idx]
    ks.at_raw = at_val
    ks.at_filt = ks.at_filt + AT_ALPHA * (ks.at_raw - ks.at_filt)

    # --- Note-on path ---
    if pressed:
        if ks.state == "UP":
            ks.state = "DOWN"
            ks.velocity = estimate_velocity(bits)
            emit(f"note_on key={key_idx} vel={ks.velocity}")
            ks.state = "HOLD"
            _off_until[key_idx] = 0.0  # cancel any pending off
        # Aftertouch emit rule
        if abs(int(ks.at_filt) - ks.last_sent_at) >= AT_DEADBAND and (t_s - ks.last_event_t) >= AT_MIN_INTERVAL:
            ks.last_sent_at = int(ks.at_filt)
            emit(f"aftertouch key={key_idx} val={ks.last_sent_at}")
            ks.last_event_t = t_s
    else:
        # Candidate for note-off if AT is low and stays low long enough
        if ks.state != "UP":
            if ks.at_raw <= AT_OFF_THRESH:
                if _off_until[key_idx] == 0.0:
                    _off_until[key_idx] = t_s + (OFF_HOLD_MS / 1000.0)
                if t_s >= _off_until[key_idx]:
                    emit(f"note_off key={key_idx}")
                    ks.state = "UP"
                    ks.at_filt = 0.0
                    ks.last_sent_at = 0
                    ks.last_event_t = t_s
            else:
                _off_until[key_idx] = 0.0  # still above threshold; keep holding

# ======== SNIFFER (no CS) ========
def main():
    pi = pigpio.pi()
    if not pi.connected:
        print("Start pigpio with: sudo pigpiod", file=sys.stderr)
        sys.exit(1)

    # Inputs
    for p in (PIN_SCLK, PIN_DATA):
        pi.set_mode(p, pigpio.INPUT)
        pi.set_pull_up_down(p, pigpio.PUD_OFF)
        pi.set_glitch_filter(p, GLITCH_US)

    bits = []
    ticks = []
    capturing = False

    def end_frame():
        nonlocal bits, ticks, capturing
        if not ticks:
            capturing = False
            return

        # timing summary
        dur_us = ticks[-1] - ticks[0] if len(ticks) > 1 else 0
        periods = [t2 - t1 for t1, t2 in zip(ticks, ticks[1:])]
        f_khz = (1_000_000 / (sum(periods)/len(periods))) / 1000 if periods else 0

        by = pack_bits_msb(bits)
        ts = datetime.datetime.now().isoformat(timespec="milliseconds")

        # quick preview
        hex_preview = " ".join(f"{x:02X}" for x in by[:SHOW_BYTES])
        print(f"[{ts}] edges={len(ticks):4d}  dur={dur_us/1000:.3f} ms  f≈{f_khz:.3f} kHz  ->  {hex_preview}")

        # hand to decoder
        process_event(bits, now_s())

        # reset
        bits.clear(); ticks.clear(); capturing = False

    def on_clk(gpio, level, tick):
        nonlocal capturing
        if level == 2:                 # watchdog timeout -> end burst
            if capturing:
                end_frame()
            return
        if level != 1:                 # sample on rising edge
            return
        if not capturing:
            capturing = True
            bits.clear(); ticks.clear()
        bits.append(pi.read(PIN_DATA))
        ticks.append(tick)
        pi.set_watchdog(PIN_SCLK, WATCHDOG_US)

    cb = pi.callback(PIN_SCLK, pigpio.EITHER_EDGE, on_clk)

    print("Listening for bursts… (Ctrl+C to stop)")
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
