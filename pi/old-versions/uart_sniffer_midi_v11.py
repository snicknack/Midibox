#!/usr/bin/env python3
# Fatar MIDI v11: Debug Mode + 1s Timeout
# Hard-Press Only (Vel >0x37 On) + Strict Noise Filter
# Run: sudo python3 uart_sniffer_midi_v11.py

import serial
import time
import sys
import csv

CURRENT_BAUD = 38400
PORT = '/dev/serial0'  # Adjust if needed (e.g., /dev/ttyS0, /dev/ttyUSB0)
READ_TIMEOUT = 1.0     # Increased to 1s
CSV_FILE = "keybed_midi_v11.csv"
UNKNOWN_FILE = "unknown_vels.txt"

KEY_MAP = {
    0x29: 21,  # A0 light
    0x38: 21,  # A0 medium
    0x3E: 108, # C8 medium
    0x3F: 108, # C8 hard
    0x2F: 21,  # A0/C8 off (assumed)
}

PADDING_VELS = {0x20, 0x21, 0x30, 0x31, 0x37}  # Ignore noise

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

def log_unknown(vel, unknown_debouncer, now):
    if unknown_debouncer.ready(now):
        with open(UNKNOWN_FILE, 'a') as f:
            f.write(f"0x{vel:02X} ({vel}) - what key/vel? {time.strftime('%H:%M:%S')}\n")
        print(f"  Unknown vel 0x{vel:02X} logged—what key?")
        return True
    return False

def assemble_and_decode(buffer, on_debouncer, off_debouncer, at_debouncer, unknown_debouncer, now):
    if len(buffer) < 2:
        return None
    for i in range(len(buffer) - 1):
        if buffer[i+1] == 0xFF and 0x28 <= buffer[i] <= 0x3F and buffer[i] not in PADDING_VELS:
            vel = buffer[i]
            if vel in KEY_MAP:
                note = KEY_MAP[vel]
                if vel > 0x37:  # Hard On threshold
                    if on_debouncer.ready(now):
                        return buffer[i-1:i+3], vel, 0, note, "Note On"
                elif vel == 0x2F:  # Explicit Off
                    if off_debouncer.ready(now):
                        return buffer[i-1:i+3], vel, 0, note, "Note Off"
            else:
                log_unknown(vel, unknown_debouncer, now)
                return None
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
        print(f"Port opened: {PORT} @ {CURRENT_BAUD} baud, timeout {READ_TIMEOUT}s")
        print(f"MIDI v11 Decoder: CSV to {CSV_FILE}")
        print("Idle. Hard press A0 + hold at [time]. Idle. C8 + hold. Ctrl+C...\n")

        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Event', 'Note', 'Name', 'Vel', 'AT', 'Raw'])

        packet_count = 0
        on_debouncer = Debouncer(100)    # 100ms On
        off_debouncer = Debouncer(500)   # 500ms Off
        at_debouncer = Debouncer(20)     # 20ms AT
        unknown_debouncer = Debouncer(500)  # 500ms Unknowns
        while True:
            chunk
