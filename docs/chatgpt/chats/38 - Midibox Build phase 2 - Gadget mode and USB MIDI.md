# Midibox Build phase 2 - Gadget mode and USB MIDI

- ChatGPT conversation id: 68db1952-b1e4-8327-adbb-754d7f884d3a
- Created: 2025-09-29 23:43
- Updated: 2025-09-29 23:53
- Project: Midibox raspberry pi
- Messages: 2

## User · 2025-09-29 23:43

Ok this is following on from midibox build phase 1. 

Phase two is to add gadget mode and usb midi implementation 

## Assistant · 2025-09-29 23:43

Perfect 👍 we’re moving into the fun part now — making the Pi behave like a real USB MIDI device.  

Here’s how we can break down **Phase 2: Gadget Mode + USB MIDI implementation**:  

---

## 1. Gadget Mode Basics
- Gadget mode allows the Pi (Zero / Zero 2 / 3A+ / 4 in OTG mode) to act as a **USB device** rather than a host.  
- This lets your Pi present itself to your computer as “USB MIDI,” just like a hardware synth or controller.  

To enable:
1. Add `dtoverlay=dwc2` to `/boot/config.txt`.
2. Add `modules-load=dwc2,g_serial` (or later `g_midi`) to `/boot/cmdline.txt` after `rootwait`.
   - `g_serial` → simple USB serial
   - `g_midi` → actual USB MIDI class device  

⚠️ Important: On Pi Zero / 3A+, the micro-USB marked “USB” must be used (not the “PWR IN”).  

---

## 2. Load the USB MIDI Gadget
- Instead of `g_serial`, load the **MIDI gadget module**:
  ```bash
  sudo modprobe g_midi
  ```
- Or add it permanently:
  ```bash
  echo "g_midi" | sudo tee -a /etc/modules
  ```

After reboot, when you connect the Pi to your Mac/PC via the OTG port, it should show up as a **USB MIDI device** (e.g. “Linux USB MIDI Gadget”).  

---

## 3. Bridge Gadget MIDI to ALSA MIDI
Once gadget mode is up, ALSA will see two ends:
- **Device end (USB connection to your host)**
- **Local ALSA ports (to/from your sequencer or synth software running on the Pi)**  

Use **`aconnect`** to route:
```bash
aconnect -l     # lists ALSA MIDI ports
aconnect 20:0 128:0
```
(where `20:0` is your USB MIDI Gadget and `128:0` could be a softsynth or MIDI thru port).  

For testing, install `aseqdump`:
```bash
aseqdump -p 20:0
```
Press a MIDI key from your computer → should print out Note On/Off messages.  

---

## 4. Integration with Midibox Build
- Now that the Pi can “pretend” to be a MIDI device, you can map incoming MIDI messages from your DAW → your hardware layer (GPIO, encoders, buttons, etc.).  
- Outgoing control (knobs, buttons on your build) can be translated into MIDI CC/Note messages and sent out through `g_midi` back to your DAW.  

---

## 5. Next Step: Python/Custom MIDI Implementation
For handling MIDI logic, you can use:
- **Python (`mido`, `python-rtmidi`)**
- **C/C++ ALSA API** for lower latency  
- **JUCE** if you want cross-platform plugin/device code later  

---

👉 Do you want me to give you a **ready-to-use config file** for `/boot/config.txt` and `/boot/cmdline.txt` so you can just drop them in, or would you rather I walk you through setting up the OTG mode line by line?

