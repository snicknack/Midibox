#!/usr/bin/env python3
# scanner_handshake_sender.py
# Raspberry Pi 4 → STM32 keybed scanner
#  - Pulses ENABLE (active-low) on a GPIO
#  - Sends a captured handshake: pairs of FF <byte> at 31,250 bps (MIDI rate)
#  - Prints any replies in HEX with timestamps
#
# Wiring (BCM numbering):
#   Yellow (STM32 TX) -> Pi RXD  (GPIO15 / physical pin 10)
#   Blue   (STM32 RX) <- Pi TXD  (GPIO14 / physical pin 8) **put ~1k series resistor**
#   White  (ENABLE)   <- Pi GPIO17 (physical pin 11) **series resistor ok; active-low**
#   GND <-> GND (e.g., physical pin 6)
#
# Requirements:
#   sudo apt install python3-serial
#   pip3 install pyserial
#   (RPi.GPIO is preinstalled on Raspberry Pi OS)

import os, sys, time, threading
import serial
import RPi.GPIO as GPIO

# ---------------- Config (edit here) ----------------
UART_PORTS_TRY = [
    os.environ.get("UART", "").strip(),
    sys.argv[1].strip() if len(sys.argv) > 1 else "",
    "/dev/serial0", "/dev/ttyS0", "/dev/ttyAMA0",
]
BAUD_MAIN = 31250          # primary TX/RX baud (MIDI rate)
BAUD_ALT  = 115200         # optional "alt try" baud for TX only (see TRY_ALT_BAUD)
TRY_ALT_BAUD = False       # set True to also try the same sequence at BAUD_ALT

EN_PIN = 17                # BCM pin for ENABLE/RESET (white), active-low
PULSE_MS = 100             # hold ENABLE active for this many ms
PULSE_POLARITY = "low"     # "low" for active-low enable, "high" for active-high

# Handshake pairs captured from the main board (order matters)
# Each entry is the single byte following 0xFF
HANDSHAKE_BYTES = [
    0x00, 0x0B, 0x07, 0x00, 0x01, 0x02, 0x07, 0x03,
    0x1F, 0x33, 0x01, 0x03, 0x0D, 0x03, 0x00, 0x02,
    0x01, 0x01, 0x00, 0x08, 0x01, 0x01, 0x0B, 0x0D,
    0x01, 0x00, 0x03, 0x02, 0x03, 0x04, 0x16,
]
REPEAT_BLOCKS = 2          # send the whole block this many times
DELAY_BETWEEN_PAIRS_MS = 15
DELAY_BETWEEN_BLOCKS_MS = 120

# After handshake, keep listening (seconds). Set 0 for no hold.
POST_LISTEN_SECONDS = 5
# ---------------------------------------------------

def pick_port():
    for p in UART_PORTS_TRY:
        if p and os.path.exists(p):
            return p
    raise SystemExit("No UART found. Enable it via raspi-config (Serial Port), then reboot.")

def make_serial(port, baud):
    ser = serial.Serial(port, baud, timeout=0.02)
    try: ser.reset_input_buffer()
    except: pass
    return ser

def pulse_enable(pin, ms, polarity="low"):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    idle   = GPIO.HIGH if polarity == "low" else GPIO.LOW
    active = GPIO.LOW  if polarity == "low" else GPIO.HIGH
    GPIO.output(pin, idle)
    time.sleep(0.05)
    print(f"[EN] Pulsing {polarity.upper()} for {ms} ms...")
    GPIO.output(pin, active)
    time.sleep(ms/1000.0)
    GPIO.output(pin, idle)
    time.sleep(0.05)

def hexline(b: bytes) -> str:
    return " ".join(f"{x:02X}" for x in b)

_running = True
def reader_thread(ser):
    while _running:
        try:
            data = ser.read(512)
            if data:
                ts = time.strftime("%H:%M:%S.") + f"{int((time.time()%1)*1000):03d}"
                print(f"<< [{ts}] {hexline(data)}")
        except Exception:
            time.sleep(0.01)

def send_handshake_block(ser, delay_ms):
    # send FF,byte pairs with spacing
    for b in HANDSHAKE_BYTES:
        frame = bytes((0xFF, b & 0xFF))
        ser.write(frame)
        print(">> " + hexline(frame))
        time.sleep(max(0, delay_ms)/1000.0)

def run_sequence(ser, blocks, pair_gap_ms, block_gap_ms, label="MIDI-31250"):
    print(f"[SEND] Handshake '{label}' — {blocks}x blocks, {pair_gap_ms} ms/pair, {block_gap_ms} ms between blocks")
    for i in range(blocks):
        send_handshake_block(ser, pair_gap_ms)
        if i < blocks - 1:
            time.sleep(max(0, block_gap_ms)/1000.0)

def main():
    global _running
    port = pick_port()
    print(f"[UART] Opening {port} @ {BAUD_MAIN} 8N1")
    ser = make_serial(port, BAUD_MAIN)

    # start reader
    t = threading.Thread(target=reader_thread, args=(ser,), daemon=True)
    t.start()

    # pulse enable/reset
    try:
        pulse_enable(EN_PIN, PULSE_MS, PULSE_POLARITY)
    except Exception as e:
        print("[EN] Warning:", e)

    # small settle
    time.sleep(0.05)

    # primary sequence at 31,250
    run_sequence(ser, REPEAT_BLOCKS, DELAY_BETWEEN_PAIRS_MS, DELAY_BETWEEN_BLOCKS_MS, "MIDI-31250")

    # optional alt-baud attempt (close/reopen at BAUD_ALT, TX the pairs again)
    if TRY_ALT_BAUD:
        print(f"[UART] Trying alt TX baud {BAUD_ALT} (RX prints may be gibberish if the scanner answers at 31,250)")
        try:
            ser.close()
            ser = make_serial(port, BAUD_ALT)
            # keep reader alive on the same ser handle
            # (for simplicity we won’t respawn the thread—small risk if reopening fails)
            run_sequence(ser, REPEAT_BLOCKS, DELAY_BETWEEN_PAIRS_MS, DELAY_BETWEEN_BLOCKS_MS, f"ALT-{BAUD_ALT}")
        except Exception as e:
            print("[ALT] Skipped alt-baud try:", e)
        finally:
            try:
                ser.close()
            except: pass
            # reopen at main baud for listening
            ser = make_serial(port, BAUD_MAIN)

    # listen a bit for changes/normal MIDI
    if POST_LISTEN_SECONDS > 0:
        print(f"[WAIT] Listening for {POST_LISTEN_SECONDS}s … press Ctrl-C to stop early.")
        deadline = time.time() + POST_LISTEN_SECONDS
        try:
            while time.time() < deadline:
                time.sleep(0.05)
        except KeyboardInterrupt:
            pass

    _running = False
    time.sleep(0.1)
    try: ser.close()
    except: pass
    GPIO.cleanup()
    print("[DONE] Closed.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        _running = False
        GPIO.cleanup()
        print("\n[ABORT] Interrupted.")
