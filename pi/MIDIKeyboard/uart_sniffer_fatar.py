#!/usr/bin/env python3
# Fatar Keybed UART Sniffer: Parses Scans for Velocity + Aftertouch
# Assumes ~16-byte packets; logs key hits, vel hints. Exports to file.
# Connections: Same (Pins 8/TX, 10/RX, 12/Control w/ pull-up, GND).
# Run: sudo python3 uart_sniffer_fatar.py

import serial
import time
import sys
import RPi.GPIO as GPIO

# Configuration
CURRENT_BAUD = 115200
PORT = '/dev/serial0'
UART_TX_PIN = 14
UART_RX_PIN = 15
CONTROL_PIN = 18
PACKET_SIZE = 16  # Target; pads with 00
IDLE_TIMEOUT = 0.05  # Shorter for fast scans
FAST_POLL = True
POLL_INTERVAL = 0.002
DEBOUNCE_MS = 5
LOG_FILE = "keybed_log.txt"  # For export

def hex_dump(data, full=False):
    """Pretty-print; full=show all bytes."""
    data = data[:PACKET_SIZE]  # Trim to expected
    hex_str = ' '.join(f'{b:02X}' for b in data)
    asc_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data)
    vel_hint = "Vel/AT: " + ", ".join(f"~{b}(key?)" for b in data[4:12] if b > 0 and b < 128)
    return f"[{len(data)}B] {hex_str} | {asc_str} | {vel_hint if vel_hint != 'Vel/AT: ' else 'Idle scan'}"

class Debouncer:
    """Debounce for pulses."""
    def __init__(self, cooldown_ms):
        self.last_low_time = 0
        self.cooldown_ms = cooldown_ms / 1000.0

    def should_alert(self, now):
        if now - self.last_low_time > self.cooldown_ms:
            self.last_low_time = now
            return True
        return False

def control_poll(channel, debouncer, now):
    """Poll for LOW (data ready)."""
    state = GPIO.input(channel)
    if state == GPIO.LOW and debouncer.should_alert(now):
        print(f"[{time.strftime('%H:%M:%S.%f')[:-3]}] CONTROL LOW: Scan incoming!")

def setup_gpio():
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(CONTROL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print(f"  - Control: GPIO{CONTROL_PIN} (fast-polling w/ debounce)")
        return True, Debouncer(DEBOUNCE_MS)
    except Exception as e:
        print(f"  - Control failed: {e}. Disabling.")
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

def log_to_file(line):
    """Append to log file."""
    with open(LOG_FILE, 'a') as f:
        f.write(f"{time.strftime('%H:%M:%S.%f')[:-3]} {line}\n")

def main():
    ser = None
    gpio_ok = False
    debouncer = None
    log_fd = open(LOG_FILE, 'w')  # Clear old log
    log_fd.close()
    try:
        gpio_ok, debouncer = setup_gpio()
        ser = setup_serial(CURRENT_BAUD)
        print(f"Sniffer started (Fatar mode): Logs to {LOG_FILE}")
        print(f"  - UART: {PORT} @ {CURRENT_BAUD} baud")
        print("  Ctrl+C to stop...\n")

        buffer = bytearray()
        last_activity = time.time()
        packet_count = 0

        while True:
            now = time.time()
            # Poll control
            if gpio_ok:
                control_poll(CONTROL_PIN, debouncer, now)

            # Read serial
            if ser.in_waiting > 0:
                chunk = ser.read(ser.in_waiting)
                buffer.extend(chunk)
                last_activity = now

                # Build packets (greedy: take multiples of PACKET_SIZE)
                while len(buffer) >= PACKET_SIZE:
                    packet = buffer[:PACKET_SIZE]
                    packet_count += 1
                    dump = hex_dump(packet)
                    timestamp = time.strftime('%H:%M:%S.%f')[:-3]
                    line = f"Scan #{packet_count} TX->Conv: {dump}"
                    print(f"[{timestamp}] {line}")
                    log_to_file(line)
                    buffer = buffer[PACKET_SIZE:]  # Shift

            # Flush partial if timeout (rare for scans)
            elif now - last_activity > IDLE_TIMEOUT and buffer:
                if len(buffer) > 0:
                    dump = hex_dump(buffer)
                    timestamp = time.strftime('%H:%M:%S.%f')[:-3]
                    line = f"Partial Scan: {dump}"
                    print(f"[{timestamp}] {line}")
                    log_to_file(line)
                    buffer.clear()

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print(f"\nStopped. Processed {packet_count} scans. Check {LOG_FILE} for full dump.")
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
