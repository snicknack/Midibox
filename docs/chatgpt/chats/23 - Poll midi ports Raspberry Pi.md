# Poll midi ports Raspberry Pi

- ChatGPT conversation id: 68e6ffb1-96bc-8330-8a79-ce89d198615c
- Created: 2025-10-09 00:20
- Updated: 2025-10-09 13:04
- Project: Midibox raspberry pi
- Messages: 2

## User · 2025-10-09 00:20

How do I poll midi ports on raspberry pi

## Assistant · 2025-10-09 00:20

Good question — let’s cover this step by step 👇  

You can **poll (list and read)** MIDI ports on a Raspberry Pi in a few ways depending on what kind of MIDI you’re dealing with (USB, UART, or virtual ALSA ports).  

---

## 🎹 1. Checking available MIDI devices (ALSA level)

First, check that the system sees the MIDI ports:

```bash
aconnect -l
```

This lists all **ALSA sequencer clients and ports**, e.g.:

```
client 20: 'USB MIDI Interface' [type=kernel]
    0 'USB MIDI Interface MIDI 1'
client 128: 'TiMidity' [type=user]
    0 'TiMidity port 0'
```

If you don’t see your device, check:

```bash
lsusb
```

or for serial MIDI (UART):

```bash
dmesg | grep tty
```

---

## 🐍 2. Polling MIDI ports in Python

For custom controllers and synth interfaces, Python is a great option using the **`mido`** or **`rtmidi`** libraries.

### Install:
```bash
sudo apt install python3-rtmidi
pip install mido python-rtmidi
```

### List available ports:
```python
import mido

print("Input ports:")
for port in mido.get_input_names():
    print(port)

print("\nOutput ports:")
for port in mido.get_output_names():
    print(port)
```

### Poll for incoming MIDI messages:
```python
import mido

with mido.open_input() as inport:
    print(f"Listening on: {inport.name}")
    for msg in inport:
        print(msg)
```

That loop blocks (polls continuously).  
If you want to **poll non-blocking**, you can use `poll()` or a timeout-based approach:

```python
import mido
import time

inport = mido.open_input()

while True:
    msg = inport.poll()
    if msg:
        print(msg)
    time.sleep(0.01)
```

---

## 💡 3. Using `amidi` (raw terminal)

If you want to **test directly from the terminal**, you can use:
```bash
amidi -l
```
To list MIDI devices. Then:
```bash
amidi -p hw:1,0,0 -d
```
to dump all incoming MIDI bytes from that port (you’ll see raw hex data).

---

## 🧩 4. UART MIDI (GPIO pins)

If you’re using the Pi’s UART pins for hardware MIDI:
1. Disable serial console and enable UART in `raspi-config`.
2. Connect TX to the MIDI DIN input through an optocoupler (for in) or driver transistor (for out).
3. Then check `/dev/ttyAMA0` or `/dev/serial0`.

To monitor serial MIDI at 31250 baud:
```bash
sudo stty -F /dev/serial0 31250 raw
cat /dev/serial0
```

---

## 🧠 TL;DR summary

| Goal | Command / Code |
|------|----------------|
| List ALSA MIDI ports | `aconnect -l` |
| List hardware devices | `lsusb` |
| Test MIDI port | `amidi -p hw:1,0,0 -d` |
| Poll in Python (blocking) | `for msg in inport: print(msg)` |
| Poll in Python (non-blocking) | `msg = inport.poll()` |
| UART test | `cat /dev/serial0` at 31250 baud |

---

Would you like me to show a **Python script that polls all connected ports at once** and prints messages tagged with their port name (handy for multi-device setups like your Midibox)?

