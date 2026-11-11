#!/usr/bin/env python3
# 88-Key Fatar Decoder: 8 Rows x 11 Cols (A0=21 to C8=108)
# Exports CSV with note names. Connections: Same. Run: sudo python3 uart_sniffer_88key.py

import serial
import time
import sys
import RPi.GPIO as GPIO
import csv

# Configuration
CURRENT_BAUD = 115200
PORT = '/dev/serial0'
UART_TX_PIN = 14
UART_RX_PIN = 15
CONTROL_PIN = 18
PACKET_SIZE = 16
IDLE_TIMEOUT = 0.05
FAST_POLL = True
POLL_INTERVAL = 0.002
DEBOUNCE_MS = 5
CSV_FILE = "keybed_88_decode.csv"
KEYS_PER_ROW = 11  # 8 rows x 11 cols = 88 keys
BASE_NOTE = 21  # A0 start

# Note names for readability
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def note_to_name(note):
    if 21 <= note <= 108:
        octave = (note // 12) - 1
        key = note % 12
        return f"{NOTE_NAMES[key]}{octave}"
    return f"Note{note}"

def hex_dump(data):
    data = data[:PACKET_SIZE]
    hex_str = ' '.join(f'{b:02X}' for b in data)
    return f"[{len(data)}B] {hex_str}"

def unpack_matrix(data):
    """Unpack bytes 4-11: 11 bits/row (low 8 from byte; high 3 from nibble guess)."""
    notes = []
    vels = []
    for row in range(8):
        byte = data[4 + row]
        # Low 8 bits for cols 0-7
        for col in range(8):
            if (byte >> col) & 1:
                note = BASE_NOTE + row * KEYS_PER_ROW + col
                notes.append(note)
                vels.append(byte & 0x7F)  # Vel guess: byte value
        # High 3 bits for cols 8-10 (from high nibble or overflow)
        high_nib = (byte >> 4) & 0x07  # 3 bits
        for col in range(3):
            if (high_nib >> col) & 1:
                note = BASE_NOTE + row * KEYS_PER_ROW + (8 + col)
                notes.append(note)
                vels.append(byte & 0x7F)
    avg_vel = sum(vels) / len(vels) if vels else 0
    at = max(data[12:]) if any(b > 10 for b in data[12:]) else 0
    return notes, int(avg_vel), int(at)

def control_poll(channel, debouncer, now):
    state = GPIO.input(channel)
    if state == GPIO.LOW and debouncer.should_alert(now):
        print(f"[{time.strftime('%H:%M:%S.%f')[:-3]}] CONTROL LOW: 88-key scan!")

def setup_gpio():
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(CONTROL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print(f"  - Control: GPIO{CONTROL_PIN} (fast-polling)")
        return True, Debouncer(DEBOUNCE_MS)
    except Exception as e:
        print(f"  - Control failed: {e}.")
        return False, None

def setup_serial(baud):
    try:
        ser = serial.Serial(
            port=PORT,
            baudrate=baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=IDLE_TIMEOUT
        )
        return ser
    except serial.SerialException as e:
        raise Exception(f"Serial failed: {e}.")

class Debouncer:
    def __init__(self, cooldown_ms):
        self.last_low_time = 0
        self.cooldown_ms = cooldown_ms / 1000.0

    def should_alert(self, now):
        if now - self.last_low_time > self.cooldown_ms:
            self.last_low_time = now
            return True
        return False

def export_csv(timestamp, notes, vel, at, raw_hex):
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        for note in notes:
            writer.writerow([timestamp, note, note_to_name(note), vel, at, raw_hex])

def main():
    ser = None
    gpio_ok = False
    debouncer = None
    # Init CSV
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Timestamp', 'MIDI Note', 'Name', 'Vel', 'Aftertouch', 'Raw Hex'])
    try:
        gpio_ok, debouncer = setup_gpio()
        ser = setup_serial(CURRENT_BAUD)
        print(f"88-Key Decoder started: A0(21) to C8(108) | CSV to {CSV_FILE}")
        print(f"  - UART: {PORT} @ {CURRENT_BAUD} baud")
        print("  Ctrl+C to stop...\n")

        buffer = bytearray()
        last_activity = time.time()
        packet_count = 0

        while True:
            now = time.time()
            if gpio_ok:
                control_poll(CONTROL_PIN, debouncer, now)

            if ser.in_waiting > 0:
                chunk = ser.read(ser.in_waiting)
                buffer.extend(chunk)
                last_activity = now

                while len(buffer) >= PACKET_SIZE:
                    packet = buffer[:PACKET_SIZE]
                    packet_count += 1
                    raw_hex = ' '.join(f'{b:02X}' for b in packet)
                    notes, vel, at = unpack_matrix(packet)[:3]  # Ignore matrix for now
                    timestamp = time.strftime('%H:%M:%S.%f')[:-3]

                    if notes:
                        note_str = ', '.join(note_to_name(n) for n in notes)
                        print(f"[{timestamp}] HIT: {note_str} | Vel ~{vel} | AT {at} | {hex_dump(packet)}")
                        export_csv(timestamp, notes, vel, at, raw_hex)
                    else:
                        print(f"[{timestamp}] IDLE #{packet_count} | {hex_dump(packet)}")

                    buffer = buffer[PACKET_SIZE:]

            elif now - last_activity > IDLE_TIMEOUT and len(buffer) > 8:
                raw_hex = ' '.join(f'{b:02X}' for b in buffer)
                notes, vel, at = unpack_matrix(buffer + b'\x00' * (PACKET_SIZE - len(buffer)))[:3]
                timestamp = time.strftime('%H:%M:%S.%f')[:-3]
                if notes:
                    note_str = ', '.join(note_to_name(n) for n in notes)
                    print(f"[{timestamp}] PARTIAL HIT: {note_str} | Vel ~{vel} | {hex_dump(buffer)}")
                    export_csv(timestamp, notes, vel, at, raw_hex)
                buffer.clear()

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print(f"\nStopped. {packet_count} scans. Check {CSV_FILE}!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if ser:
            ser.close()
        if gpio_ok:
            GPIO.cleanup()
        print("Cleanup done.")

if __name__ == "__main__":
    main()
