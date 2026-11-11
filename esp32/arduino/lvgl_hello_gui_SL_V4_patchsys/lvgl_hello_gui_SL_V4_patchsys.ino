#include <lvgl.h>

// ---- ESP32 + ILI9341 (TFT_eSPI) + FT6236 + LVGL 8.3.11 + SquareLine UI + PatchSYS page ----
// V4: the SL_V3_pi_Comms sketch plus ui_patchsys.c, a serial text form (name=text) and the
// missing arc cases. Hardware, pins and the Pi link are unchanged from V3.
#include <Arduino.h>
#include <Wire.h>
#include <TFT_eSPI.h>
#include <Adafruit_FT6206.h>

static inline int clampi(int v, int lo, int hi) {
  return v < lo ? lo : (v > hi ? hi : v);
}

#define LV_CONF_INCLUDE_SIMPLE

///////SERIAL LINK SETUP///////////
// The primary port is remapped to the Pi: ESP RX 16 <- Pi GPIO14, ESP TX 17 -> Pi GPIO15.
#define RX_PIN 16
#define TX_PIN 17

/* --- SquareLine headers (C) --- */
#include "ui_helpers.h"
#include "ui_events.h"
#include "ui_MainPage.h"
#include "ui_splashscreen.h"
#include "ui_splashscreen2.h"
#include "ui.h"
#include "ui_patchsys.h"

/////////CALLBACKS//////
extern "C" void sendWidgetValue(const char *name, int val) {
  Serial.printf("{\"get\":\"%s\",\"val\":%d}\n", name, val);
}

static constexpr int SDA_PIN = 21;
static constexpr int SCL_PIN = 22;
static constexpr int TFT_BL  = -1;     // -1 if no BL pin
static constexpr int SW = 320;         // after rotation(3)
static constexpr int SH = 240;
static constexpr uint8_t ROT = 3;

TFT_eSPI tft;
TwoWire TouchWire = TwoWire(0);
Adafruit_FT6206 ts;

// LVGL display buffers/driver
static lv_color_t buf1[SW * 40];       // ~25 KB
static lv_disp_draw_buf_t draw_buf;
static lv_disp_drv_t disp_drv;
static lv_indev_drv_t indev_drv;

// --------- LVGL -> TFT flush ----------
static void my_disp_flush(lv_disp_drv_t *d, const lv_area_t *a, lv_color_t *color_p) {
  uint16_t w = a->x2 - a->x1 + 1;
  uint16_t h = a->y2 - a->y1 + 1;

  tft.startWrite();
  tft.setAddrWindow(a->x1, a->y1, w, h);
  tft.pushImage(a->x1, a->y1, w, h, (uint16_t*)color_p);
  tft.endWrite();

  lv_disp_flush_ready(d);
}

// --------- Touch -> LVGL (ROT=3) ----------
static void my_touch_read(lv_indev_drv_t*, lv_indev_data_t *data) {
  static int16_t last_x = SW/2, last_y = SH/2;

  if (ts.touched()) {
    TS_Point p = ts.getPoint();  // p.x 0..240, p.y 0..320
    int16_t x = map(p.y, 0,320, SW,0);
    int16_t y = map(p.x, 0,240, 0,SH);
    last_x = constrain(x, 0, SW-1);
    last_y = constrain(y, 0, SH-1);
    data->state = LV_INDEV_STATE_PRESSED;
  } else {
    data->state = LV_INDEV_STATE_RELEASED;
  }
  data->point.x = last_x;
  data->point.y = last_y;
}

void setup() {
  Serial.begin(115200, SERIAL_8N1, RX_PIN, TX_PIN);
  delay(150);
  Serial.println("\nBoot (Stevies UI, V4 PatchSYS page)");

  // Touch on its own I2C
  TouchWire.begin(SDA_PIN, SCL_PIN, 100000);
  delay(30);
  bool ok = ts.begin(40, &TouchWire);
  Serial.printf("FT6236 begin: %s @0x38\n", ok ? "OK" : "FAIL");

  // TFT
  if (TFT_BL >= 0) { pinMode(TFT_BL, OUTPUT); digitalWrite(TFT_BL, HIGH); }
  tft.init();
  tft.setRotation(ROT);
  tft.invertDisplay(true);     // important for your panel
  tft.setSwapBytes(false);     // LV_COLOR_16_SWAP 1 in lv_conf.h
  tft.fillScreen(TFT_BLACK);

  // LVGL
  lv_init();
  lv_disp_draw_buf_init(&draw_buf, buf1, NULL, SW * 40);

  lv_disp_drv_init(&disp_drv);
  disp_drv.hor_res  = SW;
  disp_drv.ver_res  = SH;
  disp_drv.draw_buf = &draw_buf;
  disp_drv.flush_cb = my_disp_flush;
  lv_disp_t *disp = lv_disp_drv_register(&disp_drv);
  (void)disp;

  lv_indev_drv_init(&indev_drv);
  indev_drv.type    = LV_INDEV_TYPE_POINTER;
  indev_drv.read_cb = my_touch_read;
  lv_indev_drv_register(&indev_drv);

  // SquareLine screens (splash -> splash2 -> MainPage), then the PatchSYS page alongside
  ui_init();
  ui_patchsys_screen_init();

  Serial.println("UI ready");
}

String serialBuffer = "";
void loop() {
  static uint32_t last = millis();
  uint32_t now = millis();
  lv_tick_inc(now - last);
  last = now;

  lv_timer_handler();
  handleSerialInput();
  delay(5);
}

//------------------------------------------------------------
// 2-way Serial <-> LVGL bridge
//------------------------------------------------------------

// ------------------ Incoming (Pi -> ESP32) ------------------
void handleSerialInput() {
  while (Serial.available()) {
    char c = (char)Serial.read();

    if (c == '\n' || c == '\r') {
      if (serialBuffer.length() > 0) {
        parseSerialCommand(serialBuffer);
        serialBuffer = "";
      }
    } else if (serialBuffer.length() < 160) {
      serialBuffer += c;
    } else {
      serialBuffer = "";   // overrun: drop the line
    }
  }
}

void parseSerialCommand(String cmd) {
  int colon = cmd.indexOf(':');
  int eq = cmd.indexOf('=');

  // text form: name=text  (only when '=' comes before any ':' so values like "a:b" still work)
  if (eq != -1 && (colon == -1 || eq < colon)) {
    String name = cmd.substring(0, eq);
    String text = cmd.substring(eq + 1);
    if (ui_patchsys_set_text(name.c_str(), text.c_str())) {
      Serial.printf("{\"set\":\"%s\",\"text\":1}\n", name.c_str());
    } else {
      Serial.printf("{\"err\":\"unknown\",\"name\":\"%s\"}\n", name.c_str());
    }
    return;
  }
  if (colon == -1) return;

  String name = cmd.substring(0, colon);
  int value = cmd.substring(colon + 1).toInt();

  if (name.startsWith("ps_")) {
    if (ui_patchsys_set_int(name.c_str(), value)) {
      Serial.printf("{\"set\":\"%s\",\"val\":%d}\n", name.c_str(), value);
    } else {
      Serial.printf("{\"err\":\"unknown\",\"name\":\"%s\"}\n", name.c_str());
    }
    return;
  }

  // ---- the SquareLine MIDI page ----
  if (name == "uic_t1Arc1")          lv_arc_set_value(uic_t1Arc1, clampi(value, 0, 127));
  else if (name == "uic_t1Arc2")     lv_arc_set_value(uic_t1Arc2, clampi(value, 0, 127));
  else if (name == "uic_t1Arc3")     lv_arc_set_value(uic_t1Arc3, clampi(value, 0, 127));
  else if (name == "uic_t1Arc4")     lv_arc_set_value(uic_t1Arc4, clampi(value, 0, 127));
  else if (name == "uic_t1Arc5Tempo") lv_arc_set_value(uic_t1Arc5Tempo, clampi(value, 50, 200));
  else if (name == "uic_ModBar")     lv_bar_set_value(uic_ModBar, clampi(value, 0, 127), LV_ANIM_OFF);
  else if (name == "uic_pitchBar")   lv_bar_set_value(uic_pitchBar, clampi(value, 0, 127), LV_ANIM_OFF);
  else {
    Serial.printf("{\"err\":\"unknown\",\"name\":\"%s\"}\n", name.c_str());
    return;
  }

  Serial.printf("{\"set\":\"%s\",\"val\":%d}\n", name.c_str(), value); // confirm
}
