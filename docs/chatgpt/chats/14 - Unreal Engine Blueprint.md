# Unreal Engine Blueprint

- ChatGPT conversation id: 68f5e1ab-e994-8327-833b-793b400326eb
- Created: 2025-10-20 07:16
- Updated: 2025-10-20 07:17
- Project: Midibox raspberry pi
- Messages: 9

## User · 2025-10-20 07:15

[file: IMG_4A2C366D-1849-4912-98C8-2E2FE5D234A5.jpeg (file_0000000020a06243b70b23de33b2751e)]

[image file_0000000020a06243b70b23de33b2751e 1536x1152]
What program is that!

## Tool (file_search) · 2025-10-20 07:16

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

## Tool (file_search) · 2025-10-20 07:16

All the files uploaded by the user have been fully loaded. Searching won't provide additional information.

## Assistant · 2025-10-20 07:16

That screenshot shows a **visual scripting graph** — specifically from **Unreal Engine’s Blueprints Editor**.  

Here’s what gives it away:
- The **node-based layout** with execution pins (white arrows) and data pins (colored circles).  
- The **details panel** on the left listing variables, types, and default values.  
- Nodes like “Get Global Variable,” “Math Expression,” and “Set Scalar Parameter,” which are common in Unreal’s **Material or Animation Blueprint graphs**.  
- The light grey grid background and dark rectangular node style exactly match Unreal’s Blueprint visual scripting environment.

So, you’re looking at an **Unreal Engine Blueprint**—most likely a **Material Parameter or Animation Blueprint graph**.

## User · 2025-10-20 07:16

Can unreal engine with with microcontrollers or raspberry pie? 

## Assistant · 2025-10-20 07:17

Short answer: **yes, but not the way people first imagine.**

- **Microcontrollers (Arduino, Pico, STM32, etc.) → Unreal**
  - Treat the MCU as a **sensor/controller** and send data to a PC/Mac that’s running Unreal.
  - Common pipes:
    - **USB Serial** (needs a plugin like *UE Serial Port* / *UE4Duino*).
    - **UDP/TCP** (simple sockets).
    - **OSC** (Open Sound Control) — Unreal has an **OSC plugin** that’s easy to use in Blueprints.
    - **MIDI** (community plugins based on RtMidi).
  - Pattern: MCU sends messages (e.g., `/fader1 0.73` over OSC or a tiny binary packet over serial) → Unreal reads them and drives Blueprint variables, materials, cameras, etc.

- **Raspberry Pi → Unreal**
  - **As a device talking to Unreal**: Great. Run Python/C/C++ on the Pi and send **OSC/UDP/MQTT/WebSocket** messages to Unreal on your main machine.
  - **Running Unreal on the Pi itself**: Not practical. UE officially targets desktop/console/mobile; Pi’s GPU/driver stack isn’t a supported target and performance would be poor even with community builds.
  - **Good workaround**: Run Unreal on a Windows/Linux/macOS box and **stream** it to the Pi (Pixel Streaming/WebRTC) while sending inputs back from the Pi.

### Quick, reliable setups I recommend
1) **OSC over Wi-Fi**
   - MCU or Pi → Wi-Fi → send `/knob1 <float 0–1>`, `/key <int> <velocity>`  
   - In Unreal: enable **OSC** plugin → Add “Receive OSC Message” nodes in Blueprints.

2) **USB Serial**
   - MCU → USB → Unreal serial plugin  
   - Send a tiny framed packet (e.g., `0xAA type value checksum`). Parse in a Blueprint/C++ listener and map to variables.

3) **MQTT / WebSocket (for lots of devices)**
   - Pi publishes sensor topics; Unreal (via plugin) subscribes and drives gameplay/UI.

If you tell me which route you prefer (OSC, serial, or MQTT) and what data you want to send (e.g., “note, velocity, faders, wheels”), I’ll sketch the packet format and the matching Unreal Blueprint node setup for you.

