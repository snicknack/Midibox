#include <lvgl.h>

// ---- ESP32 + ILI9341 (TFT_eSPI) + FT6236 + LVGL 8.3.11 + EEZ UI ----
#include <Arduino.h>
#include <Wire.h>
#include <TFT_eSPI.h>
#include <Adafruit_FT6206.h>

#define LV_CONF_INCLUDE_SIMPLE

///////SERIAL LINK SETUP///////////
#define RX_PIN 20
#define TX_PIN 21


//#include <screens/screens.h>
//#include <styles.h>

/* --- SquareLine headers (C) --- */

#include "ui_helpers.h"
#include "ui_events.h"
#include "ui_MainPage.h"
#include "ui_splashscreen.h"
#include "ui_splashscreen2.h"
#include "ui.h"           // from your SquareLine export

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
  // Using little-endian LVGL RGB565 + setSwapBytes(true)
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
  Serial.println("\nBoot (Stevies UI)");

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
  tft.setSwapBytes(false);      // match LVGL RGB565 order
  tft.fillScreen(TFT_BLACK);   // quick sanity

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

  // ---- EEZ Studio UI ----
  ui_init();   // EEZ generated; builds your Main screen etc.
  // If EEZ generated a start-screen helper, you can call it here:
  // ui_set_start_screen(&main, LV_SCR_LOAD_ANIM_FADE_ON, 300, 0);

  Serial.println("UI ready");
}
String serialBuffer = "";
void loop() {
  static uint32_t last = millis();
  uint32_t now = millis();
  lv_tick_inc(now - last);
  last = now;

  lv_timer_handler();
  handleSerialInput();         // custom function below
  delay(5);
}

///------------------------------------------------------------
// 2-way Serial <-> LVGL bridge
//------------------------------------------------------------

///
///void loop() {
///  lv_timer_handler();   // keep LVGL running
///  handleSerialInput();  // listen for Pi commands
///  delay(5);
///}

// ------------------ Incoming (Pi -> ESP32) ------------------
void handleSerialInput() {
  while (Serial.available()) {
    char c = (char)Serial.read();

    if (c == '\n' || c == '\r') {
      if (serialBuffer.length() > 0) {
        parseSerialCommand(serialBuffer);
        serialBuffer = "";
      }
    } else serialBuffer += c;
  }
}

void parseSerialCommand(String cmd) {
  int colon = cmd.indexOf(':');
  if (colon == -1) return;

  String name = cmd.substring(0, colon);
  int value = cmd.substring(colon + 1).toInt();

  // ---- match any widget you want controllable ----
  if (name == "uic_t1Arc1")      lv_arc_set_value(uic_t1Arc1, value);
  else if (name == "uic_t1Arc2") lv_arc_set_value(uic_t1Arc2, value);
  else if (name == "uic_ModBar") lv_bar_set_value(uic_ModBar, value, LV_ANIM_OFF);
  else if (name == "uic_pitchBar") lv_bar_set_value(uic_pitchBar, value, LV_ANIM_OFF);
  // add more as needed

  Serial.printf("{\"set\":\"%s\",\"val\":%d}\n", name.c_str(), value); // confirm
}

// ------------------ Outgoing (ESP32 -> Pi) ------------------
// Call this from any LVGL event handler when a control changes
extern "C" void sendWidgetValue(const char *name, int val) {
  Serial.printf("{\"get\":\"%s\",\"val\":%d}\n", name, val);
}
