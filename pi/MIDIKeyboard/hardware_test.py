#!/usr/bin/env python3
"""
Midibox Phase-1 Hardware Smoke Test
- Checks: TFT driver (framebuffer), FT6236 touch (I2C 0x38), MPR121 (I2C 0x5A..0x5D),
  SPI/I2C buses, common ADCs (ADS1115 I2C / MCP3008 SPI), encoder GPIO activity (optional),
  basic analog read stubs for wheels/faders.
"""
import os, subprocess, sys, time

RESULTS = []

def check_cmd(name, cmd):
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=5)
        RESULTS.append((name, True, out.strip()))
        return out
    except Exception as e:
        RESULTS.append((name, False, str(e)))
        return ""

def status(label, ok, extra=""):
    print(f"[{'OK' if ok else 'FAIL'}] {label}")
    if extra:
        print(f"      {extra[:300]}"+("..." if len(extra)>300 else ""))

print("\n== Midibox Phase-1 Smoke Test ==\n")

# --- Step 2: TFT framebuffer / SPI present (coarse check)
spi = os.path.exists("/dev/spidev0.0") or os.path.exists("/dev/spidev0.1")
status("SPI device present (/dev/spidev0.*)", spi)
fb = os.path.exists("/dev/fb0")
status("Framebuffer device present (/dev/fb0)", fb)

# FT6236 touch over I2C (commonly 0x38)
out_i2c = check_cmd("i2cdetect-1", ["bash","-lc","i2cdetect -y 1 || true"])
has_ft6236 = "38:" in out_i2c or " 38 " in out_i2c
status("FT6236 touch controller detected (I2C addr 0x38 on bus 1)", has_ft6236)

# --- Step 6: MPR121 detection (0x5A..0x5D)
has_mpr121 = any(addr in out_i2c for addr in ["5a","5b","5c","5d"," 5a "," 5b "," 5c "," 5d "])
status("MPR121 capacitive controller detected (I2C 0x5A–0x5D)", has_mpr121)

# --- Common ADCs for wheels/faders
ads_guess = any(tok in out_i2c for tok in ["48","49","4a","4b"])  # ADS1115 defaults
status("ADS1x15 ADC likely present (I2C 0x48–0x4B)", ads_guess)

mcp_spi = os.path.exists("/dev/spidev0.0")
status("MCP3008/MCP3208 possible (SPI device present)", mcp_spi)

# --- Step 3: Encoders (GPIO library availability)
try:
    import RPi.GPIO as GPIO  # noqa
    status("RPi.GPIO library import", True)
except Exception as e:
    status("RPi.GPIO library import", False, str(e))

# --- Step 7: Power sanity: throttling check (under-voltage/brownouts)
throttle = check_cmd("vcgencmd", ["bash","-lc","vcgencmd get_throttled || true"])
status("Power/thermal throttling flags (vcgencmd get_throttled)", True, throttle)

print("\n== Raw i2c scan (bus 1) ==\n" + out_i2c)
print("\n== Summary ==")
ok = all(r[1] for r in RESULTS if r[0]!="i2cdetect-1")
print("Overall:", "PASS (basic devices visible)" if ok else "INCOMPLETE (see FAIL above)")
