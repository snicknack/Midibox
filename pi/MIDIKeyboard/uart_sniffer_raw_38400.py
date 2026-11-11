#!/usr/bin/env python3
# Raw Hex Dumper for Fatar: Locked to 38400 Baud (From Scan)
# Bigger reads for bursts. Logs to console + keybed_raw_38400.txt
# Run: sudo python3 uart_sniffer_raw_38400.py

import serial
import time
import sys

CURRENT_BAUD = 38400  # From scan results
PORT = '/dev/serial0'
READ_TIMEOUT = 0.2  # Longer for bursts
LOG_FILE = "keybed_raw_38400.txt"

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
            timeout=READ_TIMEOUT
        )
        print(f"Raw Dumper: {PORT} @ {CURRENT_BAUD} baud | Logs to {LOG_FILE}")
        print("Idle 5s. Press A0 medium + 2s hold AT at [time]. Idle 5s. C8 same. Ctrl+C...\n")

        with open(LOG_FILE, 'w') as f:
            f.write("Timestamp,Bytes Hex\n")

        while True:
            chunk = ser.read(ser.in_waiting or 1)  # Non-block if empty
            if chunk:
                timestamp = time.strftime('%H:%M:%S.%f')[:-3]
                line = f"[{timestamp}] {hex_dump(chunk)}"
                print(line)
                with open(LOG_FILE, 'a') as f:
                    f.write(f"{timestamp},{chunk.hex(sep=' ')}\n")
            time.sleep(0.005)  # Light poll

    except KeyboardInterrupt:
        print("\nStopped. Check keybed_raw_38400.txt!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if ser:
            ser.close()

if __name__ == "__main__":
    main()
