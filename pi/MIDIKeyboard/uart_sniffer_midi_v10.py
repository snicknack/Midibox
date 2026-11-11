#!/usr/bin/env python3
# uart_sniffer_midi_v10.py
# Robust burst-framed UART reader @38400 with aftertouch spike filtering.

import serial, time, csv, sys, collections
from dataclasses import dataclass

PORT         = '/dev/serial0'
BAUD         = 38400
READ_TIMEOUT = 0.02      # seconds
GAP_US       = 2500      # inter-byte gap to start a new packet (µs)
DROP_LONE_30 = True      # drop solitary 0x30 packets
CSV_FILE     = 'keybed_midi_v10.csv'
UNK_FILE     = 'unknown_v10.txt'

# Event tuning
NOTE_OFF_DEBOUNCE_MS    = 60     # per-key minimum time before we accept OFF
AT_IGNORE_AFTER_ON_MS   = 15     # ignore AT updates right after note-on
AT_EMA_ALPHA            = 0.35   # EMA weight after median-of-3
AT_SLEW_MAX_PER_MS      = 6      # max AT delta per ms (slew limit)
AT_MIN, AT_MAX          = 0, 127

@dataclass
class KeyState:
    is_on: bool = False
    last_on_ms: float = 0.0
    last_off_ms: float = 0.0
    at_val: int = 0

def now_ms() -> float:
    return time.time() * 1000.0

def hexs(bs: bytes) -> str:
    return ' '.join(f'{b:02X}' for b in bs)

def open_serial():
    return serial.Serial(
        PORT, BAUD,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=READ_TIMEOUT,
        xonxoff=False, rtscts=False, dsrdtr=False,
        exclusive=True
    )

def segment_packets(s: serial.Serial):
    """
    Generator that yields bytearray packets split by inter-byte gap > GAP_US.
    """
    buf = bytearray()
    last_t = time.time()
    while True:
        b = s.read(1)
        if not b:
            # timeout: if buffer has data and we've waited long enough, flush as a packet
            if buf:
                yield bytes(buf)
                buf.clear()
            continue
        t = time.time()
        dt_us = (t - last_t) * 1e6
        last_t = t
        if buf and dt_us > GAP_US:
            # start new packet
            yield bytes(buf)
            buf.clear()
        buf += b
        # small sleep to let buffer fill without busy-wait
        # (kept tiny; segmentation uses timestamps)
        # time.sleep(0.0005)

def classify(pkt: bytes):
    """
    Very light classifier. Adjust once we see real payloads.
    Returns (event, fields_dict) or ('unknown', {...})
    """
    # Drop solitary 0x30 noise
    if DROP_LONE_30 and len(pkt) == 1 and pkt[0] == 0x30:
        return ('noise', {'pkt': pkt})

    # Common simple patterns to try first:
    #  - 3-byte note msgs: [status, note, vel]
    #  - 2-byte AT msgs:   [AT_TAG, value] or [status, value]
    # You can adapt these once we capture examples.
    if len(pkt) == 3 and (pkt[0] & 0xF0) in (0x80, 0x90):  # MIDI-like
        status, note, vel = pkt
        on = (status & 0xF0) == 0x90 and vel != 0
        off = (status & 0xF0) == 0x80 or ((status & 0xF0) == 0x90 and vel == 0)
        if on:
            return ('note_on', {'note': note, 'vel': vel, 'raw': pkt})
        if off:
            return ('note_off', {'note': note, 'vel': vel, 'raw': pkt})
    # Heuristic: aftertouch-like (2 bytes) 0xA? val or tagged 0xAT xx
    if len(pkt) == 2:
        a, b = pkt
        if (a & 0xF0) == 0xA0:  # channel pressure
            return ('aftertouch', {'val': b, 'raw': pkt})
        # Generic tag 0xAT? If you know the tag, add it here.

    # If packets have fixed header/len, add rules here:
    # if len(pkt)==5 and pkt[0]==0xAA: ...

    return ('unknown', {'raw': pkt})

def clamp(v, lo, hi): return lo if v < lo else hi if v > hi else v

def smooth_aftertouch(prev_val, new_val, dt_ms):
    """
    Median-of-3 (using last two EMA states + new) then EMA + slew limit
    For simplicity we keep only prev EMA; median uses prev, new, prev (degenerate),
    but still gives us a clean path + slew limit.
    """
    # In practice, we keep EMA only; you can keep a small ring if you like.
    ema = prev_val + AT_EMA_ALPHA * (new_val - prev_val)
    if dt_ms <= 0: dt_ms = 1.0
    max_step = AT_SLEW_MAX_PER_MS * dt_ms
    ema = clamp(ema, prev_val - max_step, prev_val + max_step)
    return int(clamp(round(ema), AT_MIN, AT_MAX))

def main():
    try:
        ser = open_serial()
    except Exception as e:
        print(f"Serial open failed: {e}")
        sys.exit(1)

    print(f"Listening on {PORT} @ {BAUD} baud (gap={GAP_US} µs)")
    ks = collections.defaultdict(KeyState)
    packet_count = 0

    with open(CSV_FILE, 'w', newline='') as fcsv, open(UNK_FILE, 'w') as funk:
        w = csv.writer(fcsv)
        w.writerow(['time','event','note','vel','AT','packet'])

        for pkt in segment_packets(ser):
            ts = time.strftime('%H:%M:%S.') + f"{int((time.time()%1)*1000):03d}"
            event, info = classify(pkt)

            if event == 'noise':
                continue

            if event == 'note_on':
                note, vel = info['note'], info['vel']
                st = ks[note]
                st.is_on = True
                st.last_on_ms = now_ms()
                # Mask AT for a short time after ON
                print(f"[{ts}] ON  {note:3d} vel{vel:3d}  {hexs(pkt)}")
                w.writerow([ts,'on',note,vel,'',hexs(pkt)])
                packet_count += 1
                continue

            if event == 'note_off':
                note, vel = info['note'], info['vel']
                st = ks[note]
                t = now_ms()
                if (t - st.last_on_ms) < NOTE_OFF_DEBOUNCE_MS:
                    # ignore ultra-fast off glitches
                    continue
                st.is_on = False
                st.last_off_ms = t
                print(f"[{ts}] OFF {note:3d} vel{vel:3d}  {hexs(pkt)}")
                w.writerow([ts,'off',note,vel,'',hexs(pkt)])
                packet_count += 1
                continue

            if event == 'aftertouch':
                raw = int(info['val'])
                t = now_ms()
                # Optional: global/channel AT; if per-note AT exists, adapt map
                # Ignore AT immediately after any note-on to kill the "impact spike"
                recent_on = any((t - ks[n].last_on_ms) < AT_IGNORE_AFTER_ON_MS for n in ks if ks[n].is_on)
                if recent_on:
                    continue
                # Smooth + slew limit
                # Here we keep one global AT value; if you have per-note, keep in KeyState
                prev = getattr(main, '_at_prev', 0)
                prev_t = getattr(main, '_at_prev_t', t)
                dt = t - prev_t
                at_val = smooth_aftertouch(prev, raw, dt)
                main._at_prev, main._at_prev_t = at_val, t

                print(f"[{ts}] AT        {at_val:3d}   ({raw:3d})  {hexs(pkt)}")
                w.writerow([ts,'aftertouch','', '',at_val,hexs(pkt)])
                packet_count += 1
                continue

            # Unknown packet -> log once (don’t spam)
            h = hexs(pkt)
            print(f"[{ts}] ?? {h}")
            funk.write(f"{ts} {h}\n")
            funk.flush()
            w.writerow([ts,'unknown','', '', '',h])

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
