#!/usr/bin/env python3
# Raw Hex Dumper for Fatar: Timestamps + Full Bytes (No Parse)
# Logs all chunks to console + keybed_raw.txt. Run: sudo python3 uart_sniffer_raw.py

import serial
import time
import sys

CURRENT_BAUD = 115200
PORT = '/dev/serial0'
IDLE_TIMEOUT = 0.05
LOG_FILE = "keybed_raw.txt"

def hex_dump(data):
    hex_str = ' '.join(f'{b:02X}' for b in data)
    asc_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data)
    return f"[{len(data)}B] {hex_str} | {asc_str}"

def main():
    ser = None
    try:
        ser = serial.Serial(
            port=PORT,
            baudrate=CURRENT_BAUD,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=IDLE_TIMEOUT
        )
        print(f"Raw Dumper: {PORT} @ {CURRENT_BAUD} baud | Logs to {LOG_FILE}")
        print("Press A0 (medium + 2s hold), note time. Then C8. Ctrl+C to stop...\n")

        with open(LOG_FILE, 'w') as f:
            f.write("Timestamp,Bytes\n")

        while True:
            if ser.in_waiting > 0:
                chunk = ser.read(ser.in_waiting)
                timestamp = time.strftime('%H:%M:%S.%f')[:-3]
                line = f"[{timestamp}] {hex_dump(chunk)}"
                print(line)
                with open(LOG_FILE, 'a') as f:
                    f.write(f"{timestamp},{chunk.hex()}\n")
            time.sleep(0.001)  # Fast poll

    except KeyboardInterrupt:
        print("\nStopped. Check keybed_raw.txt for hex dump!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if ser:
            ser.close()

if __name__ == "__main__":
    main()
