#!/usr/bin/env python3
# Baud Rate Scanner for Fatar: Tests Common Rates for Structured Data
# Run: sudo python3 baud_scan.py | tee scan_log.txt

import serial
import time
import sys

PORT = '/dev/serial0'
BAUD_OPTIONS = [9600, 19200, 38400, 57600, 115200]  # Start with 57600?
MIN_CHUNK = 5  # Flag if >5B (packet-like)

def hex_dump(data):
    if len(data) < MIN_CHUNK:
        return None
    hex_str = ' '.join(f'{b:02X}' for b in data)
    return f"Activity [{len(data)}B]: {hex_str}"

def main():
    print(f"Scanning {PORT} on {BAUD_OPTIONS}...")
    print("Press A0/C8 during a rate to test. Ctrl+C to stop.\n")
    
    for baud in BAUD_OPTIONS:
        try:
            print(f"--- Trying {baud} baud (5s wait) ---")
            ser = serial.Serial(
                port=PORT,
                baudrate=baud,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1
            )
            start_time = time.time()
            while time.time() - start_time < 5:
                if ser.in_waiting >= MIN_CHUNK:
                    chunk = ser.read(ser.in_waiting)
                    dump = hex_dump(chunk)
                    if dump:
                        print(f"  {dump}")
                time.sleep(0.01)
            ser.close()
            print("  No activity.")
        except Exception as e:
            print(f"  Error at {baud}: {e}")
    
    print("\nDone. Rerun raw dumper at best baud.")

if __name__ == "__main__":
    main()
