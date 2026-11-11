#!/usr/bin/env python3
# Complete UART Sniffer for Raspberry Pi 4 + Control Line Monitor
# Sniffs bidirectional serial (STM32 <-> Converter) and monitors handshake/control wire.
# Connections:
# - Pi GPIO14 (Pin 8) -> Target RX line (sniff outbound to converter)
# - Pi GPIO15 (Pin 10) -> Target TX line (sniff inbound from converter)
# - Pi GPIO18 (Pin 12) -> Control/Handshake wire (e.g., RTS/IRQ)
# - Pi GND (e.g., Pin 6) -> Shared circuit GND
# Setup:
# - sudo raspi-config > Interface Options > Serial > No shell, Yes hardware
# - Add 'dtoverlay=disable-bt' to /boot/firmware/config.txt, reboot
# - sudo pip3 install pyserial (if needed)
# - Run: sudo python3 uart_sniffer_full.py
# Usage: Logs hex packets and control pulses. Ctrl+C to stop.

import serial
import time
import sys
import RPi.GPIO as GPIO

# Configuration
BAUDRATE = 9600  # Match your protocol (e.g., 9600, 115200)
PORT = '/dev/serial0'
UART_TX_PIN = 14  # GPIO14 (not used for output here, just config)
UART_RX_PIN = 15  # GPIO15
CONTROL_PIN = 18  # GPIO18 for handshake monitoring
BUFFER_FLUSH_SIZE = 32  # Flush buffer if >= this many bytes (or on \n)
IDLE_TIMEOUT = 0.1  # Seconds to wait for more data before flushing

def hex_dump(data):
    """Pretty-print bytes as hex with ASCII."""
    if not data:
        return "[]"
    hex_str = ' '.join(f'{b:02X}' for b in data)
    asc_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data)
    return f"[{len(data)} bytes] {hex_str} | {asc_str}"

def control_callback(channel):
    """Interrupt handler for control line pulses."""
    state = GPIO.input(channel)
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] CONTROL GPIO{channel}: {'HIGH' if state else 'LOW'} (edge detected)")

def setup_gpio():
    """Initialize GPIO for control pin monitoring."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(CONTROL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(CONTROL_PIN, GPIO.BOTH, callback=control_callback, bouncetime=50)

def setup_serial():
    """Open serial port for sniffing."""
    ser = serial.Serial(
        port=PORT,
        baudrate=BAUDRATE,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=IDLE_TIMEOUT  # For non-blocking-ish reads
    )
    return ser

def main():
    ser = None
    try:
        setup_gpio()
        ser = setup_serial()
        print(f"Sniffer started:")
        print(f"  - UART: {PORT} @ {BAUDRATE} baud (GPIO{UART_TX_PIN} TX, GPIO{UART_RX_PIN} RX)")
        print(f"  - Control: GPIO{CONTROL_PIN} (edges logged)")
        print("  - Packets flushed on {BUFFER_FLUSH_SIZE} bytes, \\n, or {IDLE_TIMEOUT}s idle")
        print("  Ctrl+C to stop...\n")

        buffer = bytearray()
        last_activity = time.time()

        while True:
            # Read available serial data
            if ser.in_waiting > 0:
                chunk = ser.read(ser.in_waiting)
                buffer.extend(chunk)
                last_activity = time.time()
                print(f"Raw chunk: {hex_dump(chunk)}")  # Log raw for debugging

            # Flush buffer if conditions met
            now = time.time()
            if (b'\n' in buffer or
                len(buffer) >= BUFFER_FLUSH_SIZE or
                (now - last_activity > IDLE_TIMEOUT and buffer)):
                
                if buffer:
                    timestamp = time.strftime("%H:%M:%S")
                    direction = "TX -> Converter" if any(b > 0x7F for b in buffer) else "RX <- Converter"  # Heuristic; adjust
                    print(f"[{timestamp}] {direction}: {hex_dump(buffer)}")
                    buffer.clear()
                    last_activity = now

            time.sleep(0.01)  # Low CPU usage

    except KeyboardInterrupt:
        print("\nStopped by user.")
    except serial.SerialException as e:
        print(f"Serial error: {e}")
        print("Check: Wiring, baudrate, /dev/serial0 exists, Bluetooth disabled.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if ser:
            ser.close()
        GPIO.cleanup()
        print("Cleanup done. Port closed, GPIO reset.")

if __name__ == "__main__":
    main()
