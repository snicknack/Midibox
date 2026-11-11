#!/usr/bin/env python3
# Simple Raw Dumper: No Parsing, Just Hex Bursts
# Run: sudo python3 simple_raw.py

import serial
import time

CURRENT_BAUD = 38400
PORT = '/dev/serial0'

def hex_dump(data):
    hex_str = ' '.join(f'{b:02X}' for b in data)
    return f"[{len(data)}B] {hex_str}"

ser = serial.Serial(
    port=PORT,
    baudrate=CURRENT_BAUD,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=0.1
)
print(f"Raw Dumper: {PORT} @ {CURRENT_BAUD} baud")
print("Hard press A0 @ [time]. Idle 3s. C8 @ [time]. Ctrl+C...\n")

while True:
    chunk = ser.read(ser.in_waiting or 1)
    if chunk:
        timestamp = time.strftime('%H:%M:%S.%f')[:-3]
        print(f"[{timestamp}] {hex_dump(chunk)}")
    time.sleep(0.01)

ser.close()
