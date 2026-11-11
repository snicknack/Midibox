#!/usr/bin/env python3
# midibox_serial_to_midi.py  –  Pi4 bridge from STM32 UART -> USB MIDI
import serial, time, mido

PORT = '/dev/serial0'
BAUD = 38400
out = mido.open_output('Midibox Keyboard', virtual=True)

print("✅  Virtual MIDI port 'Midibox Keyboard' created.")
print("   Run `aconnect -l` to confirm, then route it to your synth.\n")

ser = serial.Serial(PORT, BAUD, timeout=0.01)
running = None

while True:
    if ser.in_waiting:
        b = ser.read(1)[0]
        if b & 0x80:                     # new status byte
            running = b
            data = ser.read(2)
            if len(data) < 2: continue
            msg = bytes([b]) + data
        else:                             # running-status continuation
            if running is None: continue
            data = bytes([b]) + ser.read(2)
            if len(data) < 2: continue
            msg = bytes([running]) + data[:2]

        status, d1, d2 = msg
        cmd = status & 0xF0
        ch  = status & 0x0F

        if cmd == 0x90 and d2 > 0:
            out.send(mido.Message('note_on', note=d1, velocity=d2, channel=ch))
            print(f"Note ON  n={d1:3d} v={d2:3d}")
        elif cmd in (0x80, 0x90) and d2 == 0:
            out.send(mido.Message('note_off', note=d1, velocity=0, channel=ch))
            print(f"Note OFF n={d1:3d}")
        elif cmd == 0xD0:
            out.send(mido.Message('aftertouch', value=d1, channel=ch))
            print(f"AT {d1}")
        else:
            # optional debug
            print(f"?? {msg.hex(' ')}")

    time.sleep(0.001)
