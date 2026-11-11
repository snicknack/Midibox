#!/usr/bin/env python3
# Complete UART Sniffer for Raspberry Pi 4 + Optional Control Line Monitor
# Sniffs bidirectional serial (STM32 <-> Converter) and tries to monitor handshake/control wire.
# Connections:
# - Pi GPIO14 (Pin 8) -> Target RX line (sniff outbound to converter)
# - Pi GPIO15 (Pin 10) -> Target TX line (sniff inbound from converter)
# - Pi GPIO18 (Pin 12) -> Control/Handshake wire (e.g., RTS/IRQ) *optional*
# - Pi GND (e.g., Pin 6) -> Shared circuit GND
# Setup:
# - sudo raspi-config > Interface Options > Serial > No shell, Yes hardware
# - Add 'dtoverlay=disable-bt' to /boot/firmware/config.txt, reboot
# - sudo pip3 install pyserial (if needed)
# - Run: sudo python3 uart_sniffer_full.py
# Usage: Logs hex packets and control pulses (if wired). Ctrl+C to stop.

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
CONTROL_ENABLED = True  # Set to False to skip GPIO edge detection if issues

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
    """Initialize GPIO for control pin monitoring (with error handling)."""
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(CONTROL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        if CONTROL_ENABLED:
            GPIO.add_event_detect(CONTROL_PIN, GPIO.BOTH, callback=control_callback, bouncetime=50)
            print(f"  - Control: GPIO{CONTROL_PIN} (edge detection enabled)")
        else:
            print(f"  - Control: GPIO{CONTROL_PIN} (monitoring disabled)")
        return True
    except RuntimeError as e:
        print(f"  - Control: GPIO{CONTROL_PIN} setup failed: {e}. Skipping edge detection.")
        # Fallback: Poll manually if needed, but for now, just disable
        return False
    except Exception as e:
        print(f"  - Control: Unexpected GPIO error: {e}. Skipping.")
        return False

def setup_serial():
    """Open serial port for sniffing."""
    try:
        ser = serial.Serial(
            port=PORT,
            baudrate=BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=IDLE_TIMEOUT  # For non-blocking-ish reads
        )
        return ser
    except serial.SerialException as e:
        raise Exception(f"Serial setup failed: {e}. Check port, baud, wiring.")

def main():
    ser = None
    gpio_ok = False
    try:
        gpio_ok = setup_gpio()
        ser = setup_serial()
        print(f"Sniffer started:")
        print(f"  - UART: {PORT} @ {BAUDRATE} baud (GPIO{UART_TX_PIN} TX, GPIO{UART_RX_PIN} RX)")
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
                # Only log raw chunks if small/debug mode; comment out if too verbose
                # print(f"Raw chunk: {hex_dump(chunk)}")

            # Flush buffer if conditions met
            now = time.time()
            if (b'\n' in buffer or
                len(buffer) >= BUFFER_FLUSH_SIZE or
                (now - last_activity > IDLE_TIMEOUT and buffer)):
                
                if buffer:
                    timestamp = time.strftime("%H:%M:%S")
                    # Simple heuristic for direction (customize based on your protocol)
                    direction = "TX -> Converter" if len([b for b in buffer if b > 0x7F]) > 0 else "RX <- Converter"
                    print(f"[{timestamp}] {direction}: {hex_dump(buffer)}")
                    buffer.clear()
                    last_activity = now

            # Optional: Manual poll for control if edge detect failed
            if not gpio_ok and CONTROL_ENABLED:
                state = GPIO.input(CONTROL_PIN)
                if state == GPIO.HIGH:  # Or track changes manually
                    print(f"[{time.strftime('%H:%M:%S')}] CONTROL GPIO{CONTROL_PIN}: HIGH (polled)")

            time.sleep(0.01)  # Low CPU usage

    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if ser:
            ser.close()
        if gpio_ok or CONTROL_ENABLED:
            GPIO.cleanup()
        print("Cleanup done. Port closed, GPIO reset.")

if __name__ == "__main__":
    main()
