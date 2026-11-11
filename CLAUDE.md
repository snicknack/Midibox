# MidiBox — working notes for Claude

MidiBox is Stephen's desktop MIDI controller, built around the keybed of a
Studiologic SL88 Studio whose main board died. A Raspberry Pi 4 is the brain,
an ESP32 drives the touchscreen, and a Pico W (now the separate KeySYS project)
turns the keybed into USB MIDI. Brand: **Holson Instruments**; the screen's
product name is **MIDI PLAYGROUND**. The signature feature is the **SuperCore**:
one encoder with a NeoPixel ring and haptics that hosts SuperTempo glide,
SuperMapper, SuperLFO and a recorder.

The project was built with ChatGPT from 27 Sep to 8 Nov 2025 (keybed work ran
to Jan 2026). Claude took it over on 11 Nov 2026. Everything ChatGPT knew is in
`docs/chatgpt/` (41 transcripts, nine digests, ChatGPT's memory notes). This
file is the synthesis; when it conflicts with the hardware on the bench, the
bench wins and this file gets corrected.

## Where things live

| Thing | Location | Notes |
|---|---|---|
| This repo | `~/MidiBox` (Mac), GitHub `snicknack/Midibox`, branch `main` | Cloned 11 Nov 2026; the three original commits are the Sep 2025 Pi app |
| Pi 4 | `midibox.local` (192.168.1.215 on 11 Nov 2026), user `stephennicholson`, project `~/midibox` (lowercase) | SSH key from this Mac installed 11 Nov 2026. Hostname `MidiBox`, Pi OS Bookworm, Python 3.11.2. **`pi/` in this repo is a snapshot of the Pi taken 11 Nov 2026** (`pi/midibox`, `pi/MIDIKeyboard`, `pi/old-versions`, `pi/home-scripts`, `pi/system`); the Pi itself stays the live copy until the code is moved into this repo properly. The Pi's home directory is itself an old checkout of the GitHub repo |
| Keybed firmware | `~/KeySYS` (Pico W, CircuitPython) | Claude-era successor of the ChatGPT "Keyboard velocity processing" work; decodes the STM32's key-time stream properly. Do not duplicate it here. `pi/MIDIKeyboard/` is the Oct 2025 Pi-side sniffing and bridge history (`midibox_play.py`, `uart_plan_a.py`, the sniffers) |
| ESP32 sketch | `esp32/arduino/lvgl_hello_gui_SL_V3_pi_Comms/` (final, 2 Nov 2025), copied from the Intel MacBook Pro `StevesMacBookPro-2.local` (macOS 13.7.1, user `stephennicholson`, SSH key installed 11 Nov 2026), which is the Arduino IDE and KingstVIS machine. `esp32/arduino/` also holds every earlier sketch (SL_V1, SL_V2, main_page_mockup, smoke_test_lvgl_touch, Midibox_TFT_GUI, spi_sniffer*) and `libraries/TFT_eSPI/User_Setup.h`; the 127 MB logo-image sketches were copied without their giant `.c` image tables | `imports/chatgpt-sources/esp32/` is an earlier save of the same sketch (`RX_PIN 20 / TX_PIN 21`); ignore it |
| Screen UI design | `esp32/squareline/` (copied from `~/SquareLine`, saved 3 Nov 2025, with seven backups); `esp32/export-2025-10-27/` is the first export; `gui/eez/` are the abandoned EEZ Studio designs | SquareLine Studio 1.5.4, project 320×240, LVGL 8.3.11, board template ESP-BOX, non-flat export with screens/ and components/ subfolders |
| ChatGPT export | `docs/chatgpt/` here; raw JSON and images index in `~/Documents/ChatGPT/Midibox raspberry pi/` | Chat images (photos of the build) were not downloaded; `assets_index.json` lists them |

## Architecture

```
Fatar TP/100LR keybed ──(SL88 STM32 scanner board, UART 31250)──> Pico W [KeySYS] ──USB MIDI──> Mac / Pi USB-A
                                                                                          
Pi 4 (brain, Python 3, Pi OS Bookworm)
 ├─ I2C1 (GPIO2/3): SX1509 0x3E (5 encoders + presses), ADS1115 0x48 (pitch/mod wheels), DRV2605L 0x5A (haptics)
 ├─ UART0 /dev/serial0 (GPIO14 TX / GPIO15 RX) 115200 ──> ESP32 UART2 (GPIO16 RX / GPIO17 TX)   screen link
 ├─ /dev/ttyAMA2, /dev/ttyAMA3 (uart2/uart3 overlays) <── Behringer Infinium X1 optical faders, 31250 8N1
 ├─ GPIO13 (PWM1): 12-LED SK6812 RGBW NeoPixel ring around the SuperCore encoder
 ├─ GPIO18: two WS2811 pixels for the wheels (planned, untested)
 ├─ USB-A: host for class-compliant synths (Behringer Crave tested); USB-C: gadget MIDI to a computer (designed, never enabled)
 └─ MIDI out via mido / ALSA virtual ports; FluidSynth over ALSA for local sound

ESP32-WROOM-32 (screen only: LVGL 8.3.11 + TFT_eSPI, SquareLine UI, Arduino IDE)
 ├─ 3.2" ILI9341 240x320 SPI, used landscape 320x240 (rotation 3)
 └─ FT6236 capacitive touch on I2C 0x38
```

Roles were fixed on 2 Nov 2025: the ESP32 is display and touch only; every
knob, fader, wheel, LED and haptic is on the Pi; the Pi pushes values to the
screen and takes touch events back.

## Hardware map

### Pi 4 pins
| Signal | Pi pin | Device |
|---|---|---|
| SDA1 / SCL1 | GPIO2 (pin 3) / GPIO3 (pin 5) | SX1509, ADS1115, DRV2605L (all 3V3) |
| TXD0 / RXD0 | GPIO14 (pin 8) / GPIO15 (pin 10) | ESP32 link, `/dev/serial0` → `ttyS0` (the mini-UART; Bluetooth keeps the PL011), 115200 8N1, no level shifter. `enable_uart=1` is set. Serial login console is off (`cmdline.txt` has no serial console) |
| Fader 1 UART | `/dev/ttyAMA2`, `dtoverlay=uart2,txd2_pin=0,rxd2_pin=1` → fader TX into **GPIO1 (pin 28)** | Confirmed from `pi/system/config.txt`. GPIO0/1 are the HAT ID-EEPROM pins; fine without a HAT |
| Fader 2 UART | `/dev/ttyAMA3`, `dtoverlay=uart3,txd3_pin=4,rxd3_pin=5` → fader TX into **GPIO5 (pin 29)** | Confirmed from `pi/system/config.txt` |
| NeoPixel ring DIN | GPIO13 (pin 33) | rpi_ws281x channel 1; GPIO17 is not a valid ws281x pin. 330 Ω series, ~1000 µF across 5 V. Needs `sudo` |
| WS2811 wheel pixels | GPIO18 (pin 12) | implemented in `pi/midibox/midio/pi_pitch_mod_reader.py` (pixel 0 pitch: green up / red down, brighter away from centre; pixel 1 mod: blue with a floor of 40). Clashes with audio PWM if the headphone jack is used |
| SX1509 INT | GPIO17 (pin 11) | only for the interrupt driver, which never worked; polling driver ignores it |
| SX1509 RST | tied to 3V3 | **required**; floating RST was the 4 Nov breakthrough |

Earlier wiring that is no longer current: the Pi's own 3.2" ILI9341/FT6236
screen (CE0, DC GPIO24, RST GPIO25, FT6236 0x38 with CTP_RST to 3V3) from Sep
2025, the keybed UART on GPIO15 with a control line on GPIO18 (Oct 2025), and
the MPR121 transport pads at 0x5A. The MPR121's default address clashes with
the DRV2605L at 0x5A; if the pads come back, move the MPR121 to 0x5B–0x5D.

### SX1509 (I2C 0x3E, ADDR0/ADDR1 to GND)
| Encoder | A/B pins | Press pin | Screen widget |
|---|---|---|---|
| 1 | P0 / P1 | P2 (only one wired and enabled, 7 Nov 2025) | `uic_t1Arc1` |
| 2 | P3 / P4 | P5 | `uic_t1Arc2` |
| 3 | P6 / P7 | P8 | `uic_t1Arc3` |
| 4 | P9 / P10 | P11 | `uic_t1Arc4` |
| 5 Tempo = SuperCore | P12 / P13 | P14 | `uic_t1Arc5Tempo` (to be renamed `uic_SuperCore1`) |

P15 spare. Internal pull-ups ON for all A/B (Bank A encoders are dead without
them), encoder common to GND, no debounce on A/B, hardware debounce on the
press pins. Encoders are ALPS EC11E15244G5 (15 detents, 30 pulses/rev, push
switch, middle leg = common). The first batch in Sep 2025 was the smooth
EC11E183440. Note the SX1509 breakout silkscreen was found to be mislabelled
once (P0/1/2 marked where P8/9/10 are); verify pin numbers on the real board.

### Other parts
- ADS1115 at 0x48: A0 pitch wheel, A1 mod wheel (outer legs 3V3/GND). A2/A3
  were planned for faders before the optical faders arrived. Two calibration
  files exist in `pi/midibox/config/`: `ads1115_cal.json` (CC units: pitch
  75..98 deadband 3, mod 76..100 deadband 2; used by `pi_pitch_mod_reader.py`)
  and `calibration.json` (0..1 units from `calibrate_controls.py`: pitch
  0.604..0.788, mod 0.602..0.793, fader2 0..0.959, **fader1 0..0, so fader 1
  was not calibrated**; used by `test_infinium_dual_faders.py`). Two ADS
  reader classes also exist: `midio/ads1115_reader.py` (`read_cc()` → four
  ints, `read_raw()`, `read_all()`) and `midio/ads1115_mod.py` (threaded,
  `values_cc`, `begin()/close()`). Pick one when integrating.
- Behringer Infinium X1 optical faders ×2: 3.3 V, serial 31250 8N1, output is
  data-only byte pairs (no status byte) sweeping 0..127, in practice 1..126.
  Boards marked P0954 / PCB906031 REV E-01 and ME003330, 4-pin JST. Pinout was
  inferred, never metered: VCC 3V3, GND, TX, optional 4th. Do not feed 5 V.
- DRV2605L at 0x5A, VIN on 5 V, IN/TRIG to GND. The motor fitted is an ERM
  (runs in `use_ERM()` with library 1); a real LRA (Precision Microdrives
  C08-005 or similar, library 6, `use_LRM()` in the older Adafruit lib) is
  still to be fitted. The address is fixed, so the "second DRV2605L at 0x5B"
  idea from the last chat is wrong; a second driver needs a mux or another bus.
- NeoPixel ring: 12-LED SK6812 **RGBW** (not RGB, not 16), `pixel_order=GRBW`,
  `bpp=4`, brightness 0.02–0.05, pixel 0 at 12 o'clock via a `top_offset`.
- Enclosure: Retex 33020112 black sloped desktop box, 268×185×78 mm (CPC/
  Farnell). Layout locked 1 Oct 2025 as "Box V1": faders left, wheels middle
  left, screen centre, four encoders in a row plus the SuperCore. Faceplate
  idea: polycarbonate overlay with a spot-white donut window and opal
  diffuser ring around the SuperCore (no dimensions supplied yet).
- Power: official 5.1 V 3 A PSU via a USB-C panel socket; `get_throttled` was
  0x0 under test.

### ESP32 (ESP32-WROOM-32 clone "ZY-ESP32", CH340C, 4 MB flash)
| Function | GPIO |
|---|---|
| TFT SPI (VSPI) | SCK 18, MOSI 23, MISO 19, CS 5, DC 27, BL 32 (digital HIGH), RST tied to 3V3 so `TFT_RST -1` |
| FT6236 touch | SDA 21, SCL 22 on a dedicated `TwoWire(0)` at 100 kHz; CTP_RST tied to 3V3 (a GPIO reset line held the bus) |
| Pi link | RX 16 ← Pi GPIO14, TX 17 → Pi GPIO15. The final sketch does **not** use a second UART: it remaps the primary port, `Serial.begin(115200, SERIAL_8N1, 16, 17)`, so every `Serial.printf` goes to the Pi and the USB serial monitor is silent at runtime (uploads still work through the CH340 on GPIO1/3). The `HardwareSerial Link(2)` / `LINK_SERIAL` variant in chat 06 was proposed but is only a comment block in the file |

Toolchain that works (MacBook): Arduino IDE, board "ESP32 Dev Module", esp32
core 3.3.2, upload 921600 (115200 if flaky), DIO, 40 MHz, default 4 MB
partition, PSRAM off; TFT_eSPI 2.5.43 with the `User_Setup.h` kept in
`esp32/arduino/libraries/TFT_eSPI/` (ILI9341_DRIVER, 240×320, MISO 19 MOSI 23
SCLK 18 CS 5 DC 27 RST -1, `TFT_INVERSION_ON`, SPI 40 MHz); LVGL **8.3.11**
(LVGL 9 breaks everything); Adafruit FT6206 1.1.0; `lv_conf.h` in the sketch
folder with `LV_CONF_INCLUDE_SIMPLE`. The panel needs inversion ON. Colour byte
order in the final sketch: `LV_COLOR_16_SWAP 1` with `tft.setSwapBytes(false)`
(the other consistent pair is `SWAP 0` with `setSwapBytes(true)`). Rotation 3;
touch on `TwoWire(0)` at 100 kHz, `ts.begin(40, &TouchWire)`, map
`x = map(p.y, 0, 320, 320, 0)`, `y = map(p.x, 0, 240, 0, 240)`; draw buffer
320×40; `lv_tick_inc` in `loop()`.

SquareLine export rules learned the hard way: flatten `ui_*.c` into the sketch
root and change `#include "../ui.h"` to `"ui.h"`; never `#include` a `.c` from
the `.ino`; cast `lv_anim_enable_t` and `void*` in `ui_helpers.c`; enable every
`LV_FONT_MONTSERRAT_*` the UI uses; keep image assets ≤ 320 px (1024×1024 logos
overflowed DROM by 1.3 MB); functions called from generated C must be
`extern "C"` in the `.ino` and declared `extern` in `ui_events.c`.

## Pi ↔ ESP32 protocol (newline-terminated ASCII, working since 2 Nov 2025)
- Pi → ESP: `name:value\n`, value 0..127, e.g. `uic_pitchBar:90`, `uic_ModBar:83`, `uic_t1Arc1:64`.
- ESP → Pi: JSON lines `{"get":"uic_t1Arc1","val":47}` when a widget is moved,
  `{"set":"name","val":N}` echo after applying a command, `{"err":"unknown","name":"…"}`.
- Widget ids: `uic_t1Arc1..4`, `uic_t1Arc5Tempo` (also referred to as
  `uic_t1TempoArc`), `uic_pitchBar`, `uic_ModBar`. SquareLine events are
  VALUE_CHANGED → CALL FUNCTION `ui_event_t1Arc1` etc.
- What the final sketch actually implements: `parseSerialCommand()` handles
  only `uic_t1Arc1`, `uic_t1Arc2`, `uic_ModBar` and `uic_pitchBar` (bars
  clamped 0..127); `ui_events.c` sends `get` for Arc1–4 and both bars, and
  `ui_event_t1TempoArc` is empty. Arc3, Arc4 and the tempo arc still need
  parser cases, and `sendWidgetValue` is `extern "C"` in the `.ino` with an
  `extern` declaration at the top of `ui_events.c`.
- Test from the Pi: `echo "uic_t1Arc1:64" > /dev/serial0`.

## Software state (as of the last ChatGPT session, 8 Nov 2025)

| Subsystem | Status | Where the code is |
|---|---|---|
| Encoders ×5 via SX1509 | Working with the polling drivers in `pi/midibox/midio/`: `encoders_sx1509_poll2.py` (class `SX1509Encoders`, `begin()`, `read_and_zero()` → `(idx, delta, False)`, `close()`, x4 LUT, no buttons) and `encoders_sx1509_poll3.py` (same API plus the Arc1 press on P2 with hardware debounce; this is the "16:41" driver from the last chat). `encoders_sx1509.py` (interrupt) and `encoders_sx1509_driver.py` (smbus2 rewrite) are dead ends. Adding all five press pins made the tempo encoder self-oscillate; reverted | `pi/midibox/midio/` |
| SuperCore prototype | Tempo encoder + RGBW ring on GPIO13 + DRV2605L tick/confirm/end-stop, in sync. `pi/midibox/encoders_test.py` (8 Nov 2025, the last thing run) imports **poll3**, uses `RingMeter` (12 px, `top_offset=7`, vmin 20 / vmax 201, brightness 0.05, GRBW) and `apply_delta()`; it ignores the pressed flag, so the garbled press-print patch was reverted rather than fixed. `working_encoders_test.py` is the same on poll2; `encoders_test_buttons.py` differs only in ring colour. Bugs to know: the end-stop check tests `in (0, 201)` but tempo is clamped to 20..200, so it never fires; `RingMeter._color` is a stub | `pi/midibox/encoders_test.py`, `pi/home-scripts/supercore_ring.py` (earlier 16-px RGB version), `pi/home-scripts/drv2605l_*.py` |
| Pitch/mod wheels | Working: ADS1115 → `pi/midibox/midio/pi_pitch_mod_reader.py` (4 Nov 2025) → MIDI Pitch Bend + CC1, `uic_pitchBar`/`uic_ModBar` over `/dev/serial0`, and the two WS2811 wheel pixels. Smoothing alpha 0.7 in the file. Run from `~/midibox` as `sudo python3 -m midio.pi_pitch_mod_reader` (relative imports). The 2 Nov copy in `pi/home-scripts/` is older | `pi/midibox/midio/pi_pitch_mod_reader.py` |
| Optical faders | Working and calibrated: `pi/midibox/drivers/faders/infinium_x1_serial.py` (dataclass configs, `InfiniumX1Serial.process()` → event dict with `norm`), `apps/tests/test_infinium_dual_faders.py` (ttyAMA2 + ttyAMA3, CC 74 page "A"), `apps/tools/calibrate_controls.py` writing `config/calibration.json`. Fader 1 calibration is empty; scaling 1..126 and runtime loading in the main app not done | `pi/midibox/drivers/faders/`, `pi/midibox/apps/` |
| Headless I/O service | `pi/midibox/main.py` (4 Nov 2025) is only a ChatGPT skeleton: imports the interrupt driver and `ads1115_mod`, prints values, "later: send to ESP32". Nothing is wired together yet; no systemd service exists on the Pi | `pi/midibox/main.py` |
| Screen | ESP32 + LVGL + SquareLine: splashscreen, splashscreen2, MainPage with a TabView, encoder arcs `uic_t1Arc1..4`, `uic_t1Arc5Tempo`, pitch/mod bars, rollers for scale/rate/root, arp/scale checkboxes; `ui_events.c` has empty `scalePopulateFunction`, `ratePopulateFunction`, `arpTypeFunction`, `rootPopulateFunction`. Link to Pi working both ways for arcs 1–2 and the bars | Design `esp32/squareline/`; sketch `esp32/arduino/lvgl_hello_gui_SL_V3_pi_Comms/` |
| Keybed | Pico W "Plan A" worked (Oct 2025) with coarse velocity; KeySYS replaced it with proper key-time decoding | `~/KeySYS` |
| Original Pi app (Sep 2025) | `midibox/` package in this repo: PIL-drawn pages on the Pi's own SPI TFT, MPR121 pads, mido router. Superseded by the ESP32 screen but still the repo's only committed code | `midibox/`, `midibox_all.py` |
| MIDI routing, USB gadget mode, arpeggiator, banks, settings persistence | Designed only. Pi 4 USB-C gadget needs `dtoverlay=dwc2` and `g_midi`/configfs; never enabled | chats 37, 38 |
| Wheel LEDs (WS2811 on GPIO18), transport pads, 2 m keybed cable, case build | Not started or unconfirmed | — |

The Pi's `~/midibox` (snapshot in `pi/midibox/`) is a flat project folder,
not an installable package despite `pyproject.toml`: `midio/` (ADS, encoders,
wheel reader, the old mido `router.py`), `drivers/faders/`, `drivers/tft.py`
and `touch_ft6236.py` (old Pi screen), `apps/tests/`, `apps/tools/`,
`config/`, `tools/`, `leds/max7219_display.py`, `examples/`, `ui/` (old PIL
pages) and the loose test scripts. The folder `io/` was renamed `midio/`
because it shadowed the stdlib. Scripts are run from `~/midibox` with
`sudo python3 encoders_test.py` or `python3 -m midio.…` (see
`pi/system/services_and_uart.txt` and the Pi's bash history for what was
actually typed). Installed on the Pi: smbus2, pyserial, mido, python-rtmidi,
rpi-ws281x, adafruit-circuitpython-neopixel / drv2605 / ads1x15 / mpr121,
Blinka, luma.led-matrix, Pillow. Pip on Bookworm needs
`--break-system-packages` or a venv. No `dwc2`/gadget overlay is enabled.

## The service: all devices in one process, driving PatchSYS (11 Nov 2026)

`pi/midibox/service/` (deployed to `~/midibox/service/` on the Pi) is the first
program that runs every device at once, and it makes the box a PatchSYS
controller. Run it from `~/midibox` with `sudo python3 -m service.midibox_service`;
`service/README.md` has the flags and the control map. The design:

- **PatchSYS needs no change.** The Pi is a Link client with the same protocol
  as the iPad remote (`remote_link.py`, port 39276, Bonjour `_patchsys._tcp`):
  register, claim the writer lease, `set_parameter` with a monotonic sequence
  (latest value wins per control), actions, and the pushed confirmations.
  `service/link_client.py` is that client; `tools/link_standin.py` on the Mac
  is PatchSYS's own server class with a printing sink, for bench tests.
- **Encoders 1–4 → four of PatchSYS's eight semantic controls**, bank A
  (Filter Attack, Filter Release, Cutoff, Resonance) or bank B (Balance, Env
  Amount, Movement, Movement Speed); the Arc1 press toggles banks. Confirmed
  values come back and move the screen arcs, so the screen follows the app;
  a control being turned is protected from feedback for 300 ms.
- **SuperCore = the tempo encoder with ring and haptics, with modes.** TEMPO
  (cyan ring) sends `tempo`; DEPTH (amber) sends `set_depth`; a long press of
  Arc1 cycles the mode until the SuperCore's own switch (P14) is proven, after
  which `press_pin: 14` moves the roles onto it and a long press requests a
  VARIATION.
- Wheels stay MIDI pitch bend / CC1 (plus bars and pixels); faders are MIDI
  CC 7 / 74 unless configured onto a control.
- Both LED strips run from one `rpi_ws281x` instance (two channels), which is
  what lets the ring and the wheel pixels live in one process.

Verified on 11 Nov 2026 over SSH with the bench rig: all seven devices open
together; against the stand-in server every write and action arrived with no
errors; against PatchSYS Development on the Mac mini the box registered and saw
the target ONLINE (Serum 2). Physical turning was not tested (nobody at the
desk). `docs/MIDIBOX_LINK_CLIENT.md` in the PatchSYS repo records the client.

## Where it paused and the next steps ChatGPT and Stephen had agreed
1. Fix the garbled press-event prints in `encoders_test.py` (one line per event, line-buffered stdout), confirm Arc1 presses.
2. Enable presses 2–5 (P5, P8, P11, P14) one at a time, watching for the tempo-encoder oscillation. Root cause unknown; suspects are pull-up/debounce config, noise, or the haptics firing on every event.
3. Rename the tempo tag to SuperCore and wrap encoder + ring + haptics in one class; colour/theme presets.
4. Fit a real LRA; decide how to drive a second haptic (touchscreen) given the fixed DRV2605L address.
5. Integrate `main.py`: encoders + wheels + faders → MIDI and screen, loading `calibration.json`, with ESP32 feedback both ways.
6. Later: WS2811 wheel lights, MIDI routing page, USB gadget mode, arp/scale pages, case and faceplate.

Separately in KeySYS: the sustain pedal intermittently crashed the Pico (Jan
2026), the expression pedal on GP26 was unverified, aftertouch not handled.

## Known conflicts and unverified claims
- Keybed protocol: ChatGPT's SPI theory, the "walking-zero row markers", the
  C1/C2/C3 status-byte tables and the "inverted velocity nibble" were all
  guesses or partial. KeySYS's README has the real answer (the STM32 sends an
  11-bit key travel time). Treat chats 24, 27, 26, 17, 40 as history.
- Colour palettes differ between chats (#59F0E0 cyan on black; #00F0FF/#FF9900
  on #1C1F24; #00CFFF "Tron" blue). The SquareLine project holds the real ones.
- Whether the WS2811 wheel pixels lit as coded is unconfirmed (the code is
  there; the chats never reported a result).
- The digests describe the Pi link as `HardwareSerial Link(2)`; the file on
  disk remaps `Serial` instead. Trust the file.
- The 5-wire keybed harness colour-to-signal mapping flip-flopped; irrelevant
  now that KeySYS owns the keybed link.
- The debounce-code table and the dual-DRV2605L advice in the last chats are
  marked dubious by the digests.

## How Stephen likes to work (from the chats and ChatGPT's memory)
- Hobby build, no timelines; small steps, one module per feature, test with
  one-shot scripts before touching `main.py`.
- **Preserve code that already works; make minimal, targeted changes rather
  than rewriting.** Several ChatGPT rewrites were rejected for this reason.
- Read the real files before writing code; ChatGPT guessing class names and
  APIs caused most of the wasted days.
- Keep touchscreen code in separate page modules, not one huge file.
- Don't run a second Python process on the I2C bus while the app is running.
- Keep the Pi 4 for the prototype; a Pi-header base board and an open,
  community-style product come later.

## Sources
- `docs/captures/keybed-logic-analyser-2025-10-04/` — KingstVIS CSV exports
  of the keybed bus (one per key C1–C5, idle, and a MOSI timing burst); the
  bus they captured is the keybed-to-STM32 link, now KeySYS's business.
- `pi/macbook-older-code/` — the MacBook's "OLDER CODE" folder, including
  `midistream.txt`, the running-status fader parser class.
- `docs/chatgpt/digests/` — nine digests; start with `G6b.md` (latest state),
  `G6a.md` (Pi↔ESP link, wheels), `G3.md` (faders, keybed on the Pi),
  `G4b.md` (ESP32 bring-up), `G7-PM.md` (early plan).
- `docs/chatgpt/chats/` — full transcripts; headings `## Assistant · date` are
  cited by the digests when a final script exists only in a chat.
- `docs/chatgpt/chatgpt_memory_midibox.md` — ChatGPT's own summary.
- `docs/Midibox Build Overview.docx` — the original design overview (Sep 2025).
