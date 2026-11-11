#!/usr/bin/env python3
# midibox_midi_bridge.py
# Streams keybed UART data -> USB MIDI (Note/Aftertouch)

import serial, time, mido

PORT = '/dev/serial0'
BAUD = 38400
POLL_DELAY_MS = 10

# --- helper functions ---
def hexs(bs): return ' '.join(f'{b:02X}' for b in bs)

def open_uart():
    return serial.Serial(PORT, BAUD, timeout=0.01,
                         bytesize=serial.EIGHTBITS,
                         parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE)

# --- create virtual MIDI port ---
out = mido.open_output('Midibox Keyboard', virtual=True)
print("✅  Virtual MIDI port 'Midibox Keyboard' ready.")
print("   (Plug your Crave via USB and select this port.)")

# --- simple byte parser for your v3 stream ---
ser = open_uart()
running = None

def parse_stream():
    """reads 3-byte note msgs like 0x90 0x15 0x29 etc."""
    global running
    while ser.in_waiting:
        b = ser.read(1)[0]
        if b & 0x80:             # status byte
            running = b
            buf = ser.read(2)
            if len(buf) < 2: return
            status, d1, d2 = b, buf[0], buf[1]
        else:                     # running status continuation
            if running is None: return
            buf = bytes([b]) + ser.read(2)
            if len(buf) < 3: return
            status, d1, d2 = running, buf[0], buf[1]

        cmd = status & 0xF0
        ch  = status & 0x0F
        if cmd == 0x90 and d2 > 0:
            note = d1; vel = d2
            out.send(mido.Message('note_on', note=note, velocity=vel, channel=ch))
            print(f"Note ON  {note:3d} vel{vel:3d}")
        elif cmd in (0x80, 0x90) and d2 == 0:
            note = d1
            out.send(mido.Message('note_off', note=note, velocity=0, channel=ch))
            print(f"Note OFF {note:3d}")
        elif cmd == 0xD0:  # Channel Pressure / AT
            out.send(mido.Message('aftertouch', value=d1, channel=ch))
            print(f"AT {d1}")
        else:
            print("??", status, d1, d2)

try:
    while True:
        parse_stream()
        time.sleep(POLL_DELAY_MS/1000)
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    ser.close()
