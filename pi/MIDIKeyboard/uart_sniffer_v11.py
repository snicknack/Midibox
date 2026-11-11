#!/usr/bin/env python3
# v11: Frame-by-token decoder for 38k4 UART keybed bursts with 0xFF token terminators

import serial, time, sys, collections
from statistics import median

PORT = '/dev/serial0'
BAUD = 38400
READ_TIMEOUT = 0.02          # s
GAP_US        = 2500          # new token if byte gap > 2.5 ms
BURST_GAP_MS  = 15            # new burst if token gap > 15 ms
PRINT_UNKNOWN = False

def open_serial():
    return serial.Serial(PORT, BAUD, timeout=READ_TIMEOUT,
                         bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE, xonxoff=False, rtscts=False, dsrdtr=False)

def now_ms():
    return int(time.time()*1000)

def hexs(bs): return ' '.join(f'{b:02X}' for b in bs)

def read_tokens(ser):
    """Yield tokens (bytes objects) split by 0xFF or by large inter-byte gaps."""
    buf = bytearray()
    last_t = time.time()
    while True:
        b = ser.read(1)
        if not b:
            # flush partial token on idle
            if buf:
                yield bytes(buf)
                buf.clear()
            continue
        t = time.time()
        dt_us = (t - last_t) * 1e6
        last_t = t

        # Big gap mid-token? flush previous token
        if buf and dt_us > GAP_US:
            yield bytes(buf)
            buf.clear()

        if b[0] == 0xFF:
            # terminator: emit token if we have content
            if buf:
                yield bytes(buf)
                buf.clear()
            else:
                # stray FF → ignore
                pass
            continue

        buf.append(b[0])

def group_bursts(tokens):
    """Group tokens into bursts by time gap."""
    last_ms = now_ms()
    burst = []
    for tok in tokens:
        t = now_ms()
        if burst and (t - last_ms) > BURST_GAP_MS:
            yield burst
            burst = []
        burst.append((t, tok))
        last_ms = t

def classify_token(tok):
    """Return (type, payload_dict)."""
    if not tok: return ('empty', {})
    b0 = tok[0]

    # Headers
    if len(tok) == 3 and b0 in (0x26, 0x28):
        return ('hdr', {'id': tok[1], 'chk': tok[2]})

    # Footers (observed 06/07 …)
    if b0 in (0x06, 0x07) and len(tok) >= 2:
        return ('ftr', {'bytes': tok})

    # Key index tokens
    if b0 == 0x20:
        # often 1 byte payload (index), sometimes '00' sentinel
        idx = tok[1] if len(tok) >= 2 else None
        return ('keyidx', {'idx': idx})

    # Pressure/AT samples
    if b0 == 0xA0:
        val = tok[1] if len(tok) >= 2 else None
        return ('pressure', {'val': val})

    # Lone noise marker you've seen earlier
    if len(tok) == 1 and tok[0] == 0x30:
        return ('noise', {})

    return ('unknown', {'bytes': tok})

# Simple per-note state
class NoteState:
    def __init__(self):
        self.on = False
        self.last_on_ms = 0
        self.last_off_ms = 0
        self.at = 0

NOTE_OFF_DEBOUNCE_MS  = 40
AT_BLANK_AFTER_ON_MS  = 15
AT_EMA_ALPHA          = 0.35

notes = collections.defaultdict(NoteState)

def smooth_at(prev, new):
    if new is None: return prev
    if prev is None: prev = new
    return int(round(prev + AT_EMA_ALPHA*(new - prev)))

def decode_burst(burst):
    """
    From a burst (list of (t_ms, token)), pick dominant key index and a pressure value.
    Return dict with fields we can print / map later.
    """
    t0 = burst[0][0]
    hdrs, ftrs = [], []
    idx_values = []
    prs_values = []

    unknowns = []

    for t, tok in burst:
        tt, info = classify_token(tok)
        if tt == 'hdr':
            hdrs.append(info)
        elif tt == 'ftr':
            ftrs.append(info)
        elif tt == 'keyidx':
            if info.get('idx') is not None:
                idx_values.append(info['idx'])
        elif tt == 'pressure':
            if info.get('val') is not None:
                prs_values.append(info['val'])
        elif tt == 'noise':
            pass
        else:
            unknowns.append(tok)

    idx_final = None
    prs_final = None

    if idx_values:
        # many repeats in a burst → choose the mode (most frequent)
        ctr = collections.Counter(idx_values)
        idx_final = ctr.most_common(1)[0][0]

    if prs_values:
        # hard-press spikes → use median
        prs_final = int(median(prs_values))

    return {
        't0': t0,
        'hdrs': hdrs,
        'ftrs': ftrs,
        'idx': idx_final,
        'pressure': prs_final,
        'unknowns': unknowns,
        'raw': [tok for _, tok in burst],
    }

def main():
    try:
        ser = open_serial()
    except Exception as e:
        print(f"Serial open failed: {e}")
        sys.exit(1)

    print(f"Listening on {PORT} @ {BAUD} – token FF-delimited, burst gap {BURST_GAP_MS} ms")
    for burst in group_bursts(read_tokens(ser)):
        info = decode_burst(burst)

        idx = info['idx']
        prs = info['pressure']

        # If no key index in this burst, just show header/unknowns briefly
        if idx is None:
            if PRINT_UNKNOWN and info['unknowns']:
                print(f"[{time.strftime('%H:%M:%S')}] BURST (?)  unknown:", ' | '.join(hexs(u) for u in info['unknowns']))
            continue

        # Map index → MIDI note later; for now, just print index & pressure
        note = idx  # temporary 1:1; we’ll build a table once you give me 3–4 anchors
        st = notes[note]

        # Decide ON/OFF based on repetition:
        now = now_ms()
        if not st.on:
            st.on = True
            st.last_on_ms = now
            print(f"ON  idx={idx:3d}  press={prs if prs is not None else '--'}   "
                  f"hdrs={len(info['hdrs'])} toks={len(info['raw'])}")
        else:
            # treat next burst for same idx with very low pressure (or explicit 20 00) as OFF
            if prs is None and (now - st.last_on_ms) > NOTE_OFF_DEBOUNCE_MS:
                st.on = False
                st.last_off_ms = now
                print(f"OFF idx={idx:3d}")
            # Otherwise treat as update (aftertouch/hold)
            elif prs is not None and (now - st.last_on_ms) > AT_BLANK_AFTER_ON_MS:
                st.at = smooth_at(st.at, prs)
                print(f"AT  idx={idx:3d}  {st.at:3d}")

        # Light-touch unknown log (optional)
        if PRINT_UNKNOWN and info['unknowns']:
            print("  unknown:", ' | '.join(hexs(u) for u in info['unknowns']))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
