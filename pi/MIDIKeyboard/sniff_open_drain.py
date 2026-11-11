#!/usr/bin/env python3
"""
SPI burst sniffer with open-drain /CS emulation
------------------------------------------------
GPIO22 -> /CS (through ~470Ω)
GPIO23 -> SCLK input
GPIO24 -> MOSI input
"""

import RPi.GPIO as GPIO
import time

# --- pin config ---
CS   = 22   # open-drain emulated
SCLK = 23
MOSI = 24

# --- setup ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(SCLK, GPIO.IN)
GPIO.setup(MOSI, GPIO.IN)
GPIO.setup(CS, GPIO.IN)  # released (hi-Z)

def cs_assert():
    """Drive /CS LOW (sink the line)"""
    GPIO.setup(CS, GPIO.OUT, initial=GPIO.LOW)

def cs_release():
    """Release /CS (let pull-up bring it HIGH)"""
    GPIO.setup(CS, GPIO.IN)

def read_burst(timeout=0.01):
    """
    Capture MOSI bits on rising edges of SCLK for a short burst.
    timeout: max seconds to wait
    """
    start = time.perf_counter()
    bits = []
    prev_clk = GPIO.input(SCLK)
    while time.perf_counter() - start < timeout:
        clk = GPIO.input(SCLK)
        if clk and not prev_clk:  # rising edge
            bits.append(GPIO.input(MOSI))
        prev_clk = clk
    return bits

def bits_to_hex(bits):
    if not bits:
        return "(no data)"
    while len(bits) % 8:
        bits.append(0)
    out = []
    for i in range(0, len(bits), 8):
        byte = 0
        for b in bits[i:i+8]:
            byte = (byte << 1) | b
        out.append(f"{byte:02X}")
    return " ".join(out)

# --- main loop ---
print("Sniffer running. Pulsing /CS every 1s. Ctrl-C to stop.")
try:
    while True:
        cs_assert()
        time.sleep(0.5)         # hold low for 2 ms
        bits = read_burst(0.02)   # read for 20 ms
        cs_release()
        print(bits_to_hex(bits))
        time.sleep(1.0)

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
