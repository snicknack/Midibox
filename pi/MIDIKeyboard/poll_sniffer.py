#!/usr/bin/env python3
# Poll-capable UART sniffer for STM32 keyboard mini board
# Works on Raspberry Pi (python3 + gpiozero) or Pico (MicroPython)

import time, sys

# ===== Select your platform =====
USE_GPIOZERO = True     # False if running on Pico/MicroPython

# ===== Configuration =====
PORT   = '/dev/serial0' # Pi UART port
BAUD   = 38400
CTRL_PIN = 18           # active-low control line
POLL_PERIOD_MS = 1000     # how often to poll
LOW_PULSE_US   = 15000    # length of low pulse
SEND_CMD_BYTE  = None   # e.g. b'\x01' if STM expects byte poll, else None
READ_WINDOW_MS = 20     # time to read after each poll
MAX_BYTES_PRINT = 64

# ===== Platform-specific setup =====
if USE_GPIOZERO:
    import serial
    from gpiozero import LED
    ctrl = LED(CTRL_PIN)          # behaves as push-pull; we’ll fake open-drain
    uart = serial.Serial(PORT, BAUD, timeout=READ_WINDOW_MS/1000)
else:
    # --- MicroPython version ---
    from machine import Pin, UART
    ctrl = Pin(CTRL_PIN, Pin.IN)  # released (hi-Z)
    uart = UART(0, BAUD)

def ctrl_pulse_low():
    """briefly pull the control line low (open-drain style)."""
    if USE_GPIOZERO:
        ctrl.off()                # drive low
        time.sleep(LOW_PULSE_US / 1e6)
        ctrl.on()                 # release (idle high)
    else:
        ctrl.init(Pin.OUT)
        ctrl.value(0)
        time.sleep_us(LOW_PULSE_US)
        ctrl.init(Pin.IN)

def poll_once():
    """Send one hardware (and optional software) poll, then read reply."""
    # 1. Optional command byte
    if SEND_CMD_BYTE:
        uart.write(SEND_CMD_BYTE)
    # 2. Hardware low pulse
    ctrl_pulse_low()
    # 3. Read reply window
    t0 = time.time()
    data = b''
    while (time.time() - t0) * 1000 < READ_WINDOW_MS:
        chunk = uart.read(MAX_BYTES_PRINT)
        if not chunk:
            continue
        data += chunk
    if data:
        print('RX', len(data), 'bytes:', ' '.join(f'{b:02X}' for b in data))
    else:
        print('RX 0 bytes')

def main():
    print(f'Polling {PORT}@{BAUD}, ctrl={CTRL_PIN}, every {POLL_PERIOD_MS} ms')
    try:
        while True:
            poll_once()
            time.sleep(POLL_PERIOD_MS / 1000)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        if USE_GPIOZERO:
            ctrl.on()              # leave released

if __name__ == '__main__':
    main()
