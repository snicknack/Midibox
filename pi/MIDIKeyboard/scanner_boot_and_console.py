#!/usr/bin/env python3
# Pulses ENABLE (white) then lets you send/receive hex over UART (blue/yellow).
# Wiring (BCM pins):
#   Yellow -> GPIO15 (RXD)  | Blue -> GPIO14 (TXD, add 1k series) | White -> GPIO17 (ENABLE, active-low, 1k series)

import os, sys, time, threading, serial
import RPi.GPIO as GPIO
PULSE_MS = 1000          # how long to hold the pin LOW
PULSE_POLARITY = "low" # "low" = active-low pulse  (set "high" if yours is active-high
BAUD = 31250
EN_PIN = 17  # white, active-low ENABLE/RESET

def pick_port():
    c = []
    if os.environ.get("UART"): c.append(os.environ["UART"])
    if len(sys.argv) > 1:      c.append(sys.argv[1])
    c += ["/dev/serial0", "/dev/ttyS0", "/dev/ttyAMA0"]
    for p in c:
        if p and os.path.exists(p): return p
    raise SystemExit("No UART found. Enable it via raspi-config (Serial Port), then reboot.")

PORT = pick_port()
print(f"Opening {PORT} @ {BAUD} (8N1)")
ser = serial.Serial(PORT, BAUD, timeout=0.02)
try: ser.reset_input_buffer()
except: pass

# ---- control line: configurable pulse ----
# GPIO.setmode(GPIO.BCM)
#GPIO.setup(EN_PIN, GPIO.OUT)

#idle = GPIO.HIGH if PULSE_POLARITY == "low" else GPIO.LOW
#active = GPIO.LOW if PULSE_POLARITY == "low" else GPIO.HIGH

#GPIO.output(EN_PIN, idle)
#time.sleep(0.05)
#print(f"Pulsing ENABLE {PULSE_POLARITY.upper()} for {PULSE_MS} ms...")
#GPIO.output(EN_PIN, active)
#time.sleep(PULSE_MS / 1000.0)
#GPIO.output(EN_PIN, idle)
#time.sleep(0.05)

# ---- try a few kick bytes ----
def send_bytes(bs):
    if not bs: return
    ser.write(bytes(bs))
    print(">> " + " ".join(f"{b:02X}" for b in bs))

print("Sending kick bytes...")
# send_bytes([0x00])
# time.sleep(0.05)
# send_bytes([0xFF, 0x00, 0xFF, 0x0B, 0xFF, 0x07])   # guessy 3-byte frame
# time.sleep(0.05)

# ---- background reader to show replies in HEX ----
_running = True
def reader():
    while _running:
        try:
            data = ser.read(512)
            if data:
                ts = time.strftime("%H:%M:%S.") + f"{int((time.time()%1)*1000):03d}"
                print("<< [%s] %s" % (ts, " ".join(f"{b:02X}" for b in data)))
        except Exception:
            time.sleep(0.01)

t = threading.Thread(target=reader, daemon=True); t.start()

print("\nInteractive HEX console. Type bytes like: 00   or   AA 01 00")
print("Commands: /repeat N <hex...> | /sleep ms | /kick | /quit\n")

try:
    while True:
        line = input("> ").strip()
        if not line: continue
        if line.startswith("/"):
            parts = line.split()
            cmd = parts[0].lower()
            if cmd in ("/quit","/q","/exit"): break
            if cmd == "/kick":
                send_bytes([0x00]); continue
            if cmd == "/sleep":
                try: time.sleep(max(0,int(parts[1]))/1000.0)
                except: print("Usage: /sleep ms")
                continue
            if cmd == "/repeat":
                if len(parts) < 3:
                    print("Usage: /repeat N <hex...>"); continue
                try: count = int(parts[1])
                except: print("Usage: /repeat N <hex...>"); continue
                # parse hex payload
                toks = " ".join(parts[2:]).replace(",", " ").split()
                try:
                    payload = [(int(x,16)&0xFF) for x in toks]
                except: print("Bad hex token"); continue
                for _ in range(max(0,count)):
                    send_bytes(payload)
                    time.sleep(0.01)
                continue
            print("Unknown command.")
            continue
        # raw hex line
        try:
            toks = line.replace(",", " ").split()
            payload = [(int(x,16)&0xFF) for x in toks]
            send_bytes(payload)
        except Exception as e:
            print("Bad hex:", e)
except KeyboardInterrupt:
    pass
finally:
    _running = False
    try: t.join(0.2)
    except: pass
    ser.close()
    GPIO.cleanup()
    print("\nClosed.")
