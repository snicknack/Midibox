# Fader pin configuration explanation

- ChatGPT conversation id: 68e09fda-b29c-8332-8fe0-388c3f95696f
- Created: 2025-10-04 04:17
- Updated: 2025-10-04 04:37
- Project: Midibox raspberry pi
- Messages: 25

## User · 2025-10-04 04:17

Why are the faders 6pin? 

## Tool (file_search) · 2025-10-04 04:17

> MidiBox Design Overview



Two Long Throw Faders for CC 



Transport Control via the MPR121 capacitive Touch

	Start, Stop, Rec, Jog L, Jog R, Loop, 



Pitch and Mod Wheel 



Fatar Midi Keyboard

	Aftertouch

	Velocity

	88 Keys



Touch Screen FT6236 and 

	

	Page 1

	Midi Transpose

	Midi Octave up/down

	Display Chords Played 

	Display 4 touch encoder parameters



	Page 2 - Arpeggiator

	Scale Major minor etc.

	Up/Down/Chord



	Page 3 - 2 Faders and 4 touch sensitive encoders Setup page

	Allow Change cc out of 2 faders

	Assign Touch sensitive encoders to internal functions such as midi transpose octave jump

	Or assign touch encoders to cc.



	Page 4 - Select USB Midi Out (for devices on USB-A ports



USB Midi out 

	USB-A allows class compliant midi devices such as synthesizers

	USB-C Allows connection to Class compliant Hosts such as OSX (gadget)





Other features

	Swipe functions 

	UI Design using a library such as Ktinter or Kivy, PyQt and PySide

	

Optional

RGB Leds available for suggestionsas previously tested

Buttons available for suggestions

	

	

Code Requirements



Skeleton Main.py - Not Bulky and full of code

Multiple Files/Modules for each Requirement (gestures, UI, Midi USB-C, Midi USB-A, Midi Scales CC and Transport functions.

Allows for Updates and my learning.

(When Project is complete) = Boot direct into Program with Boot Screen and no need for Pi OS interaction.













Hardware Equipment 



PI 4

Ft6236 3.2”TFT SPI  TouchScreen 240 x 320

MPR121 Break out (adafruit)

Midi and Pitch Wheels (analogue)

4 Smooth Encoders with Capacitive functionality and Clickable

Capacitive Pads for Transport Functions Not Purchased yet (make recommendations)

3D Printer for Case

Will need to create a 2M cable going from the FATAR Keyboard to my Midi Box

## Tool (file_search) · 2025-10-04 04:17

All the files uploaded by the user have been fully loaded. Searching won't provide additional information.

## Assistant · 2025-10-04 04:17

The faders in your design are **6-pin because they’re not just simple 3-pin potentiometers**. Long-throw MIDI faders often include extra tracks or switches beyond the basic resistive element. The common reasons are:  

1. **Dual-gang (stereo) design** – Two separate resistive tracks in one fader, each with 3 pins. That makes 6 pins total (3 per track). This is useful if you want to read the same movement twice (for redundancy, smoothing, or CV + MIDI output), or if the fader is intended for stereo audio.  

2. **Touch-sensing faders** – Some MIDI-controller faders (motorized or touch-sensitive) add an extra track or conductive strip so the system can detect when your finger is on the fader. That requires additional pins.  

3. **Integrated switches at end of travel** – Certain faders include a small switch at the top or bottom, triggered when you push the fader fully up/down, and those switch contacts add extra pins.  

So in short:  
- **3 pins = standard potentiometer track.**  
- **6 pins = either 2 tracks (dual-gang) or 1 track + touch/switch pins.**  

Do you know the part number of your faders? That will confirm if they’re dual-gang or touch-sensitive. Would you like me to cross-check that with the model you ordered for the Midibox?

## User · 2025-10-04 04:20

Is there a fader that can report its current position so it can allow a dead band between switching presets where it’s say 10% and should be 80% 

## Assistant · 2025-10-04 04:20

Yes 👍 — what you’re describing is usually called a **“pickup” or “soft takeover”** function, and there are two main ways it’s achieved:  

---

### 1. **With Standard Faders (most common in MIDI controllers)**
- A regular fader (potentiometer) can’t “report its position” by itself; it only outputs its voltage divider value.  
- The **controller firmware** handles the deadband logic:  
  - When you switch presets, the current value in software (say 80%) may not match the physical fader (say 10%).  
  - Instead of jumping immediately, the software ignores fader movement until the physical position crosses close to the stored value (within a deadband you set, e.g. ±5%).  
  - Once the fader “catches up,” control is handed back and it moves smoothly.  

➡️ This is how Ableton, MPC, and most MIDI gear implement smooth preset changes with ordinary faders.  
You’d just code this in your Midibox firmware.  

---

### 2. **With Motorized Faders (studio mixers, high-end MIDI controllers)**
- Motorized faders **do report their absolute position** because they’re still potentiometers, but they also have a **servo motor** that can physically move the fader to the correct position when presets change.  
- These are more complex: you need motor driver circuitry, feedback reading, and safety logic to prevent sudden jumps.  
- Examples: **ALPS motorized faders**, **Penny & Giles conductive plastic motorized faders**.  

➡️ These give you both absolute feedback *and* physical alignment with stored values, so no deadband is needed — the fader physically moves to the right place.  

---

### 3. **Digital/Optical Faders**
- Less common but available in some pro-audio gear.  
- They use encoders or optical strips that directly output an absolute digital value, which can be queried at startup.  
- Same idea: firmware manages the deadband, unless paired with motors.  

---

✅ **For your Midibox:**  
- If you don’t want the expense/complexity of motorized faders, the best solution is **regular faders + firmware deadband logic**.  
- When switching presets, you store the “target CC value,” and only re-engage control once the fader crosses into a ±10% window.  

Would you like me to sketch out a **Python module for your Midibox** that adds this pickup/deadband logic for the two long-throw faders mentioned in your design doc?

## User · 2025-10-04 04:23

How could we implement these? Would the software need to callback the new position of the midi cc to the pi in order to not jump on moving the fader? How could we do this with one of these 

## Assistant · 2025-10-04 04:23

Great follow-up. When I said **digital/optical faders**, I meant “fader-like position sensors that provide an **absolute digital reading** (via I²C/SPI or pulses), instead of a plain analog wiper.” That lets your firmware do super-reliable **pickup/soft-takeover** without needing motors.

Here’s how to implement it cleanly.

# What a “digital/optical fader” actually is
- **Magnetic linear encoder + strip** (practical + robust): a tiny IC reads a magnet attached to the fader carriage over a magnetic scale/strip and gives you absolute position (I²C/SPI or high-res quadrature).  
- **Optical linear encoder**: a LED + sensor reads a coded/striped scale; you get absolute or incremental counts.  
- **Hall/3D-Hall sensor**: a 3D Hall IC (I²C) under the slot, magnet on the slider. Calibrate min/max to get absolute 0–100% travel.

Any of these gives a **stable, absolute 0–100%** every scan—no analog noise, no scratchy tracks.

# Do we need “callback” of the DAW/synth value?
There are two scenarios:

1) **Local-only control (no host feedback):**  
You can still avoid jumps with **firmware pickup**:
- Keep a “target value” for each mapped parameter (e.g., 80%).  
- Read the digital fader continuously (say 0–1023 → 0–127).  
- **Ignore movement** until the physical fader enters a **deadband** around the target (e.g., ±4).  
- When it enters, “latch” and start sending live CCs.

2) **Bidirectional control (best):**  
If the DAW/synth **sends back** the current parameter (CC/NRPN echo, SysEx, Mackie/HUI, or **MIDI 2.0** Property Exchange), your Pi should **listen and update the target value** immediately when presets change externally. Then your pickup logic uses the **true live** value, not just whatever you last sent.  
- If your device/DAW doesn’t send parameter feedback, you can’t know the new value—so you must rely on your own stored value or preset database.

# Hardware patterns that work
- **Magnetic linear (absolute)**: e.g., a linear magnetic encoder IC (I²C/SPI) + magnet on the fader carriage. Mechanically it feels like a normal long-throw slider; electrically you read a clean absolute number.  
- **Optical linear (incremental + index)**: use quadrature counting with an index mark. On boot, run a quick **reference pass** to find index (or use endstop). Store counts in NVRAM to survive reboots.  
- **3D Hall (I²C) under the slot**: simplest build—mount the sensor on your PCB, glue a tiny magnet to the slider nub. Do a one-time calibration (min/max ADC) and map to 0–127.

# Firmware logic (soft-takeover with deadband + hysteresis)
- Maintain, per fader:
  - `target_cc` (the value currently in the synth/DAW)
  - `latched` (bool: are we following live yet?)
- On preset change or incoming MIDI feedback, set `target_cc` and `latched=False`.
- Each scan:
  - `phys = read_fader_abs()`  # 0..127 after scaling
  - If not latched:
    - If `abs(phys - target_cc) <= DEAD_BAND` → `latched=True`
  - If latched:
    - If `abs(phys - last_sent) >= STEP_THRESH` → send CC and update `last_sent`
- Use a small **hysteresis** (e.g., latch at ±4, unlatch only if you leave ±6) to keep it stable.

Tiny Python sketch (fits your Pi stack; plug your sensor read in `read_fader_abs()`):

```python
DEAD_BAND = 4      # ±4 around target to latch
STEP_THRESH = 1    # send only if moved >= 1

class SoftTakeoverFader:
    def __init__(self):
        self.target_cc = 64
        self.latched = False
        self.last_sent = 64

    def on_external_param(self, cc_val):  # from DAW/synth MIDI in
        self.target_cc = cc_val
        self.latched = False

    def tick(self):
        phys = read_fader_abs()  # -> int 0..127 from your digital/optical sensor
        if not self.latched:
            if abs(phys - self.target_cc) <= DEAD_BAND:
                self.latched = True
                self.last_sent = phys
                send_cc(phys)
        else:
            if abs(phys - self.last_sent) >= STEP_THRESH:
                self.last_sent = phys
                send_cc(phys)
```

# Wiring & CPU notes (Pi)
- **I²C/SPI absolute encoders**: easy, low CPU. Poll at 500–1000 Hz for smoothness.  
- **Quadrature (optical/magnetic incremental)**: use an RP2040/Arduino coprocessor to count in hardware interrupts, then publish counts to the Pi over I²C/USB-Serial. This avoids missed pulses at fast moves.  
- **Noise immunity**: magnetic/optical sensors are far less noisy than analog pots—great for smooth MIDI.

# When would you still want motors?
If you need the **physical** fader to move to match the preset (live show with no pickup time), only a **motorized fader** can do that. Digital/optical gives you perfect sensing and pickup, but won’t move itself.

---

If you tell me which route you like (magnetic I²C, optical quadrature, or 3D Hall), I’ll drop in a ready-to-use module for your Midibox (readout driver + soft-takeover class + ALSA MIDI glue).

## User · 2025-10-04 04:27

[file: IMG_A35A9E4E-3B7D-49EE-B3DE-B51E3162183D.jpeg (file_00000000b73c62469c7fcd6eaf3cfd48)]

[image file_00000000b73c62469c7fcd6eaf3cfd48 1536x1152]
Is this an optical fader? 

## Assistant · 2025-10-04 04:27

Yes — the **Behringer Infinium X1** is indeed an **optical fader**.  

🔎 From the product description in your screenshot:  
- *“Ultra-Long Life With Contact-Free Optical Technology”*  
- *“High Digital Precision With 128 Positions”*  

That means:  
- Instead of a resistive carbon track (like normal faders), it uses **an LED + optical sensor** to detect the slider’s position.  
- No mechanical wear, since there’s no wiper dragging across a resistive strip.  
- The onboard PCB converts the optical sensing into a digital output (in the case of the DDM4000 mixer, the microcontroller reads it as 128 steps = 7-bit resolution, perfect for MIDI CC).  

---

✅ **Why this is good for your Midibox project:**  
- It already gives you absolute position (0–127), so you can implement soft-takeover/pickup logic directly in software.  
- Because it’s contact-free, it’s much more durable and won’t get scratchy like a pot.  
- It’s designed to feel like a normal long-throw fader with adjustable magnetic friction, so the playability is the same.  

---

⚡ One thing to check:  
The Infinium X1 was designed as a **drop-in spare for Behringer mixers**, so it probably outputs either:  
- A raw analog voltage (already linearized from the optical sensor), **or**  
- A digital signal that the mixer’s microcontroller interprets.  

Would you like me to dig into the **pinout and output signal format** of the Infinium X1, so we know whether you can wire it straight into the Pi’s ADC (like a normal pot), or if you’ll need a small interface board?

## User · 2025-10-04 04:29

I really want to try two of these over resistive potentiometers can you think of something cool they could do with midi over the potentiometers 

## Assistant · 2025-10-04 04:29

That’s a wicked idea 👌 — optical faders like the **Infinium X1** open up possibilities you just can’t do with scratchy resistive pots. Since they’re **contact-free, absolute, and digitally smooth**, you can treat them more like expressive controllers than just “volume sliders.”  

Here are some **cool MIDI ideas** you could try that go beyond a normal pot fader:  

---

## 🎛 1. Multi-mode Faders (switchable function)
- **Preset-aware:** Assign the fader to different CCs depending on the preset (Filter cutoff, Reverb wet/dry, Granular stretch).  
- **Dual mapping:** Bottom half of the fader sends one CC, top half sends another.  
- **Page layers:** Use your touchscreen (FT6236) to select “page,” and the fader instantly maps to that layer’s parameters.  

---

## 🎚 2. Gesture-based MIDI (because optical reads smoothly)
- **Velocity fader:** Measure the *speed* of the fader move and send velocity-like MIDI messages or trigger modulation bursts.  
- **Acceleration mapping:** Faster moves = more dramatic parameter sweeps, slower moves = fine-tuning.  
- **Throw modulation:** When you slam the fader quickly from top to bottom, send a MIDI note or trigger an FX stab.  

---

## 🌓 3. Zone-based Expression
- Divide the fader into zones:
  - **0–25%** = dry/wet reverb.  
  - **25–50%** = filter cutoff.  
  - **50–75%** = delay feedback.  
  - **75–100%** = master volume.  
- LEDs (WS2811 strips you mentioned earlier) could light up according to the zone.  

---

## 🎹 4. Touch + Position Hybrid
Since the Infinium fader is *contact-free*, you can add a **capacitive touch strip** (like the SX1509 or MPR121) alongside it:  
- Only send CCs when it’s touched.  
- Tap to reset to default CC value.  
- Hold + slide = alternate parameter.  

---

## 🌀 5. Audio-Rate CV Tricks
Because the optical fader is so smooth, you could sample it at high rate and use it almost like a **live CV source**:  
- Map it to modulate a wavetable position in Serum/Falcon.  
- Use it to scrub sample position in real time (MIDI CC to Ableton Simpler/Granular).  
- Combine with LFO so fader sets **LFO depth** or **rate**.  

---

## 🏎 6. Motorized-fader-style pickup (without the motor!)
- Use **deadband/pickup logic** like we discussed: the fader “catches” parameter control only when it passes near the current preset value.  
- Add a visual indicator (RGB LED next to the fader) showing whether it’s “latched” to the synth parameter yet.  
- This mimics how pro gear feels, but without the motor.  

---

## 🔮 7. Creative FX Mode
- Put fader into a **macro sequencer mode**:
  - Fader position = morph index between 4–8 parameter snapshots (CC maps).  
  - As you slide, it morphs EQ, filter, reverb, and pan all at once.  

---

✨ In short: compared to resistive pots, these optical faders are **smooth, durable, and absolute** — which makes them ideal for **gesture, zoning, and expressive multi-mapping** rather than just “volume up/down.”  

---

Would you like me to mock up a **Python class for Midibox** that wraps one Infinium fader and gives it these extra MIDI modes (standard CC, velocity-based, zone-based, macro morph)? That way you could drop them in and switch modes with a single parameter.

## User · 2025-10-04 04:31

Holy crap! Sounds amazing I’m buying two right now! 

## Assistant · 2025-10-04 04:31

🔥 Haha, that’s the spirit! Two Infiniums in the Midibox will make it feel like a **pro DJ mixer meets modular MIDI brain**. You’ll have silky-smooth faders that never wear out, perfect for expressive control instead of just “volume sliders.”  

If you grab them, here’s what I’d suggest as a next step when they arrive:  

1. **Pinout check** → confirm what the Infinium is outputting (most likely an analog voltage, but could be digital stepped).  
2. **Quick test rig** → wire one to an ADS1115 or Pi ADC channel, print raw values, and check resolution/linearity.  
3. **Write a fader class** → we can wrap all those cool modes (standard CC, zone, velocity, pickup, macro-morph).  
4. **Visual feedback** → pair with a WS2811 strip or RGB LED next to the fader to show which mode it’s in and whether it’s “latched.”  
5. **Preset integration** → connect with your soft-takeover logic so they smoothly follow DAW/MIDI preset changes.  

⚡️ These could become the *signature hands-on control* of your Midibox — way more expressive than resistive pots.  

Do you want me to start drafting the **Python fader class skeleton** now, so you’ll have it ready to drop in once the hardware lands?

## User · 2025-10-04 04:34

[file: IMG_014078FF-13BF-4FC9-A0C3-E6E6E458D976.jpeg (file_000000009a78623098a89db728072618)]

[image file_000000009a78623098a89db728072618 1536x1152]
From searching forums it’s serial output 

## Assistant · 2025-10-04 04:34

Nice find—that forum post is gold. If the Infinium X1 really speaks **31250-baud serial (0–127 steps)**, you can treat each fader like a little MIDI-style TX device and read it directly on the Pi.

Here’s the practical plan:

## Pinout (per the post you found)
Weird colors, but reported as:
- **RED → GND**
- **BLACK (edge) → +3.3 V**
- **MIDDLE BLACK → DATA @ 31250 baud** (this is the fader’s TX; on the mixer it’s labeled RX)

So on your Pi:
- Fader **DATA → Pi RX** (GPIO15, pin 10, or another UART RX)
- Fader **GND → Pi GND**
- Fader **+3.3 V → Pi 3V3** (check current draw; usually tiny)

> 31250 baud and 0–127 screams **MIDI-like 8N1**. It’s TTL, not a current loop, so no MIDI opto needed.

## Two faders on a Pi
- The Pi has **one full PL011 UART (ttyAMA0)** and a **mini-UART (ttyS0)**. You can enable both and read **two faders** simultaneously.  
- Alternative: plug one or two **USB-serial** dongles and read them as `/dev/ttyUSB0/1`.  
- If you’d rather offload, an **RP2040** can read both and forward via I²C/USB.

## Minimal test (Python + pyserial)
```python
import serial

ser = serial.Serial('/dev/ttyAMA0', baudrate=31250, bytesize=8, parity='N', stopbits=1, timeout=0.01)

while True:
    b = ser.read(1)
    if b:
        val = b[0]         # expect 0..127
        print("Fader:", val)
```
Run a second instance on `/dev/ttyS0` (or `/dev/ttyUSB0`) for the other fader.

## What the stream looks like
Most likely it spits **single bytes 0–127** when you move, maybe also idle repeats. If you see frames (e.g., `0xF0 val 0xF7`), just parse and take the middle byte.

## Integrate pickup/deadband
Once you’re reading values, drop them into the soft-takeover logic we discussed:
- Keep `target_cc` from the preset/host.
- **Latch** when `abs(fader - target_cc) ≤ deadband`.
- Send CC while latched; ignore until latched.

## Gotchas / checks
- Make sure the Pi UART isn’t grabbed by the console; disable serial console, enable UARTs in `raspi-config`.
- If values look inverted, map `val = 127 - val`.
- If the forum’s “RX” wording confuses: it’s **RX from the mixer’s perspective**. For you, treat that pin as **TX from the fader → RX on Pi**.
- If the stream is noisy, add a 3–5 sample moving average before CC output.

If you want, I’ll whip up a tiny **`infinium_fader.py`** class that:
- Opens a given UART,
- Reads bytes, debounces/averages,
- Exposes 0–127,
- And includes a **mode switch** for standard, zone, velocity, and pickup behaviors.

## User · 2025-10-04 04:36

So to confirm the two faders don’t steal the i/o of the other modules we’ve been developing preventing us from using them 

## Assistant · 2025-10-04 04:36

Short answer: **no, they don’t have to steal any I/O.** We can hang the two Infinium faders off interfaces that your other Midibox modules aren’t using.

Here are the clean options:

1) **USB-Serial (easiest, zero GPIO conflicts)**
- Give each fader a tiny **3.3 V USB-TTL serial dongle**.
- They show up as `/dev/ttyUSB0` and `/dev/ttyUSB1` at **31250 baud**.
- Leaves **I²C** (FT6236, MPR121, ADS1115, SX1509) and **SPI** (MAX7219) untouched.

2) **RP2040 bridge (one cable back to Pi)**
- A £4 Pico reads both faders’ serial lines and exposes two bytes over **I²C** (e.g., registers 0x00 and 0x01).
- Pi just reads them at 100–400 kHz; you only “spend” **SDA/SCL** which you already use—this is fine because I²C is a **bus**.

3) **Use Pi UARTs (if you want pure GPIO)**
- Enable the PL011 + mini-UART and wire each fader’s **DATA → a Pi RX**.
- This does mean touching UART config (and possibly Bluetooth routing) but still doesn’t collide with your I²C/SPI stuff.

Recommended for Midibox: **Option 1 or 2.**  
They keep your current plan intact:

- **I²C-1:** FT6236 (touch), MPR121 (caps pads), ADS1115 (analog), SX1509 (IO/LED) – address-unique, all good.  
- **SPI-0:** MAX7219 (LED matrix).  
- **USB:** MIDI gadget + class-compliant synths **and** (option 1) the two USB-serial faders.  

If you want, I’ll draft:
- a tiny **Python reader** for `/dev/ttyUSB0/1` (+ soft-takeover), **or**
- a **Pico firmware** + Pi-side I²C reader for the RP2040 bridge.

Which route do you prefer?

