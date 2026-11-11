#!/usr/bin/env python3
# uart_hex_console.py — interactive HEX send/receive console @ 31,250 bps (MIDI speed)
# Use this to probe the STM32 link, send test bytes, and see responses in HEX.

import os, sys, time, threading, serial

BAUD = 31250

def pick_port():
    # Priority: env UART → CLI arg → serial0 → ttyS0 → ttyAMA0
    candidates = []
    if os.environ.get("UART"): candidates.append(os.environ["UART"])
    if len(sys.argv) > 1:      candidates.append(sys.argv[1])
    candidates += ["/dev/serial0", "/dev/ttyS0", "/dev/ttyAMA0"]
    for p in candidates:
        if p and os.path.exists(p):
            return p
    raise SystemExit("No UART device found. Enable it with 'sudo raspi-config' → Serial Port, then reboot.")

PORT = pick_port()
print(f"Opening {PORT} @ {BAUD} 8N1 ...")
ser = serial.Serial(PORT, BAUD, timeout=0.02)
try: ser.reset_input_buffer()
except Exception: pass

# -------- background reader --------
_running = True
def reader():
    while _running:
        try:
            data = ser.read(512)
            if data:
                ts = time.strftime("%H:%M:%S.") + f"{int((time.time()%1)*1000):03d}"
                print("<< [%s] %s" % (ts, " ".join(f"{b:02X}" for b in data)))
        except Exception:
            # keep console alive even if a read hiccups
            time.sleep(0.01)

t = threading.Thread(target=reader, daemon=True)
t.start()

# -------- helpers --------
def parse_hex_line(s: str):
    """Return list of integers from a string like 'AA 01 00' (hex, case-insensitive)."""
    vals = []
    for tok in s.replace(",", " ").split():
        tok = tok.strip()
        if not tok:
            continue
        if tok.startswith("#"):
            break  # comment to end of line
        if tok.lower().startswith("0x"):
            tok = tok[2:]
        try:
            vals.append(int(tok, 16) & 0xFF)
        except ValueError:
            raise ValueError(f"Bad hex token: {tok}")
    return vals

def send_bytes(bs):
    if not bs:
        return
    ser.write(bytes(bs))
    print(">> " + " ".join(f"{b:02X}" for b in bs))

# -------- banner --------
print("Interactive HEX console. Type hex bytes and press Enter (e.g., '00' or 'AA 01 00').")
print("Commands: /repeat N <hex...> | /sleep ms | /kick | /help | /quit")
print("Press Ctrl-C or type /quit to exit.\n")

# -------- main loop --------
try:
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        if not line:
            continue

        if line.startswith("/"):
            cmd = line.split()
            name = cmd[0].lower()

            if name in ("/quit", "/exit", "/q"):
                break

            if name == "/help":
                print("Commands:")
                print("  /repeat N <hex...>   send the sequence N times")
                print("  /sleep ms            delay (milliseconds) – useful between /repeat steps")
                print("  /kick                send single 00 byte")
                print("  /quit                exit")
                print("Examples:")
                print("  /repeat 5 AA 01 00")
                print("  00")
                continue

            if name == "/kick":
                send_bytes([0x00])
                continue

            if name == "/sleep":
                if len(cmd) != 2:
                    print("Usage: /sleep ms")
                    continue
                try:
                    ms = int(cmd[1])
                    time.sleep(max(0, ms) / 1000.0)
                except Exception as e:
                    print("Bad ms:", e)
                continue

            if name == "/repeat":
                if len(cmd) < 3:
                    print("Usage: /repeat N <hex...>")
                    continue
                try:
                    count = int(cmd[1])
                except:
                    print("Usage: /repeat N <hex...>")
                    continue
                try:
                    payload = parse_hex_line(" ".join(cmd[2:]))
                except Exception as e:
                    print(e)
                    continue
                for _ in range(max(0, count)):
                    send_bytes(payload)
                    # tiny gap so the STM32 isn't swamped
                    time.sleep(0.01)
                continue

            print("Unknown command. Try /help.")
            continue

        # raw hex line
        try:
            bytes_out = parse_hex_line(line)
            send_bytes(bytes_out)
        except Exception as e:
            print(e)

except KeyboardInterrupt:
    pass
finally:
    _running = False
    try: t.join(timeout=0.2)
    except: pass
    ser.close()
    print("\nClosed.")

