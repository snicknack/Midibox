#!/usr/bin/env python3
# 88-Key Fatar Row Decoder: Flags Rows w/ Vel (No Bit Unpack to Avoid Flood)
# Row 0-7: Bytes 4-11 (non-00/F8/C0 = hit vel). CSV w/ row guesses.
# Connections: Same. Run: sudo python3 uart_sniffer_88row.py

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
CSV_FILE = "keybed_88row.csv"
KEYS_PER_ROW = 11  # For note range guess
BASE_NOTE = 21  # A0

# Padding values to ignore
PADDING = {0x00, 0xF8, 0xC0}

# Row note ranges (approx for guesses)
ROW_RANGES = [
    f"A0-B0 (21-23)", f"C1-D#1 (24-35)", f"E1-G#1 (36-47)", f"A1-B1 (48-50)",
    f"C2-D#2 (51-62)", f"E2-G#2 (63-74)", f"A2-B2 (75-77)", f"C3-C8 (78-108)"
]

def note_range(row):
    return ROW_RANGES[row % 8]

def hex_dump(data):
    data = data[:PACKET_SIZE]
    hex_str = ' '.join(f'{b:02X}' for b in data)
    matrix_str = ' '.join(f'{b:02X}' for b in data[4:12])  # Bytes 4-11
    return f"[{len(data)}B] {hex_str} | Matrix: {matrix_str}"

def unpack_rows(data):
    """Flag rows 0-7 if byte 4-11 non-padding; vel = byte if 1-127."""
    rows_hit = []
    vels = []
    for row in range(8):
        byte = data[4 + row]
        if byte not in PADDING and 1 <= byte <= 127:
            rows_hit.append(row)
            vels.append(byte)
    avg_vel = sum(vels) / len(vels) if vels else 0
    at_bytes = [b for b in data[12:] if 1 <= b <= 127]  # Real AT, ignore F8
    at = max(at_bytes) if at_bytes else 0
    return rows_hit, int(avg_vel), int(at)

def control_poll(channel, debouncer, now):
    state = GPIO.input(channel)
    if state == GPIO.LOW and debouncer.should_alert(now):
        print(f"[{time.strftime('%H:%M:%S.%f')[:-3]}] CONTROL LOW: Row scan!")

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

def export_csv(timestamp, rows_hit, vel, at, raw_hex):
    row_str = ','.join(map(str, rows_hit)) if rows_hit else 'Idle'
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, row_str, vel, at, raw_hex])

def main():
    ser = None
    gpio_ok = False
    debouncer = None
    # Init CSV
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Timestamp', 'Rows Hit', 'Vel', 'Aftertouch', 'Raw Hex'])
    try:
        gpio_ok, debouncer = setup_gpio()
        ser = setup_serial(CURRENT_BAUD)
        print(f"88-Key Row Decoder: Rows 0-7 (A0-C8) | CSV to {CSV_FILE}")
        print(f"  - UART: {PORT} @ {CURRENT_BAUD} baud")
        print("  Press ONE key at a time (A0 then C8). Ctrl+C to stop...\n")

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
                    rows_hit, vel, at = unpack_rows(packet)
                    timestamp = time.strftime('%H:%M:%S.%f')[:-3]

                    if rows_hit:
                        row_str = ', '.join(f"Row{ r } {note_range(r)} vel{data[4+r]}" for r in rows_hit)
                        print(f"[{timestamp}] HIT: {row_str} | Avg Vel ~{vel} | AT {at} | {hex_dump(packet)}")
                        export_csv(timestamp, rows_hit, vel, at, raw_hex)
                    else:
                        print(f"[{timestamp}] IDLE #{packet_count} | {hex_dump(packet)}")

                    buffer = buffer[PACKET_SIZE:]

            elif now - last_activity > IDLE_TIMEOUT and len(buffer) > 8:
                raw_hex = ' '.join(f'{b:02X}' for b in buffer)
                rows_hit, vel, at = unpack_rows(buffer + b'\x00' * (PACKET_SIZE - len(buffer)))
                timestamp = time.strftime('%H:%M:%S.%f')[:-3]
                if rows_hit:
                    row_str = ', '.join(f"Row{ r } {note_range(r)} vel{data[4+r]}" for r in rows_hit)
                    print(f"[{timestamp}] PARTIAL HIT: {row_str} | Avg Vel ~{vel} | {hex_dump(buffer)}")
                    export_csv(timestamp, rows_hit, vel, at, raw_hex)
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
