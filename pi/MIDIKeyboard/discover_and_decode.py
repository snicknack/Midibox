#!/usr/bin/env python3
import pigpio, time, sys, json, argparse, statistics as stats
from collections import Counter, defaultdict
from pathlib import Path

# -------- pins (BCM) --------
SCLK = 23
DATA = 24

# -------- burst split / filtering --------
WATCHDOG_US = 8000     # end burst if no clocks for 0.8 ms
GLITCH_US   = 0       # 0 or 1–2 if you see ringing
PREVIEW_BITS = 128

MAP_PATH = Path("pitch_map.json")

# ===== utilities =====
def pack_msb(bits):
    out, b = [], 0
    for i, bit in enumerate(bits):
        b = (b << 1) | (bit & 1)
        if (i & 7) == 7:
            out.append(b); b = 0
    if len(bits) & 7:
        out.append(b << (8 - (len(bits) & 7)))
    return out

def first_zero_index(bits):
    for i, b in enumerate(bits):
        if b == 0:
            return i
    return None

def zero_runs(bits):
    runs = []
    if not bits: return runs
    cur = bits[0]; n = 1
    for b in bits[1:]:
        if b == cur: n += 1
        else:
            runs.append((cur, n)); cur, n = b, 1
    runs.append((cur, n))
    return runs

def simple_velocity(bits):
    """
    Heuristic velocity: count zeros in first 64 bits + weight longest zero run
    near the start. Returns 0..127.
    """
    head = bits[:64]
    zc = sum(1 for b in head if b == 0)
    zr = max([n for v, n in zero_runs(head) if v == 0] + [0])
    raw = 6*zc + 10*zr
    return max(1, min(127, raw))

# ===== pigpio burst capture (no CS) =====
class BurstSniffer:
    def __init__(self, sclk=SCLK, data=DATA):
        self.pi = pigpio.pi()
        if not self.pi.connected:
            print("Start pigpio: sudo pigpiod", file=sys.stderr); sys.exit(1)
        for p in (sclk, data):
            self.pi.set_mode(p, pigpio.INPUT)
            self.pi.set_pull_up_down(p, pigpio.PUD_OFF)
            self.pi.set_glitch_filter(p, GLITCH_US)
        self.sclk = sclk
        self.data = data
        self.bits = []
        self.ticks = []
        self.capturing = False
        self.cb = self.pi.callback(self.sclk, pigpio.EITHER_EDGE, self._on_clk)

    def _on_clk(self, gpio, level, tick):
        if level == 2:  # watchdog
            if self.capturing and self.on_burst:
                self.on_burst(self.bits[:], self.ticks[:])
            self.bits.clear(); self.ticks.clear(); self.capturing = False
            return
        if level != 1:   # sample on rising
            return
        if not self.capturing:
            self.capturing = True
            self.bits.clear(); self.ticks.clear()
        self.bits.append(self.pi.read(self.data))
        self.ticks.append(tick)
        self.pi.set_watchdog(self.sclk, WATCHDOG_US)

    def loop(self, on_burst):
        self.on_burst = on_burst
        print("Listening for bursts… (Ctrl+C to stop)")
        try:
            while True: time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self.pi.set_watchdog(self.sclk, 0)
            self.cb.cancel()
            self.pi.stop()

# ===== learning: build mapping key -> {index/signature} =====
def learn_mapping():
    mapping = {}
    if MAP_PATH.exists():
        mapping = json.loads(MAP_PATH.read_text())

    sniffer = BurstSniffer()
    bucket = defaultdict(list)

    def on_burst(bits, ticks):
        idx = first_zero_index(bits)
        if idx is None:
            return
        # small signature: first zero index + next 8 bits (helps disambiguate)
        tail = bits[idx:idx+8]
        sig_byte = 0
        for b in tail:
            sig_byte = (sig_byte << 1) | b
        bucket[idx].append(sig_byte)
        by = pack_msb(bits)
        print(f"  burst: edges={len(ticks):4d} idx0={idx:4d} sig={sig_byte:02X} hex={ ' '.join(f'{x:02X}' for x in by[:8]) }")

    print("\nLEARN MODE")
    print("Type a MIDI note number (e.g., 48 for C3), then press that key 5–10 times.\n"
          "Empty line to finish & save.\n")

    while True:
        note = input("MIDI note (empty to finish): ").strip()
        if not note:
            break
        try:
            note_num = int(note)
        except ValueError:
            print("Enter an integer MIDI note (0..127)."); continue

        bucket.clear()
        print("Press the key now… (Ctrl+C to abort this key)")
        try:
            sniffer.loop(on_burst)
        except KeyboardInterrupt:
            pass

        if not bucket:
            print("No bursts captured; try again.")
            continue

        # Choose dominant first-zero index and most common signature at that index
        idx_counts = Counter({k: len(v) for k, v in bucket.items()})
        idx0, _ = idx_counts.most_common(1)[0]
        sig_counts = Counter(bucket[idx0])
        sig0, _ = sig_counts.most_common(1)[0]
        mapping[str(note_num)] = {"zindex": idx0, "sig": sig0}
        print(f"Saved: note {note_num} -> zindex {idx0}, sig {sig0:02X}\n")

    MAP_PATH.write_text(json.dumps(mapping, indent=2))
    print(f"\nMapping saved to {MAP_PATH}:\n{json.dumps(mapping, indent=2)}")

# ===== running: decode using learned mapping =====
def run_decoder():
    if not MAP_PATH.exists():
        print("No pitch_map.json found. Run with --learn first.", file=sys.stderr)
        sys.exit(1)
    mapping = json.loads(MAP_PATH.read_text())
    # Build reverse lookup by nearest zindex (in case of small drift)
    rev = { int(v["zindex"]): int(k) for k, v in mapping.items() }

    # per-note state
    state = { int(k): {"down": False, "last_at": 0, "t_last": 0.0} for k in mapping.keys() }

    def nearest_note(idx):
        if not rev: return None
        nearest = min(rev.keys(), key=lambda k: abs(k - idx))
        # sanity: require proximity ≤ 6 bits (tweak if needed)
        if abs(nearest - idx) <= 6:
            return rev[nearest]
        return None

    sniffer = BurstSniffer()

    def on_burst(bits, ticks):
        if not ticks: return
        idx0 = first_zero_index(bits)
        if idx0 is None:
            return
        note = nearest_note(idx0)
        if note is None:
            # print unknowns so you can extend the map later
            by = pack_msb(bits)
            print(f"?? idx0={idx0}  hex={ ' '.join(f'{x:02X}' for x in by[:8]) }")
            return

        # pressed/released heuristic:
        # treat presence of at least one 0 in first 64 bits as "pressed"
        pressed = any(b == 0 for b in bits[:64])

        # aftertouch estimate + velocity heuristic
        at_val = min(127, simple_velocity(bits))   # reuse as AT proxy initially
        vel    = min(127, max(1, simple_velocity(bits)))  # same proxy for now

        st = state[note]
        tnow = time.time()
        if pressed and not st["down"]:
            st["down"] = True
            st["last_at"] = at_val
            st["t_last"] = tnow
            print(f"note_on {note} vel={vel}")
        elif pressed and st["down"]:
            # aftertouch rate limit
            if abs(at_val - st["last_at"]) >= 3 and (tnow - st["t_last"]) >= 0.010:
                st["last_at"] = at_val
                st["t_last"] = tnow
                print(f"aftertouch {note} val={at_val}")
        else:
            if st["down"]:
                st["down"] = False
                print(f"note_off {note}")

    sniffer.loop(on_burst)

# ===== main =====
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--learn", action="store_true", help="learn key -> first-zero index mapping")
    ap.add_argument("--run",   action="store_true", help="decode using saved mapping")
    args = ap.parse_args()

    if args.learn:
        learn_mapping()
    elif args.run:
        run_decoder()
    else:
        print("Use --learn to build the map, then --run to decode.")
