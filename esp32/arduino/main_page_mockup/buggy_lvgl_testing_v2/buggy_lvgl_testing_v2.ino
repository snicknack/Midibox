#include <Arduino.h>
#include <Wire.h>
#include <TFT_eSPI.h>          // SPI pins come from TFT_eSPI User_Setup
#include <Adafruit_FT6206.h>
#define LV_CONF_INCLUDE_SIMPLE
#include "lv_conf.h"   // directly, right before lvgl.h
#include <lvgl.h>

// ---------- Pins you asked to use ----------
#define SDA_PIN 21
#define SCL_PIN 22
#define TFT_BL  -1      // set to -1 if you have no BL pin
// ------------------------------------------

static const int SCR_W = 320;
static const int SCR_H = 240;
static const int BUF_LINES = 40;

TFT_eSPI tft;
Adafruit_FT6206 ts;

static lv_color_t buf1[SCR_W * BUF_LINES];
static lv_disp_draw_buf_t draw_buf;
static lv_disp_drv_t disp_drv;

static lv_indev_drv_t indev_drv;
static lv_indev_t* indev_touch;

// If your colors were correct only with invert, keep this true.
static const bool USE_INVERT = false;

// Simple touch rotation (MODE: 0..3). 0 = rotation(1) landscape default.
#define MODE 0

// ---------- LVGL display flush ----------
static void my_flush(lv_disp_drv_t *disp, const lv_area_t *area, lv_color_t *color_p) {
  int32_t w = area->x2 - area->x1 + 1;
  int32_t h = area->y2 - area->y1 + 1;

  tft.startWrite();
  tft.setAddrWindow(area->x1, area->y1, w, h);
  tft.pushColors((uint16_t*)color_p, w * h, true); // true = big-endian order
  tft.endWrite();

  lv_disp_flush_ready(disp);
}

// ---------- LVGL tick ----------
static uint32_t last_ms = 0;

// ---------- Touch read -> LVGL ----------
static void my_touch_read(lv_indev_drv_t *drv, lv_indev_data_t *data) {
  static uint16_t last_x = SCR_W / 2, last_y = SCR_H / 2;

  bool touched = ts.touched();
  if (!touched) {
    data->state = LV_INDEV_STATE_REL;
    data->point.x = last_x;
    data->point.y = last_y;
    return;
  }

  TS_Point p = ts.getPoint();   // raw FT6206 (x,y) 0..239 / 0..319 (sensor orientation)

  // Map raw to screen based on display rotation (MODE)
  uint16_t x, y;
  switch (MODE) {
    case 0: // tft.setRotation(1) -> landscape 320x240
      x = map(p.y, 0, 319, 0, SCR_W-1);
      y = map(p.x, 0, 239, SCR_H-1, 0);
      break;
    case 1: // rotation(1) but swapped
      x = map(p.y, 0, 319, SCR_W-1, 0);
      y = map(p.x, 0, 239, 0, SCR_H-1);
      break;
    case 2: // alternative if your glass is mounted flipped
      x = map(p.y, 0, 319, 0, SCR_W-1);
      y = map(p.x, 0, 239, 0, SCR_H-1);
      break;
    default:
      x = map(p.y, 0, 319, SCR_W-1, 0);
      y = map(p.x, 0, 239, SCR_H-1, 0);
      break;
  }

  last_x = constrain(x, 0, SCR_W-1);
  last_y = constrain(y, 0, SCR_H-1);
  data->state = LV_INDEV_STATE_PR;
  data->point.x = last_x;
  data->point.y = last_y;
}

void setup() {
  Serial.begin(115200);
  delay(50);

  // --- I2C for FT6206
  Wire.begin(SDA_PIN, SCL_PIN);

  // --- TFT
  tft.init();
  tft.setRotation(3);                 // 320x240 landscape
  tft.setSwapBytes(false);      // enable 16-bit byte swap for LVGL buffers
  if (USE_INVERT) tft.invertDisplay(true);
  if (TFT_BL >= 1) { pinMode(TFT_BL, OUTPUT); digitalWrite(TFT_BL, HIGH); }

  // Quick sanity paint so you know panel is alive
  tft.fillScreen(TFT_WHITE);

  // --- Touch
  Serial.println("Starting FT6236/FT6206...");
  if(!ts.begin(40, &Wire)) {          // threshold 40, using the Wire we configured
    Serial.println("FT6236/FT6206 NOT found");
  } else {
    Serial.println("FT6236 OK");
  }

  // --- LVGL
  lv_init();

  lv_disp_draw_buf_init(&draw_buf, buf1, NULL, SCR_W * BUF_LINES);
  lv_disp_drv_init(&disp_drv);
  disp_drv.hor_res = SCR_W;
  disp_drv.ver_res = SCR_H;
  disp_drv.flush_cb = my_flush;
  disp_drv.draw_buf = &draw_buf;
  disp_drv.user_data = &tft;
  lv_disp_drv_register(&disp_drv);

  // input device (touch)
  lv_indev_drv_init(&indev_drv);
  indev_drv.type = LV_INDEV_TYPE_POINTER;
  indev_drv.read_cb = my_touch_read;
  indev_touch = lv_indev_drv_register(&indev_drv);

  // background and a test label
  lv_obj_set_style_bg_color(lv_scr_act(), lv_color_hex(0x101214), 0);
  lv_obj_t* lbl = lv_label_create(lv_scr_act());
  lv_label_set_text(lbl, "LVGL + FT6206 OK");
  lv_obj_center(lbl);

  last_ms = millis();

  Serial.println("UI ready");
}

void loop() {
  // Advance LVGL tick (this fixes the “blank/black screen” issue)
  uint32_t now = millis();
  lv_tick_inc(now - last_ms);
  last_ms = now;

  lv_timer_handler();
  delay(5);
}
