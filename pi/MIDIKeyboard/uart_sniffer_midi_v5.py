#!/usr/bin/env python3
# Fatar MIDI v5: Debounced Events + Noise Filter (Ignore Padding 0x2F/0x31)
# AT only after On. Raw >3B only. Logs unknowns.
# Run: sudo python3 uart_sniffer_midi_v5.py

import serial
import time
import sys
import csv

CURRENT_BAUD = 38400
PORT = '/dev/serial0'
READ_TIMEOUT = 0.2
CSV_FILE = "keybed_midi_v5.csv"
UNKNOWN_FILE = "unknown_vels.txt"

KEY_MAP = {
    0x29: 21,  # A0 light
    0x38: 21,  # A0 medium
    0x3E: 108, # C8 medium
    0x2F: 21,  # A0 off (from log)
}

PADDING_VELS = {0x20, 0x21, 0x2F, 0x31}  # Ignore these as noise

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

def assemble_and_decode(buffer, debouncer, now, after_on):
    if len(buffer) < 2:
        return None
    # Vel FF for On/Off
    for i in range(len(buffer) - 1):
        if buffer[i+1] == 0xFF and 0x28 <= buffer[i] <= 0x3F and buffer[i] not in PADDING_VELS:
            if not debouncer.ready(now):
                return None
            vel = buffer[i]
            note = KEY_MAP.get(vel, 0)
            if note == 0:
                log_unknown(vel)
                print(f"  Unknown vel 0x{vel:02X} ({vel}) logged—what key?")
            event = "Note On" if vel >= 0x30 else "Note Off"
            return buffer[i-1:i+3], vel, 0, note, event, True  # True = after_on
    # Channel AT nibble (07-0E, only after On)
    if after_on:
        for i in range(len(buffer)):
            if 0x07 <= buffer[i] <= 0x0E:
                if not debouncer.ready(now):
                    return None
                at = buffer[i]
                return buffer[i-1:i+2], 0, at, 0, "Channel AT", False
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
        print(f"MIDI v5 Decoder: {PORT} @ {CURRENT_BAUD} baud | CSV to {CSV_FILE}")
        print("Idle. Press A0 + hold at [time]. Idle. C8 + hold. Ctrl+C...\n")

        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Event', 'Note', 'Name', 'Vel', 'AT', 'Raw'])

        packet_count = 0
        last_raw_time = 0
        debouncer = Debouncer(50)  # 50ms cooldown
        after_on = False
        while True:
            chunk = ser.read(ser.in_waiting or 1)
            if chunk:
                buffer.extend(chunk)
                now = time.time()
                result = assemble_and_decode(buffer, debouncer, now, after_on)
                if result:
                    packet, vel, at, note, event, new_after_on = result
                    packet_count += 1
                    after_on = new_after_on
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
                # Throttled raw (>3B)
                now = time.time()
                if len(chunk) > 3 and not result and now - last_raw_time > 0.2:
                    timestamp = time.strftime('%H:%M:%S.%f')[:-3]
                    print(f"[{timestamp}] Raw: {hex_dump(chunk)}")
                    last_raw_time = now
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
