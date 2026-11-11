#!/usr/bin/env python3
# Fatar MIDI v3: "XX FF" Events + Expanded Map from Log
# Vel = XX (29=A0 light, 38=A0 medium, 3E=C8); AT = 07-0E. CSV + MIDI bytes.
# Run: sudo python3 uart_sniffer_midi_v3.py

import serial
import time
import sys
import csv

CURRENT_BAUD = 38400
PORT = '/dev/serial0'
READ_TIMEOUT = 0.2
CSV_FILE = "keybed_midi_v3.csv"

# Map from log: vel byte → note (expand with more)
KEY_MAP = {
    0x29: 21,  # 41 dec → A0 light
    0x38: 21,  # 56 dec → A0 medium
    0x3E: 108, # 62 dec → C8 medium
    # Unknowns logged for add (e.g., 0x21: 21 low vel)
}

def note_name(note):
    names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (note // 12) - 1
    key = note % 12
    return f"{names[key]}{octave}"

def hex_dump(data):
    hex_str = ' '.join(f'{b:02X}' for b in data)
    return f"[{len(data)}B] {hex_str}"

def assemble_and_decode(buffer):
    if len(buffer) < 2:
        return None
    # Look for "XX FF" pattern (vel + end)
    for i in range(len(buffer) - 1):
        if buffer[i+1] == 0xFF:
            vel = buffer[i]
            if 0x20 <= vel <= 0x3F:  # Vel range
                note = KEY_MAP.get(vel, 0)
                if note == 0:
                    print(f"  Unknown vel 0x{vel:02X} ({vel})—what key?")
                event = "Note On" if vel >= 0x28 else "AT"  # Threshold for on vs pressure
                # AT if low + 07-0E follow
                at = 0
                at_pos = i + 2
                if at_pos < len(buffer) and 0x07 <= buffer[at_pos] <= 0x0E:
                    at = buffer[at_pos]
                return buffer[i-2:i+4] if i >=2 else buffer, vel, at, note, event  # Small packet
    # Note Off on FE
    if b'\xFE' in buffer:
        note = 21  # Guess A0; refine
        return buffer[-3:], 0, 0, note, "Note Off"
    return None

def main():
    ser = None
    buffer = bytearray()
    try:
        ser = serial.Serial(
            port=PORT,
            baudrate=CURRENT_BAUD,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=READ_TIMEOUT
        )
        print(f"MIDI v3 Decoder: {PORT} @ {CURRENT_BAUD} baud | CSV to {CSV_FILE}")
        print("Idle. Press A0 + hold at [time]. Idle. C8 + hold. Ctrl+C...\n")

        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Event', 'Note', 'Name', 'Vel', 'AT', 'Raw', 'MIDI Bytes'])

        packet_count = 0
        last_raw_time = 0
        while True:
            chunk = ser.read(ser.in_waiting or 1)
            if chunk:
                buffer.extend(chunk)
                result = assemble_and_decode(buffer)
                if result:
                    packet, vel, at, note, event = result
                    packet_count += 1
                    name = note_name(note) if note else "Unknown"
                    timestamp = time.strftime('%H:%M:%S.%f')[:-3]
                    line = f"[{timestamp}] {event} {name} vel{vel} AT{at}"
                    print(line)
                    # MIDI Bytes Stub (ch1)
                    if event == "Note On":
                        midi = f"90 {note:02X} {vel:02X}"
                        print(f"  MIDI: {midi} (Note On)")
                    elif event == "AT":
                        midi = f"A0 {note:02X} {at:02X}"
                        print(f"  MIDI: {midi} (Poly AT)")
                    elif event == "Note Off":
                        midi = f"80 {note:02X} 00"
                        print(f"  MIDI: {midi} (Note Off)")
                    with open(CSV_FILE, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([timestamp, event, note, name, vel, at, packet.hex(sep=' '), midi if 'midi' in locals() else ''])
                    buffer = buffer[len(packet):] if len(packet) > 0 else buffer[1:]  # Shift
                # Throttled raw
                now = time.time()
                if len(chunk) > 0 and not result and now - last_raw_time > 0.05:
                    timestamp = time.strftime('%H:%M:%S.%f')[:-3]
                    print(f"[{timestamp}] Raw: {hex_dump(chunk)}")
                    last_raw_time = now
            time.sleep(0.005)

    except KeyboardInterrupt:
        print(f"\nStopped. {packet_count} events. Check {CSV_FILE}!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if ser:
            ser.close()

if __name__ == "__main__":
    main()
