#!/usr/bin/env python3
# Fatar MIDI v8: Hard-Press Filter (Vel >50 On, Ignore 0x37) + 300ms Off
# Run: sudo python3 uart_sniffer_midi_v8.py

import serial
import time
import sys
import csv

CURRENT_BAUD = 38400
PORT = '/dev/serial0'
READ_TIMEOUT = 0.2
CSV_FILE = "keybed_midi_v8.csv"
UNKNOWN_FILE = "unknown_vels.txt"

KEY_MAP = {
    0x29: 21,  # A0 light
    0x38: 21,  # A0 medium
    0x3E: 108, # C8 medium
    0x3F: 108, # C8 hard
}

PADDING_VELS = {0x20, 0x21, 0x2F, 0x31, 0x37}  # Ignore noise

class Debouncer:
    def __init__(self, cooldown_ms):
        self.last_time = 0
        self.cooldown = cooldown_ms / 1000.0

    def ready(self, now):
        if now - self.last_time > self.cooldown:
            self.last_time = now
            return True
        return False

def note_name(note):
    names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (note // 12) - 1
    key = note % 12
    return f"{names[key]}{octave}"

def hex_dump(data):
    hex_str = ' '.join(f'{b:02X}' for b in data)
    return f"[{len(data)}B] {hex_str}"

def log_unknown(vel):
    with open(UNKNOWN_FILE, 'a') as f:
        f.write(f"0x{vel:02X} ({vel}) - what key/vel? {time.strftime('%H:%M:%S')}\n")

def assemble_and_decode(buffer, on_debouncer, off_debouncer, at_debouncer, now):
    if len(buffer) < 2:
        return None
    # Vel FF for On/Off (known only, On vel >50 dec = 0x32+)
    for i in range(len(buffer) - 1):
        if buffer[i+1] == 0xFF and 0x28 <= buffer[i] <= 0x3F and buffer[i] not in PADDING_VELS:
            vel = buffer[i]
            if vel in KEY_MAP:
                note = KEY_MAP[vel]
                if vel > 50:  # Hard On threshold
                    if on_debouncer.ready(now):
                        return buffer[i-1:i+3], vel, 0, note, "Note On"
                else:  # Off
                    if off_debouncer.ready(now):
                        return buffer[i-1:i+3], vel, 0, note, "Note Off"
            else:
                log_unknown(vel)
                print(f"  Unknown vel 0x{vel:02X} logged—what key?")
                return None
    # Channel AT (07-0E)
    for i in range(len(buffer)):
        if 0x07 <= buffer[i] <= 0x0E:
            if at_debouncer.ready(now):
                at = buffer[i]
                return buffer[i-1:i+2], 0, at, 0, "Channel AT"
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
        print(f"MIDI v8 Decoder: {PORT} @ {CURRENT_BAUD} baud | CSV to {CSV_FILE}")
        print("Idle. Hard press A0 + hold at [time]. Idle. C8 + hold. Ctrl+C...\n")

        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Event', 'Note', 'Name', 'Vel', 'AT', 'Raw'])

        packet_count = 0
        on_debouncer = Debouncer(100)  # 100ms On
        off_debouncer = Debouncer(300)  # 300ms Off
        at_debouncer = Debouncer(20)  # 20ms AT
        while True:
            chunk = ser.read(ser.in_waiting or 1)
            if chunk:
                buffer.extend(chunk)
                now = time.time()
                result = assemble_and_decode(buffer, on_debouncer, off_debouncer, at_debouncer, now)
                if result:
                    packet, vel, at, note, event = result
                    packet_count += 1
                    name = note_name(note) if note else "N/A"
                    timestamp = time.strftime('%H:%M:%S.%f')[:-3]
                    line = f"[{timestamp}] {event} {name} vel{vel} AT{at}"
                    print(line)
                    # MIDI Bytes
                    if event == "Note On":
                        midi = f"90 {note:02X} {vel:02X}"
                        print(f"  MIDI: {midi} (Note On)")
                    elif event == "Channel AT":
                        midi = f"D0 {at:02X}"
                        print(f"  MIDI: {midi} (Channel AT)")
                    elif event == "Note Off":
                        midi = f"80 {note:02X} 00"
                        print(f"  MIDI: {midi} (Note Off)")
                    with open(CSV_FILE, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([timestamp, event, note, name, vel, at, packet.hex(sep=' ')])
                    buffer = buffer[len(packet):]
            time.sleep(0.005)

    except KeyboardInterrupt:
        print(f"\nStopped. {packet_count} events. Check {CSV_FILE}! Unknowns in {UNKNOWN_FILE}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if ser:
            ser.close()

if __name__ == "__main__":
    main()
