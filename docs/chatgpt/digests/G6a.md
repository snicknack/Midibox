# Group 6a digest (2025-10-27 to 2025-11-06; chats 04, 06, 10, 11)

Heading dates are quoted as "## Assistant · date time" in the chat files. "(ESP)" = the ESP32 touchscreen board, "(Pi)" = Raspberry Pi 4.

## Per chat

### 06 - ESP32 to PI Serial Integration (2025-10-27 14:08 to 2025-11-04 00:13, 297 msgs)
Started as GUI-framework talk (LVGL alternatives, Qt/TouchGFX/LovyanGFX, C6 vs S3 for displays), then became the log of getting the ESP32 LVGL/SquareLine GUI talking to the Pi over a hardware UART, then wiring the pitch/mod wheels (via ADS1115 on the Pi) so they move bars on the ESP screen and send MIDI, then WS2811 LEDs and a connector ID.

**Hardware facts**
- Roles: ESP32 = screen only (LVGL GUI + touch). Pi = brain (MIDI, wheels, logic). Wheels go to the Pi, NOT the ESP (user correction, 2025-11-02 18:22).
- The ESP in use is a standard ESP32 (WROOM, not the C6/S3 discussed earlier). User confirmed "standard esp32" from a pin map photo (16:14).
- Physical link (working, confirmed 16:28): Pi pin 8 (GPIO14 TXD0) -> ESP GPIO16 (RX2); Pi pin 10 (GPIO15 RXD0) <- ESP GPIO17 (TX2); Pi pin 6 GND <-> ESP GND. 3.3 V logic both sides, no level shifter. Pi device `/dev/serial0` (-> ttyS0), 115200 baud, 8N1. ESP uses UART2 via `HardwareSerial Link(2); Link.begin(115200, SERIAL_8N1, 16, 17);`. UART0 (GPIO1/3) is left for USB programming/debug.
- Earlier wrong code defines `#define RX_PIN 20 / TX_PIN 21` (valid on S3/C3, nonexistent on WROOM) -> changed to 16/17.
- The three real faults fixed (user's summary, 16:28): GND not common between Pi and ESP; pins not defined in code; the Pi wires had been put on the same RX/TX line as the touchscreen.
- Pi setup: raspi-config -> Serial: login shell No, hardware Yes. Optional `dtoverlay=disable-bt` frees the PL011 UART (up to 3 Mbps) in /boot/firmware/config.txt. Suggested baud range 115200-921600. Keep leads under ~20 cm.
- USB alternative discussed but not used (CDC would be /dev/ttyUSB0 or ttyACM0); USB kept free for class-compliant MIDI devices. UART does not interfere with USB MIDI.
- Wheels: ADS1115 on Pi I2C bus 1 (SDA GPIO2 pin 3, SCL GPIO3 pin 5, VDD 3V3 pin 1, GND pin 6, address 0x48). A0 = pitch wheel wiper, A1 = mod wheel wiper; outer pot legs 3V3 and GND. A2/A3 = faders ("FaderA"/"FaderB" in calibration JSON). MCP3008 (SPI) was offered as option A and not used.
- User's photos showed pitch + mod wheels with wires and two RGB lights (WS2811).
- LEDs: two WS2811 pixels from Pi GPIO18 (pin 12, PWM), 5 V power, common GND; suggested 74AHCT125/74HCT14 level shifter, 330 ohm series resistor on data, 1000 uF cap across 5 V/GND. Lib `rpi_ws281x` (LED_COUNT 2, LED_PIN 18, LED_FREQ_HZ 800000, LED_DMA 10, LED_BRIGHTNESS 255, LED_CHANNEL 0). Needs sudo (PWM/DMA). Pixel 0 = pitch (green), pixel 1 = mod (blue), dim->bright with value. Not confirmed working in chat.
- Bookworm pip error "externally-managed-environment": options apt `python3-rpi-ws281x`, `pip install --user rpi-ws281x --break-system-packages`, or venv `~/venvs/midibox` (run with `sudo --preserve-env=PATH,VIRTUAL_ENV python -m ...`).
- Connector asked about (2025-11-04 00:13, from a photo): identified as JST-PH 3-pin, 2.0 mm pitch, housing JST PHR-3, contacts JST SPH-002T-P0.5S; if 2.54 mm pitch then JST-XH. For wheels / LED lines. Sources: Farnell/RS/Mouser or PH 2.0 kits.
- Legacy 5-pin DIN MIDI would need an opto board (6N138/PC900) on Pi UART at 31250 baud; not needed for USB-MIDI.
- Display advice (not final): C6 is not fastest (single core 160 MHz); SPI practical to ~480x320 (3.5"); for ~5" 800x480 use ESP32-S3 RGB; P4 for more.

**Protocol and code**
- Line protocol, newline-terminated ASCII, in both directions:
  - Pi -> ESP: `name:value\n`, e.g. `uic_t1Arc1:64`, `uic_pitchBar:90`, `uic_ModBar:83`. Value clamped 0..127. Names are the SquareLine/LVGL object ids (`uic_` prefix = SquareLine "user interface component" variable, declared in `ui_MainPage.h`).
  - ESP -> Pi: JSON lines, `{"get":"uic_t1Arc1","val":47}` when a control is moved on screen; `{"set":"<name>","val":N}` echo after applying a Pi command; `{"err":"unknown","name":"..."}` for unknown names. Debug variants `[RX] ...`, `[SET] name=v`, `[NOOBJ]`, `[BAD]`.
  - Earlier proposal (not adopted): `SET CUT=127`, `TOUCH XY=120,40`. Suggested later: CRC/packet header.
- Widget names mentioned: uic_t1Arc1..uic_t1Arc4, uic_t1TempoArc, uic_pitchBar, uic_ModBar (user's final correction at 23:58; assistant had used uic_t1PitchBar/uic_t1ModBar). SquareLine event handlers `ui_event_t1Arc1..4`, `ui_event_t1TempoArc`, `ui_event_t1PitchBar`, `ui_event_t1ModBar`.
- ESP files: sketch `~/Documents/Arduino/lvgl_hello_gui_SL_V3_pi_Comms/lvgl_hello_gui_SL_V3_pi_Comms.ino` (LVGL, loop() calls `lv_timer_handler(); handleSerialInput(); delay(5);`; has `parseSerialCommand()`, `applyWidgetValue()`, `sendWidgetValue()`, `#define LINK_SERIAL Link`, `static String serialBuffer` with 128-char overflow guard), plus SquareLine-generated `ui_events.c/.h`, `ui_MainPage.c/.h`. Final parser/Link snippet: "Assistant 2025-11-02 22:42" (LINK_SERIAL alias), "15:29" (tidy parser with clamp, echo and table-driven idea), "23:58" (applyWidgetValue with uic_pitchBar/uic_ModBar and lv_bar_set_range 0..127 after ui_init()). `sendWidgetValue` must be `extern "C"` in the .ino and declared `extern void sendWidgetValue(const char*, int);` at the top of ui_events.c ("15:52"); it should print to `Link`/LINK_SERIAL, not `Serial` ("16:15"). The user's final .ino is NOT in the chat (only pieces).
- Pi files (package layout, all under `/home/stephennicholson/midibox/`): `__init__.py`, `io/__init__.py`, `tools/__init__.py`, `io/ads1115_reader.py` (class `ADS1115Reader(address=0x48)`; methods `read_channel(i)` returns 0..1 float, `read_cc()` returns list of 4 ints 0..127; no `calibrate_channels`), `tools/ads1115_calibrate.py`, `config/ads1115_cal.json`, `pi_pitch_mod_reader.py`, scratch `esp_link.py`, `esp_link_repl.py`. Run from `~` with `python3 -m midibox.pi_pitch_mod_reader` (use `sudo` if LEDs added). Absolute imports `from midibox.io.ads1115_reader import ADS1115Reader`. User wrote the reader and calibrator themselves (a week's work) and refused Adafruit lib.
- Calibration JSON (as shown 22:18): keys "0".."3" each with name,min,max,invert,deadband, e.g. `"0": {"name":"Pitch","min":75,"max":98,"invert":false,"deadband":1}`, `"1": Mod 76..100`, `"2": FaderA 72..72 deadband 0`, `"3": FaderB 72..72`. Units are CC-like (0..127), NOT 0..1 -- the unit mismatch (read_channel gives 0..1, cal is ~75..100) was the final bug (Assistant 00:23, 2025-11-03).
- FINAL Pi script = "Assistant · 2025-11-03 00:23" (full file; prefers `read_cc()[idx]`, falls back to `read_channel*127`; loads cal; `to01`, `to7`; `send_to_esp()` writes `f"{name}:{value}\n"` + flush; W_PITCH="uic_pitchBar", W_MOD="uic_ModBar"; sends MIDI `pitchwheel` (int(p01*16383)-8192) and CC1; FORCE_SEND_SECONDS=10 diagnostic burst then deadband from JSON). Smoothing patch (EMA alpha 0.3) = "Assistant · 2025-11-03 00:29" (block replacing normalise step; user said it was added). LED patch = "Assistant · 2025-11-03 00:46". User confirmed bars move ("YESSSS", 00:26); the exact final file with smoothing/LEDs lives only on the Pi.
- Earlier full version with diagnostics = "2025-11-02 23:50"; echo emulator test = "22:49".
- Test method that proved the link: `echo "uic_t1Arc1:64" > /dev/serial0` and a 5-line Python sweep.

**Decisions and why**
- UART on GPIO header (not USB-CDC, I2C or SPI): simplest, already working, keeps USB ports for MIDI devices.
- Use ESP UART2 (16/17) not UART0, to avoid boot garbage (74880 baud ROM log), flashing conflicts.
- ESP = display only; analog wheels via ADS1115 on the Pi; the Pi pushes wheel values to ESP bars and sends MIDI Pitch Bend + CC1.
- Keep both directions: ESP -> Pi event callbacks AND Pi -> ESP parser.
- SquareLine events: Trigger VALUE_CHANGED, Action CALL FUNCTION with name e.g. `ui_event_t1Arc1`; user declared empty functions in `ui_events.h` for all 4 arcs, then implemented in the generated .c (C compiled, so no Serial) -> bridge via `extern "C"`.
- Python package structure with `python3 -m midibox...` run from `~` instead of pip -e.
- Pitch re-scaled from -8192..8192 to 0..127 for the screen (user, 23:58).

**Problems hit**
- Callbacks never fired / events not bound; `start_debug_pollers` not declared; `ui_events.c` vs `.cpp` multiple definitions; `'Serial' undeclared` in .c; `undefined reference to sendWidgetValue` -> solved with extern "C" (15:52).
- Garbled serial: solved (GND, undefined pins, shared touch-screen TX/RX line, UART2 16/17).
- Python import errors / `calibrate_channels` missing / pip -e "package directory midibox does not exist" -> solved with __init__.py + `-m`.
- Script zeroed a widget once but wheels did not move it: name mismatch + 0..1 vs 0..127 unit mismatch -> solved 00:23.
- Pip externally-managed-environment for rpi-ws281x: three options given; outcome not reported.

**State at end**: wheels -> ADS1115 -> Pi -> (MIDI + ESP bars) working; smoothing added; WS2811 code provided but untested in chat; user buying JST-PH 3-pin plugs. Planned next: RGB dim->bright on pitch/mod, then Pi->ESP feedback, touch-to-MIDI mapping, GUI->Pi two-way sync, aftertouch idea.

### 04 - Colour palette reference (2025-10-27 19:03 to 2025-10-28 16:09, 61 msgs)
EEZ Studio (LVGL designer) work for the ESP32 TFT: asked for project hex colours and the EEZ component palette, how to swipe pages, TileView vs pages, list/roller for scale selection, splash screen, binding encoder values to labels, EEZ vars.c/vars.h stubs. (Later the project switched to SquareLine in chat 06.)

**Hardware / design facts**
- Display: FT6236 3.2" SPI TFT touchscreen 240x320 (landscape 320x240 used for splash).
- Midibox design overview quoted: Pi 4; 2 long-throw faders (CC); MPR121 (Adafruit) capacitive touch transport (Start, Stop, Rec, Jog L/R, Loop); pitch + mod wheels (analogue); Fatar 88-key keyboard (velocity, aftertouch); 4 smooth encoders with capacitive + click; USB-A for class-compliant devices; USB-C gadget to hosts; pages: P1 transpose/octave/chords/4 encoder params, P2 arpeggiator/scale/Up-Down-Chord, P3 faders + encoders setup, P4 USB MIDI out select; 2 m cable from Fatar to box; boots straight into program; modular Python files.
- IMPORTANT: the palette below was RECONSTRUCTED by the assistant ("recommended reconstructed palette"), not read from the project; user's logo/splash "MIDI PLAYGROUND" / "Holson Instruments" ice-blue theme.
- Palette hex: Primary Blue #00CFFF (accent/LED/highlight, "Tron" ice-blue); Secondary Blue #0078A0; Highlight Cyan #3FE8FF (touch glow); Dark Grey #1C1C1C (background/enclosure); Panel Grey #2A2A2A; Text White #FFFFFF; Text Soft White #CCCCCC; Accent Orange #FF6B00 (warning/record); Accent Green #00FF88 (OK/play); Accent Red #FF2B2B (stop/record); Purple #8A2EFF (MIDI Playground/experimental). Arc/bar styling used: indicator/foreground #00CFFF, background #303030. EEZ defaults listed: #E0E0E0, #FFFFFF, #32CD32, #FF0000, #00BFFF, #D6D6D6, #222222.
- Splash generated (PIL): 320x240 (also 240x320, 480x320), bg (8,8,10), vignette (16,16,18), glow (255,200,80,70); final `splash_320x240_clean.png` (no loading bar). Files only in ChatGPT sandbox.
- Protocol/code: none for serial. EEZ: bind arc Value and label Text to one global variable (`encoder_4_val`); widget names `arc_encoder_4`, `text_encoder_value_4`; EEZ needs `get_var_encoder_4_val()/set_var_encoder_4_val()` in vars.c/vars.h (int32_t). `arc_encoder_4[value]` syntax not supported. Label vanishing fixed by nesting under arc, size=parent, align centre, clickable off.
- Decisions: TileView only gives swipeable areas inside one page; use a bottom tab/button matrix for pages. State at end: encoder label binding being fixed; superseded by SquareLine workflow.

### 10 - New chat (2025-11-06 08:02, 4 msgs)
Faceplate overlay with opaque section for LEDs around the SUPERCORE encoder, Quasar-style Neopixel halo.
- Idea (Option A): 0.5-0.75 mm hardcoat polycarbonate overlay, second-surface UV print, spot-white mask layer with a donut-shaped knockout window, 3M 467MP/468MP adhesive, opal PMMA diffuser ring (Perspex Opal 050, 2-3 mm, ring 6-10 mm wide), matte black 3D-printed baffle (0.8-1.2 mm wall, height LED + 0.5-1.0 mm, ~2.8-3.5 mm total), Neopixel ring (24-32 LED, 5050/3535, or APA102) for 35-50 mm OD halos, LED-diffuser gap 1.5-3 mm.
- CAD: window inner dia = encoder nut clearance + 1.0 mm; outer = ring OD + 1.0-1.5 mm; diffuser OD = window OD - 0.3, ID = window ID + 0.3; legends 1.5-2 mm from window. Files: vector PDF/SVG art, "WHITE"/"Spot1" layer, optional HALO_TINT (15-30% CMY), cut/score layer, fiducials. Tolerances +-0.2 mm holes, +-0.3 mm outline. Option B: PCB faceplate with black mask and milled annular slot. Drive at low global brightness; optional Rosco 3008 / Lee 216 film.
- No decision; assistant offered a DXF/SVG if given encoder nut dia and ring OD (not supplied).

### 11 - Pi4 replacement options (2025-11-06 08:46, 14 msgs)
- Question: could the Pi 4 be replaced by smaller/cheaper board. Assistant: CPU load is modest (SPI TFT + FT6236, ADS1115, SX1509 encoders, 2 faders, MIDI host on USB-A, USB-C gadget); the constraint is USB host+gadget at once. Candidates: Pi Zero 2 W (one OTG, host OR gadget only), Pi 3A+, CM4 on small carrier (host + gadget together), keep Pi 4 (simplest).
- Conclusion (user, 08:50): stick with Pi 4 for the prototype. Pi 4 is the simplest way to be USB host (A) and gadget (C) simultaneously.
- Then production strategy for Etsy/Kickstarter: trademark "Holson Instruments", secure boot/ATECC608A, disable JTAG in production, cost ranges (PCBA 10-100 units GBP 50-150/board; tooling GBP 5k-30k+). User's chosen direction (08:58): community-style brand, own circuit board with a Pi header (Pi-hat/base board), do not worry about reverse engineering, lock down what is easy. Assistant playbook: open schematics/pinout/API, paid premium firmware and add-on daughter boards, two SKUs (Maker Kit, Pro Box), trademark, start with 50-100 boards.

## Group facts table
- Link: Pi pin 8 GPIO14 TX -> ESP GPIO16 RX2; Pi pin 10 GPIO15 RX <- ESP GPIO17 TX2; GND pin 6 common; 115200 8N1; /dev/serial0; 3.3 V no shifter; ESP UART2 `Link`; serial console disabled via raspi-config.
- ESP is a standard ESP32 WROOM (GPIO20/21 do not exist); programmed in Arduino IDE with LVGL + SquareLine export; touchscreen shares nothing with the Pi UART (do not share its RX/TX).
- ESP -> Pi JSON `{"get":name,"val":n}`; Pi -> ESP `name:value\n`; value 0..127; widget ids uic_t1Arc1-4, uic_t1TempoArc, uic_pitchBar, uic_ModBar.
- Sketch `lvgl_hello_gui_SL_V3_pi_Comms.ino`; Pi package `/home/stephennicholson/midibox/` with io/, tools/, config/ads1115_cal.json, `pi_pitch_mod_reader.py`; run `python3 -m midibox.pi_pitch_mod_reader` from ~.
- ADS1115 at 0x48 on I2C1 (GPIO2/3): A0 pitch, A1 mod, A2/A3 faders; reader `read_cc()` -> 4 ints 0..127; cal min/max pitch 75..98, mod 76..100; raw pitch ~0.58 to 0.78, mod ~0.6 to 0.79 (0..1 floats).
- MIDI out: Pitch Bend (int(p01*16383)-8192) and CC1 via mido; EMA smoothing alpha 0.3.
- WS2811 x2 on Pi GPIO18 via rpi_ws281x (sudo); JST-PH 3-pin (PHR-3, 2.0 mm) plugs needed.
- Display FT6236 3.2" 240x320 SPI (EEZ era); palette #00CFFF, #0078A0, #3FE8FF, #1C1C1C, #2A2A2A, #FFFFFF, #CCCCCC, #FF6B00, #00FF88, #FF2B2B, #8A2EFF, arc bg #303030 (assistant-reconstructed).
- Faceplate: polycarbonate overlay + spot-white donut window + opal ring + black baffle + 24-32 LED Neopixel ring around the SUPERCORE encoder.
- Pi 4 kept for prototype; production idea = Pi-header base board, open hardware, brand Holson Instruments (also "MIDI Playground" splash).

## Open threads
- Final .ino (Link-based parser + sendWidgetValue using Link) and final Pi script with smoothing and LEDs are not stored whole in the chats; recover pieces from the headings cited.
- WS2811 LED code untested/unconfirmed; rpi-ws281x install on Bookworm not confirmed.
- Pi -> ESP feedback of other params, GUI -> Pi sync, touch-to-MIDI/aftertouch mapping, pitch smoothing split (GUI raw vs MIDI smoothed) not done.
- Palette values are not authoritative; real colours must be read from the EEZ/SquareLine project.
- Faceplate dimensions (encoder nut dia, ring OD) not supplied; no DXF made.
- Pi-header base board / secure-boot / BOM plan only discussed, nothing drawn.
