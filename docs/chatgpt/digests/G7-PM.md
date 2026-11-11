# Midibox PM digest (2025-09-30 to 2025-10-09)

**IMPORTANT CAVEAT:** The export header says created 2025-09-30, updated 2026-11-11, 108 messages, but the file body (4853 lines) ends at the 2025-10-09 17:55 message. There is NO mention anywhere of SuperCore, SuperTempo Glide, SuperMapper, SuperLFO, ESP32, LVGL, Pico, haptics, "super faders/encoders", or banks. grep confirmed zero hits. The later material (Oct-Nov 2025) is not in this file. This digest covers only what is present: an early Pi-4 + Python/PIL project, not the later ESP32/Pico/SuperCore architecture. The assistant persona is nicknamed "Bert" ("Bert the destroyer of bugs") by the user from 2025-09-30.

## Timeline
- 2025-09-30 09:03: User uploads "Midibox Build Overview.docx" (design overview, see Project map). Asks to discuss.
- 2025-09-30 09:07-09:09: Chat designated the Project Management (PM) hub (high level); deep-dives go in other chats. Master plan set up: 5 phases, 5 workstreams, decision log, risks.
- 2025-09-30 09:13: User: no timelines/Gantt, "hobby build"; just the steps of Phase 1, work through them. 8-step Phase 1 defined.
- 2025-09-30 09:14: Step 1 (Pi 4 boots into OS) complete.
- 2025-09-30 09:55-10:05: Assistant could not see code; user uploaded midibox.zip; assistant extracted and read it (main.py, gestures.py, ui/pages.py, ui/widgets.py, drivers/tft.py, drivers/touch_ft6236.py, midi/router.py).
- 2025-09-30 ~10:05: Review: TFT + touch drivers, UI pages, swipe detector, mido router already exist; no encoder/ADC/MPR121/power code in repo yet.
- 2025-09-30 12:34: User ran hardware_test.py smoke test on Pi: SPI present, /dev/fb0 present, FT6236 at 0x38 found, MPR121 NOT detected, ADS1x15 NOT detected (at that time), RPi.GPIO ok, `throttled=0x0`. Only 0x38 on I2C bus 1.
- 2025-09-30 12:38-13:11: touch_draw_demo.py iterated (assistant had guessed class names TFT/FT6236; user corrected: real classes are `Display` and `Touch`). Fixed PIL bullet-char font error, `event` int vs str crash, screen rotation 180 kept, touch needed invert X and Y. Result: dots follow finger. Step 2 complete. User named assistant "Bert".
- 2025-09-30 12:43: Assistant added examples/touch_draw_demo.py, examples/mcp3008_read.py, drivers/adc_mcp3008.py, drivers/mpr121.py.
- 2025-09-30 21:21: Tracker: Steps 1, 2, 8 complete.
- 2025-09-30 21:27-21:53: User says encoders+capacitive sensing complete using SX1509 I/O expander (code lives in other chat "Capacitive and analog inputs"); MPR121 working earlier (other chat "Midibox Build - Phase 1"). Assistant generated sx1509.py, encoder_manager.py, transport_mpr121.py + test examples; user: not needed, modules already done elsewhere; "not fussed about main until all the modules are finished". Next: ADS1115 arriving next day, then a data logger task on Thursday when hardware arrives. Assistant produced ads1115.py driver, ads1115_read.py, utils/logger.py (CSV), ads1115_logger.py.
- 2025-09-30 22:07: User adds Stretch Track: WS2811 LEDs in the wheel space. Pitch wheel: two colours for bend up/down; mod wheel: one colour to red at full range. Steps S-1..S-5 defined.
- 2025-09-30 22:14: Step 7 power decided: USB-C panel socket ordered + official Raspberry Pi 3 A PSU, separate from the Pi, to be integrated in a case later. Marked "Procured, test next".
- 2025-10-01 23:11: Tracker updated with Hardware Design lane ("Box v1" layout locked).
- 2025-10-09 17:55: User: "optical fader drivers complete, the keyboard working". Tracker: Phase 1 steps 1-6, 8 complete; step 7 in progress; Fatar keyboard working and decoded; Phase 1 "essentially complete". Next: Phase 2 (MIDI I/O + routing), then WS2811. Assistant offers a Case Assembly & Wiring sub-tracker (unanswered; file ends).

## Project map (as named in this thread)
- Pi 4 testbed: complete.
- TFT + FT6236 touchscreen (3.2", 240x320, SPI, ILI9341 via adafruit_rgb_display): complete; 180 deg rotation, touch invert X+Y.
- Encoders (4 smooth, capacitive, clickable) via SX1509 expander: complete (code in another chat). Capacitive sensing via MPR121.
- Transport pads (MPR121 capacitive): working; actions start/stop/rec/jog_l/jog_r/loop; code in "Midibox Build - Phase 1" chat.
- Pitch and Mod wheels (analogue) via ADS1115: marked complete 2025-10-09.
- Long-throw faders (2): described as "optical faders" with drivers complete 2025-10-09 (ADS1115 inputs). (Original overview said 2 long-throw faders for CC.)
- Fatar 88-key keybed (velocity, aftertouch): working and decoded as of 2025-10-09 (2 m cable extension to make; not stated as built).
- Power: USB-C panel socket + official Pi 3 A PSU; test in progress.
- Hardware test script (hardware_test.py): complete.
- Data logger (CSV, utils/logger.py): module ready; hardware arriving.
- Stretch Track WS2811 LED feedback (S-1 HW/5 V/level shift; S-2 driver; S-3 wheel-to-colour; S-4 ADS1115 hookup; S-5 config/UI toggles): all not started.
- Phase 2 Core MIDI I/O (USB-A host, USB-C gadget, merge/routing, Fatar verify): not started.
- Phase 3 UI (pages, swipe): partly stubbed in code; formal phase "coming after full MIDI stack".
- Phase 4 feature integration (transport map, encoder touch assignments, arp sync, RGB/buttons); Phase 5 polish (boot-to-app, splash, case, long-run test): not started.
- Case: 3D printed, Box v1 layout locked (widened right-hand side, encoder cluster top-right); case sub-tracker offered.

## Architecture
Only the early design is present.
- Pi 4 is the sole controller: reads I2C (FT6236 0x38, MPR121, SX1509, ADS1115), SPI (TFT, optional MCP3008), outputs MIDI via mido; UI drawn with PIL to the SPI TFT. No Pico/ESP32 in this file.
- MIDI out: USB-A host for class-compliant synths; USB-C gadget mode to Mac/PC host. Pi powered separately by USB-C panel socket, so gadget bus stays free (PMIC arbitrates VBUS; optional USB-C power blocker).
- Original overview pages: Page 1 transpose/octave up-down/chord display/4 touch encoder params; Page 2 arpeggiator (scale, up/down/chord); Page 3 setup (fader CC assignment, assign touch encoders to internal functions or CC); Page 4 USB MIDI out selection. Swipe gestures. UI libs considered: Tkinter, Kivy, PyQt/PySide (actual code uses PIL rendering).
- Repo layout seen in midibox.zip: midibox/main.py, gestures.py (SwipeDetector min_dist=50 max_time=0.6), ui/pages.py (PadsPage, SlidersPage, PerformancePage, SettingsPage, PortsPage; PageBase), ui/widgets.py, drivers/tft.py, drivers/touch_ft6236.py, midi/router.py (MidiRouter with MIDI_CHANNEL=1, TRANSPOSE=0 globals; note_on/note_off/cc/pitchbend). Pi path: /home/stephennicholson/midibox/, run as `python3 -m midibox.examples.<name>`.
- Added modules (assistant-generated, partly superseded by user's own): drivers/adc_mcp3008.py, drivers/mpr121.py, drivers/sx1509.py, drivers/ads1115.py, inputs/encoder_manager.py, inputs/transport_mpr121.py, utils/logger.py, examples/{touch_draw_demo,mcp3008_read,encoders_test,transport_test,ads1115_read,ads1115_logger}.py. Planned: drivers/led_ws281x.py, effects/wheel_meter.py, examples/wheels_led_demo.py, config.py, utils/power.py.

## Decisions and principles
- This chat = high-level Project Management hub; technical deep dives in separate chats (UI, MIDI/gadget, hardware, codebase, enclosure).
- Lightweight checklist, no timelines/Gantt ("hobby build").
- main.py stays a thin skeleton; one module per requirement (gestures, UI, MIDI USB-C, USB-A, scales/CC, transport) for updates and learning; do not work on main.py until all modules are finished.
- Assistant must read the project's actual files before writing code (user corrected guessed class names `TFT`/`FT6236`; real are `Display`/`Touch`).
- Touch calibration: INVERT_X = True, INVERT_Y = True under 180 deg screen rotation (flags TOUCH_SWAP_XY, TOUCH_INVERT_X, TOUCH_INVERT_Y, TOUCH_ROTATION; to be pinned into config.py).
- Power: USB-C panel socket + official 3 A Pi PSU, 5 V into Pi via USB-C not GPIO; LEDs on separate/internal 5 V rail if >30-40 LEDs; common ground; level shift 74AHCT125/14 (not HC); optional polyfuse and TVS.
- Hardware layout Box v1 locked after sketches.
- Boot direct into program (no Pi OS interaction) when project complete.
- Optional RGB LEDs/buttons available as suggestions.

## Last known status
Last message in file: 2025-10-09 17:55 (user) with assistant tracker reply. Phase 1 essentially complete: Pi 4, TFT+FT6236, encoders (SX1509)/MPR121 capacitive, pitch/mod wheels (ADS1115), optical faders, transport pads, hardware test script all complete; Fatar keyboard working; power step 7 in progress (parts procured). Next: Phase 2 MIDI I/O and routing (USB-A host, USB-C gadget, merge), then WS2811 stretch track, case assembly and wiring. No later status exists in this file.

## Facts table
- Pi 4; OS user `stephennicholson`; project dir /home/stephennicholson/midibox; logs dir planned /home/pi/midibox_logs/.
- Display: 3.2" 240x320 SPI TFT, ILI9341 driver (adafruit_rgb_display), baud 32 MHz, rotation 180; CS=CE0 (GPIO8), DC=GPIO24 (D24), RST=GPIO25 (D25).
- Touch: FT6236, I2C bus 1, addr 0x38, reg TD_STATUS 0x02.
- MPR121: Adafruit breakout, default addr 0x5A (0x5B-0x5D via ADDR pin); transport map default {0:start,1:stop,2:rec,3:jog_l,4:jog_r,5:loop}.
- SX1509 I/O expander: example addr 0x3E, bus 1; encoders enc1 pins A0/A1/A2(btn), enc2 A3/A4/A5(btn) (example values, "adjust to wiring"); reset reg 0x7D (0x12 then 0x34).
- ADS1115: I2C 0x48-0x4B (ADDR GND/VDD/SDA/SCL); 4 channels; PGA suggestion pga=2 (+/-2.048 V) or 0 (+/-6.144 V).
- MCP3008 (SPI, CE0/spidev0.0): earlier assumed ADC; superseded by ADS1115. SPI pins: CLK GPIO11, MISO GPIO9, MOSI GPIO10.
- I2C: SDA1 GPIO2 (pin 3), SCL1 GPIO3 (pin 5); 3.3 V only for MPR121.
- WS2811 data: GPIO18 (PWM) or GPIO21 (PCM) via rpi_ws281x; ~20 mA typical, 60 mA max per LED; planned config keys LED_PIN, LED_COUNT, LED_BRIGHTNESS, COLOR_UP, COLOR_DOWN, COLOR_NEUTRAL, MOD_BASE, MOD_FULL_RED, GAMMA, FPS_CAP, PITCH_DEADZONE, PITCH_CENTER_CALIBRATION.
- Libraries: mido, PIL, smbus/smbus2, RPi.GPIO, board/digitalio (CircuitPython blinka).
- Power check: `vcgencmd get_throttled` = 0x0 clean.
- Fatar keybed (dead Studiologic SL88 context not stated in this file); 2 m cable extension planned; aftertouch, velocity, 88 keys.
- Files referenced: "Midibox Build Overview.docx", midibox.zip; related chats: "Capacitive and analog inputs", "Midibox Build - Phase 1".
- Persona nickname: Bert.
