# ESP32 touchscreen

- `arduino/lvgl_hello_gui_SL_V3_pi_Comms/` — **the sketch that runs on the
  box** (2 Nov 2025): LVGL 8.3.11 + TFT_eSPI + Adafruit FT6206, SquareLine UI,
  primary serial remapped to GPIO16/17 for the Pi link. Its `lv_conf.h` is
  the one that compiles.
- `arduino/libraries/TFT_eSPI/User_Setup.h` — the display pin file that goes in
  `~/Documents/Arduino/libraries/TFT_eSPI/` on whichever Mac builds it.
- `arduino/` (rest) — every earlier sketch from the MacBook, oldest to newest:
  `spi_sniffer*` (Oct 5–6, Pico-era keybed sniffing), `Midibox_TFT_GUI`
  (TFT_eSPI-only pages), `LVGL_Hello_Gui`, `lvgl_v8`, `smoke_test_lvgl_touch`,
  `main_page_mockup`, `lvgl_hello_gui_1..6_splash` and `basic_main_lvgl`
  (EEZ Studio era), `lvgl_hello_gui_SL_V1`, `SL_V2`. Five of them had 54–72 MB
  generated logo tables, which were left out; regenerate from the PNGs in
  `squareline/assets/` if ever needed.
- `squareline/` — the SquareLine Studio 1.5.4 project (from `~/SquareLine` on
  the Mac mini, saved 3 Nov 2025) with assets and seven backups. Open
  `SquareLine_Project.spj`; export into the sketch folder, flatten the
  screens/ files and fix `#include "../ui.h"` to `"ui.h"`.
- `export-2025-10-27/` — the first SquareLine export.
- `touchscreen-pages-testing/` — the MacBook's early `Midibox_TFT_GUI` copy.
- Build machine so far: the Intel MacBook Pro (Arduino IDE, esp32 core 3.3.2,
  board "ESP32 Dev Module", port `/dev/cu.usbserial-1460`).
