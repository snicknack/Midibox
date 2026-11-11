# ChatGPT memory summary — Midibox-related sections only

Captured 2026-11-11 from ChatGPT Settings → Personalization → Memory summary.
Only the two sections that concern Midibox are copied here; the personal,
music, business and studio sections were left out on purpose.

## Instrument Projects

You're developing the Midibox/SuperCore controller as a substantial
hardware-and-software project. Its work includes super faders, super encoders,
capacitive sensing, optical fader drivers, pitch and mod controls, haptics and
LED feedback. The central encoder-based SuperCore concept brings together
functions such as SuperTempo Glide, SuperMapper and SuperLFO; it belongs on the
project map, while development is intended to wait until basic encoder
operation is stable. Recent build work has combined Raspberry Pi modules with
an ESP32 touchscreen interface, including page and bank layouts, encoder
displays, pitch/mod bars and RGB lighting. You prefer keeping touchscreen code
organised into separate page modules rather than one enormous file, and you've
explored an opaque faceplate section for LEDs around the SuperCore encoder.
You've also considered a dedicated PCB with a Pi header for a more
product-ready design. Other instrument ideas include an Ableton Link module, a
Eurorack STM32H7 reverb, and a powerful Pi 5 Eurorack synth with polyphony,
multitimbrality, class-compliant computer access, automation and project
recall.

## Tools and Working Style

You prefer practical, incremental development with clear project structure and
working components before moving on to a larger concept. In hardware and code
work, you've asked to preserve code that is already working and make minimal,
targeted changes rather than replacing it wholesale. Your Midibox work has used
Raspberry Pi 4, Raspberry Pi Pico, ESP32, Python, Arduino tooling and EEZ
Studio/LVGL; you've also worked through I²C input modules, serial integration,
encoder event handling and WS2811/NeoPixel colour order. You've preferred
keeping the Pi 4 for the prototype while considering a more compact production
design later.
