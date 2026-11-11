// ESP32 + ILI9341 (TFT_eSPI) + FT6236 touch + LVGL v8.x
// Wiring assumed:
//   SPI: MOSI=23, MISO=19, SCLK=18, CS=5, DC=27, RST->3V3  (so TFT_RST = -1 in User_Setup.h)
//   Touch (FT6236): SDA=21, SCL=22, INT (optional, not required), RST->3V3
// Notes: Your panel needs display inversion ON.

#include <Arduino.h>
#include <Wire.h>
#include <TFT_eSPI.h>
#include <Adafruit_FT6206.h>

#define LV_CONF_INCLUDE_SIMPLE
#include <lvgl.h>

// ---- Pins / panel geometry ----
static constexpr int SDA_PIN = 21;
static constexpr int SCL_PIN = 22;
static constexpr int TFT_BL  = 32;     // set to -1 if your backlight is hard-wired
static constexpr int SW = 320;         // screen width after rotation(3)
static constexpr int SH = 240;         // screen height after rotation(3)
static constexpr uint8_t ROT = 3;      // tft.setRotation

TFT_eSPI tft;
TwoWire TouchWire = TwoWire(0);        // dedicated I2C for touch
Adafruit_FT6206 ts;

// ------------ LVGL display buffers/driver ------------
static lv_color_t buf1[SW * 40];       // ~25KB, one small line buffer (40 rows)
static lv_disp_draw_buf_t draw_buf;
static lv_disp_drv_t disp_drv;
static lv_indev_drv_t indev_drv;

// Display flush: LVGL -> TFT_eSPI
static void my_disp_flush(lv_disp_drv_t *d, const lv_area_t *a, lv_color_t *color_p) {
  uint16_t w = a->x2 - a->x1 + 1;
  uint16_t h = a->y2 - a->y1 + 1;

  tft.startWrite();
  tft.setAddrWindow(a->x1, a->y1, w, h);
  // Pair with tft.setSwapBytes(true) and LV_COLOR_16_SWAP 0
  tft.pushImage(a->x1, a->y1, w, h, (uint16_t*)color_p);
  tft.endWrite();

  lv_disp_flush_ready(d);
}

// Touch read: FT6236 raw -> LVGL coords (for ROT=3)
static void my_touch_read(lv_indev_drv_t*, lv_indev_data_t *data) {
  static int16_t last_x = SW/2, last_y = SH/2;

  if (ts.touched()) {
    TS_Point p = ts.getPoint();        // p.x:0..240 (L->R), p.y:0..320 (T->B)
    int16_t x, y;
    switch (ROT) {
      case 0: x = map(p.x, 0,240, 0,SW); y = map(p.y, 0,320, 0,SH); break;
      case 1: x = map(p.y, 0,320, 0,SW); y = map(p.x, 0,240, SH,0); break;
      case 2: x = map(p.x, 0,240, SW,0); y = map(p.y, 0,320, SH,0); break;
      default: // ROT=3
        x = map(p.y, 0,320, SW,0);
        y = map(p.x, 0,240, 0,SH);
        break;
    }
    last_x = constrain(x, 0, SW-1);
    last_y = constrain(y, 0, SH-1);
    data->state   = LV_INDEV_STATE_PRESSED;
  } else {
    data->state   = LV_INDEV_STATE_RELEASED;
  }
  data->point.x = last_x;
  data->point.y = last_y;
}

void setup() {
  Serial.begin(115200);
  delay(150);
  Serial.println("\nBoot");

  // --- Touch first, on its own I2C at a conservative clock ---
  TouchWire.begin(SDA_PIN, SCL_PIN, 100000);
  delay(30);
  bool ok = ts.begin(40, &TouchWire);      // threshold 40 (typical)
  Serial.printf("FT6236 begin: %s @0x38\n", ok ? "OK" : "FAIL");

  // --- TFT init ---
  if (TFT_BL >= 0) { pinMode(TFT_BL, OUTPUT); digitalWrite(TFT_BL, HIGH); }
  tft.init();
  tft.setRotation(ROT);
  //tft.invertDisplay(true);                 // or set TFT_INVERSION_ON in User_Setup.h
  tft.setSwapBytes(true);                  // LVGL RGB565 buffer is little-endian

  // Quick direct draw sanity (optional):
  tft.fillScreen(TFT_BLACK);
  tft.setTextDatum(MC_DATUM);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.drawString("TFT OK", SW/2, SH/2, 2);
  delay(200);

  // --- LVGL init ---
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

  // --- Simple visible UI to verify colors + touch ---
  lv_obj_set_style_bg_opa  (lv_scr_act(), LV_OPA_COVER, 0);
  lv_obj_set_style_bg_color(lv_scr_act(), lv_color_hex(0x202428), 0); // dark grey

  lv_obj_t *title = lv_label_create(lv_scr_act());
  lv_label_set_text(title, "LVGL + ILI9341 + FT6236");
  lv_obj_align(title, LV_ALIGN_TOP_MID, 0, 6);

  lv_obj_t *btn = lv_btn_create(lv_scr_act());
  lv_obj_set_size(btn, 160, 80);
  lv_obj_center(btn);
  lv_obj_t *lbl = lv_label_create(btn);
  lv_label_set_text(lbl, "TOUCH");
  lv_obj_center(lbl);

  lv_obj_add_event_cb(btn, [](lv_event_t *e){
    static bool on = false; on = !on;
    lv_obj_t *b = lv_event_get_target(e);
    lv_obj_t *l = lv_obj_get_child(b, 0);
    lv_label_set_text(l, on ? "ON" : "OFF");
  }, LV_EVENT_CLICKED, nullptr);

  Serial.println("UI ready");
}

void loop() {
  // LVGL v8: you must advance ticks
  static uint32_t last = millis();
  uint32_t now = millis();
  lv_tick_inc(now - last);
  last = now;

  lv_timer_handler();
  delay(5);
}
