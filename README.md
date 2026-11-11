# Midibox

Desktop MIDI controller and new brain for a Studiologic SL88 whose main board
died. Holson Instruments "MIDI PLAYGROUND".

- **Raspberry Pi 4** — the brain: five encoders (SX1509), pitch/mod wheels
  (ADS1115), two Behringer Infinium X1 optical faders, NeoPixel ring and
  DRV2605L haptics on the SuperCore encoder, MIDI out, future USB host/gadget.
- **ESP32** — the 3.2" touchscreen (ILI9341 + FT6236) running LVGL 8.3.11 with
  a SquareLine Studio UI, linked to the Pi over UART.
- **Pico W** — reads the keybed's STM32 scanner board and appears as USB MIDI.
  That part lives in its own repo, `~/KeySYS`.

## Layout

| Path | What |
|---|---|
| `CLAUDE.md` | State of the project, hardware map, protocol, next steps. Read this first. |
| `midibox/`, `midibox_all.py` | The original Sep 2025 Pi app (PIL pages on the Pi's own SPI TFT). Superseded by the ESP32 screen. |
| `imports/chatgpt-sources/pi/` | Pi-side scripts as uploaded to ChatGPT (encoders, ADS1115, main). The Pi's `~/midibox` is the live copy. |
| `imports/chatgpt-sources/esp32/` | SquareLine export of the screen UI plus an early copy of the Arduino sketch. |
| `gui/eez/` | EEZ Studio GUI projects, theme and font packs (abandoned for SquareLine in Oct 2025). |
| `docs/` | Design overview, and `docs/chatgpt/` with every ChatGPT transcript and digest. |

## Working on it

Pi: `ssh stephennicholson@midibox.local`, project in `~/midibox`, run modules
from there with `python3 -m …` (`sudo` for NeoPixels and serial).

ESP32: Arduino IDE, board "ESP32 Dev Module", LVGL 8.3.11, TFT_eSPI 2.5.43.
Pin map and export rules are in `CLAUDE.md`.
