#!/usr/bin/env python3
# midibox_serial_to_midi_v2.py  – Pi4 bridge from STM32 UART -> USB MIDI, robust parser
import serial, time, mido

PORT = '/dev/serial0'
BAUD = 31250    
SER_TIMEOUT = 0.00

# Optional index->MIDI mapping (leave DISABLED unless you confirm indices)
USE_INDEX_MAP = False
IDX_LOW, NOTE_LOW = 120, 21   # A0 example
IDX_HIGH, NOTE_HIGH = 248, 108
def map_idx_to_midi(n):
    # linear map from two anchors
    if IDX_HIGH == IDX_LOW: return n
    slope = (NOTE_HIGH - NOTE_LOW) / (IDX_HIGH - IDX_LOW)
    return int(round(NOTE_LOW + slope * (n - IDX_LOW)))

# MIDI real-time (single-byte, can occur anywhere)
REALTIME = {0xF8, 0xFA, 0xFB, 0xFC, 0xFE, 0xFF}

# How many data bytes follow each status (Channel Voice msgs)
DATA_LEN = {
    0x80: 2, 0x90: 2, 0xA0: 2, 0xB0: 2, 0xC0: 1, 0xD0: 1, 0xE0: 2
}

def is_status(b):   return 0x80 <= b <= 0xEF
def is_realtime(b): return b in REALTIME
def is_sysex_or_system_common(b): return 0xF0 <= b <= 0xF7  # we’ll ignore these for now

def main():
    out = mido.open_output('Midibox Keyboard', virtual=True)
    print("✅  Virtual MIDI port 'Midibox Keyboard' created.")
    print("   Use `aconnect 'Midibox Keyboard':0 'Behringer Crave':0` to route.\n")

    ser = serial.Serial(PORT, BAUD, timeout=SER_TIMEOUT,
                        bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)

    running_status = None
    needed = 0
    buf = bytearray()

    while True:
        bts = ser.read(64)
        if not bts:
            time.sleep(0.001)
            continue

        for b in bts:
            # 1) Handle real-time immediately; don’t disturb running_status
            if is_realtime(b):
                # You could forward clocks if you want; for now ignore.
                # Example: if b == 0xF8: out.send(mido.Message('clock'))
                continue

            # 2) Ignore system-common / sysex for now (F0..F7) to avoid parser confusion
            if is_sysex_or_system_common(b):
                # reset any partial msg
                running_status = None
                needed = 0
                buf.clear()
                continue

            # 3) If a fresh Channel Voice status byte, start a new message
            if is_status(b):
                running_status = b
                cmd = running_status & 0xF0
                needed = DATA_LEN.get(cmd, 0)
                buf.clear()
                # If no data needed (shouldn’t happen for channel voice except C0/D0 1 byte), we’d dispatch here.
                continue

            # 4) Otherwise it's a data byte (0..127). Filter out junk >127.
            if b > 0x7F:
                # Non-MIDI token (e.g. 0x20 0x.. FF sequences from STM32). Drop it.
                # Also reset partial assembly to avoid poisoning next msg.
                needed = 0
                buf.clear()
                continue

            # If we don't have a running status, we can't place this data byte; drop it.
            if running_status is None or needed == 0:
                # No active MIDI context → ignore stray data (e.g., '20 18' tokens)
                continue

            # Accumulate data bytes
            buf.append(b)
            if len(buf) == needed:
                # Dispatch
                status = running_status
                ch = status & 0x0F
                cmd = status & 0xF0

                try:
                    if cmd == 0x90 and buf[1] > 0:
                        note = map_idx_to_midi(buf[0]) if USE_INDEX_MAP else buf[0]
                        out.send(mido.Message('note_on', note=note, velocity=buf[1], channel=ch))
                        print(f"Note ON  n={note:3d} v={buf[1]:3d}")
                    elif cmd in (0x80, 0x90) and buf[1] == 0:
                        note = map_idx_to_midi(buf[0]) if USE_INDEX_MAP else buf[0]
                        out.send(mido.Message('note_off', note=note, velocity=0, channel=ch))
                        print(f"Note OFF n={note:3d}")
                    elif cmd == 0xD0:
                        out.send(mido.Message('aftertouch', value=buf[0], channel=ch))
                        print(f"AT {buf[0]}")
                    elif cmd == 0xC0:
                        out.send(mido.Message('program_change', program=buf[0], channel=ch))
                    elif cmd == 0xA0:
                        out.send(mido.Message('polytouch', note=buf[0], value=buf[1], channel=ch))
                    elif cmd == 0xB0:
                        out.send(mido.Message('control_change', control=buf[0], value=buf[1], channel=ch))
                    elif cmd == 0xE0:
                        # pitch bend LSB/MSB 7-bit -> 14-bit
                        val = (buf[1] << 7) | buf[0]
                        out.send(mido.Message('pitchwheel', pitch=val-8192, channel=ch))
                    # Keep running_status for possible running-state continuation
                except ValueError as e:
                    # Guard against any out-of-range values
                    print("Dropped invalid MIDI:", e)

                # Prepare for next message (running status remains valid)
                buf.clear()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
