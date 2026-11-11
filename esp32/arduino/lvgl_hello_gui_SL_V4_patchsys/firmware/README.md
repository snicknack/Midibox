# Built firmware: lvgl_hello_gui_SL_V4_patchsys

Compiled 11 Nov 2026 on the MacBook with the Arduino IDE's arduino-cli 1.2.0,
esp32 core 3.3.2, board "ESP32 Dev Module", DIO, 40 MHz, default 4 MB
partition. Sketch 1,214,863 bytes (92 % of the app partition).

## Flash from the MacBook (ESP32 on its USB)

    CLI="/Applications/Arduino IDE.app/Contents/Resources/app/lib/backend/resources/arduino-cli"
    cd ~/Documents/Arduino
    "$CLI" --config-file ~/.arduinoIDE/arduino-cli.yaml upload -p /dev/cu.usbserial-1460 \
      --fqbn esp32:esp32:esp32 lvgl_hello_gui_SL_V4_patchsys

or open the sketch in the Arduino IDE and press Upload.

## Flash from the Pi or any machine with esptool (ESP32 on its USB)

    pip install esptool          # on the Pi: pip install --break-system-packages esptool
    esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 write_flash \
      0x1000  lvgl_hello_gui_SL_V4_patchsys.ino.bootloader.bin \
      0x8000  lvgl_hello_gui_SL_V4_patchsys.ino.partitions.bin \
      0x10000 lvgl_hello_gui_SL_V4_patchsys.ino.bin

Hold BOOT on the board while it connects if the upload says it cannot
connect. The Pi link keeps working during flashing (the bootloader uses the
USB pins, not GPIO16/17).
