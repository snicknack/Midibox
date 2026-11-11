#!/usr/bin/env python3
# Fatar MIDI Decoder: Maps Vel/AT to Notes (A0=38, C8=3E) + Stub Output
# Assembles bursts, scales AT. CSV + console MIDI events.
# Run: sudo python3 uart_sniffer_midi.py

import serial
import time
import sys
import csv

CURRENT_BAUD = 38400
PORT = '/dev/serial0'
READ_TIMEOUT = 0.2
PACKET_SIZE = 16
CSV_FILE = "keybed_midi.csv"

# Key Mapping (expand with more tests; vel byte → note)
KEY_MAP = {
    0x38: 21,  # 56 dec → A0
    0x3E: 108, # 62 dec → C8
    # Add e.g., 0x3A: 60 (middle C) from future tests
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
    """Assemble to packet, extract vel/AT/note."""
    if len(buffer) < 4:
        return None
    # Find F8 start
    start = buffer.find(b'\xF8')
    if start == -1:
        return None
    packet = buffer[start:start+PACKET_SIZE]
    if len(packet) < PACKET_SIZE:
        packet += b'\x00' * (PACKET_SIZE - len(packet))
    # Vel: first non-padding after F8
    vel_bytes = [b for b in packet[1:6] if b in KEY_MAP]  # Early bytes for vel
    vel = vel_bytes[0] if vel_bytes else 0
    note = KEY_MAP.get(vel, 0)
    # AT: avg non-F8 in 6-12, scale /2
    at_raw = [b for b in packet[6:12] if 1 <= b <= 127]
    at = int(sum(at_raw) / len(at_raw) / 2) if at_raw else 0
    # Event guess: vel>0 = Note On, FE = Off
    event = "Note On" if vel > 0 else "Note Off" if b'\xFE' in packet else "AT"
    return packet, vel, at, note, event

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
        print(f"MIDI Decoder: {PORT} @ {CURRENT_BAUD} baud | CSV to {CSV_FILE}")
        print("Press A0/C8 + hold. Ctrl+C...\n")

        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Event', 'Note', 'Name', 'Vel', 'AT', 'Raw'])

        packet_count = 0
        while True:
            chunk = ser.read(ser.in_waiting or 1)
            if chunk:
                buffer.extend(chunk)
                result = assemble_and_decode(buffer)
                if result:
                    packet, vel, at, note, event = result
                    packet_count += 1
                    name = note_name(note) if note else "Idle"
                    timestamp = time.strftime('%H:%M:%S.%f')[:-3]
                    line = f"[{timestamp}] {event} {name} vel{vel} AT{at}"
                    print(line)
                    # MIDI Stub: Print for DAW (or use mido for USB)
                    if event == "Note On":
                        print(f"  MIDI: Note On ch1 {note} vel{vel}")
                    elif event == "AT":
                        print(f"  MIDI: Poly Pressure {note} {at}")
                    elif event == "Note Off":
                        print(f"  MIDI: Note Off {note} vel0")
                    with open(CSV_FILE, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([timestamp, event, note, name, vel, at, packet.hex(sep=' ')])
                    buffer = buffer[len(packet):]
                # Raw fallback
                if len(chunk) > 0 and not result:
                    timestamp = time.strftime('%H:%M:%S.%f')[:-3]
                    print(f"[{timestamp}] Raw: {hex_dump(chunk)}")
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
