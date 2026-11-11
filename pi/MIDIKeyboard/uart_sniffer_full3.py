#!/usr/bin/env python3
# Robust UART Sniffer for Raspberry Pi 4 + Polling Control Monitor
# Disables edge detection; polls for active-low pulses. Verbose logging for debugging.
# Connections: Same as before (Pins 8/TX, 10/RX, 12/Control, GND).
# Setup: Same (raspi-config, disable-bt, pyserial).
# Run: sudo python3 uart_sniffer_robust.py
# Features: Baud scan mode (uncomment BAUD_SCAN), loopback test prompt.

import serial
import time
import sys
import RPi.GPIO as GPIO

# Configuration
BAUD_OPTIONS = [9600, 19200, 38400, 57600, 115200]  # Common rates; start with 115200?
CURRENT_BAUD = 115200  # Try this first—change or use scan
PORT = '/dev/serial0'
UART_TX_PIN = 14
UART_RX_PIN = 15
CONTROL_PIN = 18
BUFFER_FLUSH_SIZE = 32
IDLE_TIMEOUT = 0.1
CONTROL_ENABLED = True  # Polling always works
BAUD_SCAN = False  # Set True to auto-scan bauds (slow, for testing)
LOOPBACK_TEST = False  # Set True to prompt for loopback verification

def hex_dump(data):
    """Pretty-print bytes as hex with ASCII."""
    if not data:
        return "[0 bytes] (empty)"
    hex_str = ' '.join(f'{b:02X}' for b in data)
    asc_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data)
    return f"[{len(data)} bytes] {hex_str} | {asc_str}"

def control_poll(channel):
    """Poll for active-low control pulses (fallback from edge detect)."""
    if GPIO.input(channel) == GPIO.LOW:
        timestamp = time.strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] CONTROL GPIO{channel}: LOW - Data Ready on RX! (polled)")

def setup_gpio():
    """Setup GPIO with polling only (no edge detect)."""
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(CONTROL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print(f"  - Control: GPIO{CONTROL_PIN} (polling for LOW pulses enabled)")
        return True
    except Exception as e:
        print(f"  - Control: GPIO setup failed: {e}. Disabling.")
        return False

def setup_serial(baud):
    """Open serial port for sniffing."""
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
        raise Exception(f"Serial setup failed at {baud} baud: {e}. Check port/wiring.")

def loopback_test(ser):
    """Simple loopback: Send a test byte, expect echo."""
    print("Loopback test: Short TX (Pin 8) to RX (Pin 10). Sending 0xAA...")
    test_byte = b'\xAA'
    ser.write(test_byte)
    time.sleep(0.1)
    echo = ser.read(1)
    if echo == test_byte:
        print(f"  SUCCESS: Echoed {hex_dump(echo)}")
    else:
        print(f"  FAILED: Sent {hex_dump(test_byte)}, got {hex_dump(echo)}")
    print("Remove short for normal sniffing.\n")

def baud_scan():
    """Scan common bauds for activity."""
    print("Baud scan mode: Testing for data on each rate (press Ctrl+C to stop).")
    for baud in BAUD_OPTIONS:
        try:
            print(f"\n--- Trying {baud} baud ---")
            ser = setup_serial(baud)
            time.sleep(2)  # Wait for settle
            if ser.in_waiting > 0:
                chunk = ser.read(ser.in_waiting)
                print(f"  Activity detected: {hex_dump(chunk)}")
            else:
                print("  No data (yet).")
            ser.close()
        except Exception as e:
            print(f"  Scan error at {baud}: {e}")

def main():
    ser = None
    gpio_ok = False
    try:
        if LOOPBACK_TEST:
            gpio_ok = setup_gpio()
            ser = setup_serial(CURRENT_BAUD)
            loopback_test(ser)
            ser.close()
            return  # Exit after test

        if BAUD_SCAN:
            baud_scan()
            return  # Exit after scan

        gpio_ok = setup_gpio()
        ser = setup_serial(CURRENT_BAUD)
        print(f"Sniffer started:")
        print(f"  - UART: {PORT} @ {CURRENT_BAUD} baud (GPIO{UART_TX_PIN} TX, GPIO{UART_RX_PIN} RX)")
        print(f"  - Verbose: Logging every raw read (even empty)")
        print("  Ctrl+C to stop...\n")

        buffer = bytearray()
        last_activity = time.time()
        read_count = 0

        while True:
            # Read available serial data
            chunk_size = ser.in_waiting
            read_count += 1
            if chunk_size > 0:
                chunk = ser.read(chunk_size)
                buffer.extend(chunk)
                last_activity = time.time()
                print(f"[{time.strftime('%H:%M:%S.%f')[:-3]}] Raw RX read ({chunk_size} bytes): {hex_dump(chunk)}")
            else:
                if read_count % 100 == 0:  # Log empty every ~1s
                    print(f"[{time.strftime('%H:%M:%S')}] Idle: No data in_waiting=0")

            # Poll control
            if gpio_ok and CONTROL_ENABLED:
                control_poll(CONTROL_PIN)

            # Flush buffer if conditions met
            now = time.time()
            if (b'\n' in buffer or
                len(buffer) >= BUFFER_FLUSH_SIZE or
                (now - last_activity > IDLE_TIMEOUT and buffer)):
                
                if buffer:
                    timestamp = time.strftime("%H:%M:%S.%f")[:-3]
                    high_bits = len([b for b in buffer if b > 0x7F])
                    direction = "TX -> Converter" if high_bits > len(buffer)/2 else "RX <- Converter"
                    print(f"[{timestamp}] PACKET {direction}: {hex_dump(buffer)}")
                    buffer.clear()
                    last_activity = now

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if ser:
            ser.close()
        if gpio_ok:
            GPIO.cleanup()
        print("Cleanup done. Port closed, GPIO reset.")

if __name__ == "__main__":
    main()
