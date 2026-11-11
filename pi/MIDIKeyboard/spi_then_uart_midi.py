#!/usr/bin/env python3
# Replays the mainboard's SPI boot MOSI → then opens UART @31250 and bridges to ALSA
# Uses velocity reconstruction like Plan A (config toggles at top)

import os, sys, time
import spidev, serial, mido
from mido import Message
import RPi.GPIO as GPIO

# -------- CONFIG --------
# Enable/Reset (white) - active LOW
EN_PIN = 17
PULSE_MS = 100
PULSE_POLARITY = "high"   # "low" (active-low) or "high" (active-high)

# SPI0 (Pi pins: MOSI GPIO10/p19, MISO GPIO9/p21, SCLK GPIO11/p23, CE0 GPIO8/p24)
SPI_BUS, SPI_DEV = 0, 0
SPI_MODE = 3                 # try 3 first; if no luck, try 0
SPI_SPEED_HZ = 500_000       # safe start; can increase

# --- Paste MOSI boot bytes here (from your capture) ---
BOOT_MOSI = [
    0xFF,0xF7,0xFF,0xDF,0xF7,0xBF,0xAF,0xAD,0xAD,0xBF,0xFF,0xF5,0xF7,0xFF,
    0xDB,0x9F,0xD1,0x4F,0xFF,0x7D,  # stop before the long FF,FF flood
]
PAIR_GAP_MS   = 0            # set 10–20ms if the STM32 misses bytes
POST_SPI_PAUSE_MS = 50       # small settle before UART

# UART for runtime MIDI-ish stream from STM32
UART_PORTS = [os.environ.get("UART",""), sys.argv[1] if len(sys.argv)>1 else "",
              "/dev/serial0","/dev/ttyS0","/dev/ttyAMA0"]
UART_BAUD = 31250
FORCE_CHANNEL = True
CHANNEL_NUMBER = 1
# Velocity reconstruction options (same as Plan A)
USE_RECONSTRUCT = True   # True = use nibble-hack; False = pass d2 as-is
LSB_BITS = 3             # 3 or 4 (try 3 first; 4 gives finer steps)
IGNORE_VELOCITY = False
FIXED_VEL = 100
SCALE_ON = True;  SCALE_MIN = 10; SCALE_MAX = 127
SCALE_OFF = False; SCALE_OFF_MIN = 1; SCALE_OFF_MAX = 64
# -----------------------

def pick_uart():
    for p in UART_PORTS:
        if p and os.path.exists(p): return p
    raise SystemExit("No UART found; pass explicit device or enable serial0.")

def pulse_enable(pin, ms, polarity):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    idle   = GPIO.HIGH if polarity=="low" else GPIO.LOW
    active = GPIO.LOW  if polarity=="low" else GPIO.HIGH
    GPIO.output(pin, idle); time.sleep(0.05)
    print(f"[EN] Pulse {polarity.upper()} {ms}ms")
    GPIO.output(pin, active); time.sleep(ms/1000.0)
    GPIO.output(pin, idle); time.sleep(0.05)

def spi_send(mosi_bytes):
    if not mosi_bytes: return
    spi = spidev.SpiDev(); spi.open(SPI_BUS, SPI_DEV)
    spi.mode = SPI_MODE; spi.max_speed_hz = SPI_SPEED_HZ
    print(f"[SPI] mode{SPI_MODE} @{SPI_SPEED_HZ}Hz sending {len(mosi_bytes)} bytes")
    if PAIR_GAP_MS <= 0:
        spi.xfer2(mosi_bytes)
    else:
        for b in mosi_bytes:
            spi.xfer2([b])
            time.sleep(PAIR_GAP_MS/1000.0)
    spi.close()

def clamp(v): return 0 if v<0 else (127 if v>127 else int(v))

def reconstruct_velocity(status_byte, byte3):
    if not USE_RECONSTRUCT: return byte3 & 0x7F
    nib = status_byte & 0x0F
    msb = 15 - nib
    if LSB_BITS == 4: return clamp((msb<<4) | (byte3 & 0x0F))
    else:             return clamp((msb<<3) | (byte3 & 0x07))

def scale_vel(v, note_on=True):
    if v<=0: return 0
    if note_on:
        if not SCALE_ON: return v
        a,b=SCALE_MIN,SCALE_MAX
    else:
        if not SCALE_OFF: return v
        a,b=SCALE_OFF_MIN,SCALE_OFF_MAX
    return clamp(int(round(a + (v/127.0)*(b-a))))

def force_ch(st):
    if not FORCE_CHANNEL: return st
    if 0x80<=st<=0xEF:
        return (st & 0xF0) | ((CHANNEL_NUMBER-1)&0x0F)
    return st

def main():
    try:
        pulse_enable(EN_PIN, PULSE_MS, PULSE_POLARITY)
    except Exception as e:
        print("[EN] warn:", e)

    # SPI boot
    spi_send(BOOT_MOSI)
    time.sleep(POST_SPI_PAUSE_MS/1000.0)

    # UART runtime
    port = pick_uart()
    ser = serial.Serial(port, UART_BAUD, timeout=0)
    try:
        out = mido.open_output("PiKeybed Out", virtual=True)
    except Exception:
        out = mido.open_output()

    print(f"[UART] {port} @ {UART_BAUD} → ALSA '{out.name}'")
    RUN=None; NEED=0; D1=None

    def send(st,d1=None,d2=None):
        st = force_ch(st); t = st & 0xF0; ch = st & 0x0F
        if IGNORE_VELOCITY and t in (0x90,0x80):
            d2 = FIXED_VEL if d2 is None else FIXED_VEL
        if t==0x90 and d2 is not None: out.send(Message('note_on', channel=ch, note=d1, velocity=d2))
        elif t==0x80 and d2 is not None: out.send(Message('note_off', channel=ch, note=d1, velocity=d2))
        elif t==0xB0 and d2 is not None: out.send(Message('control_change', channel=ch, control=d1, value=d2))
        elif t==0xC0 and d1 is not None: out.send(Message('program_change', channel=ch, program=d1))
        elif t==0xD0 and d1 is not None: out.send(Message('aftertouch', channel=ch, value=d1))
        elif t==0xE0 and d2 is not None:
            pb = ((d2&0x7F)<<7)|(d1&0x7F); out.send(Message('pitchwheel', channel=ch, pitch=pb-8192))

    while True:
        n = ser.in_waiting
        if not n:
            time.sleep(0.00005); continue
        data = ser.read(n)
        for b in data:
            if 0xF8 <= b <= 0xFF:   # ignore realtime
                continue
            if b & 0x80:
                if b >= 0xF0: RUN=None; NEED=0; D1=None; continue
                RUN=b; NEED=1 if (b&0xF0) in (0xC0,0xD0) else 2; D1=None; continue
            if RUN is None: continue
            if NEED==2:
                D1=b; NEED=1; continue
            # NEED==1 final data
            t = RUN & 0xF0
            if t==0x90:
                vel = reconstruct_velocity(RUN, b if D1 is not None else 0)
                vel = scale_vel(vel, note_on=True)
                if vel==0: send(0x80 | (RUN & 0x0F), D1, 0)
                else:      send(0x90 | (RUN & 0x0F), D1, vel)
            elif t==0x80:
                v = scale_vel(b, note_on=False)
                send(RUN, D1, v)
            else:
                send(RUN, D1, b)
            RUN=None; NEED=0; D1=None

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("\nStopped.")
