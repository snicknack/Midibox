#include <Arduino.h>
#include <Wire.h>
#include <TFT_eSPI.h>
#include <Adafruit_FT6206.h>
#define LV_CONF_INCLUDE_SIMPLE
#include <lvgl.h>


// ---------- Your wiring / panel ----------
#define SDA_PIN 21
#define SCL_PIN 22
#define TFT_BL  32          // tie to 3V3 if you prefer

static const int SW = 320;  // after rotation
static const int SH = 240;

// ---------- Globals ----------
TFT_eSPI tft;
Adafruit_FT6206 ts;
static lv_color_t buf1[SW * 40];     // 2.5KB line buffer (40 lines)
static lv_disp_draw_buf_t draw_buf;
static lv_disp_drv_t disp_drv;
static lv_indev_drv_t indev_drv;

static uint8_t current_bank = 1;

// ---------- LVGL Display flush using TFT_eSPI ----------
static void my_disp_flush(lv_disp_drv_t *d, const lv_area_t *a, lv_color_t *p) {
  uint16_t w = a->x2 - a->x1 + 1;
  uint16_t h = a->y2 - a->y1 + 1;

  tft.startWrite();
  tft.setAddrWindow(a->x1, a->y1, w, h);
  // LVGL uses RGB565 when LV_COLOR_DEPTH=16. Cast buffer to 16-bit.
  tft.pushColors((uint16_t *)&p->full, w * h, true);
  tft.endWrite();

  lv_disp_flush_ready(d);
}

// ---------- LVGL Touch (FT6236) ----------
static void my_touch_read(lv_indev_drv_t *d, lv_indev_data_t *data) {
  static int16_t last_x = 0, last_y = 0;
  if (ts.touched()) {
    TS_Point p = ts.getPoint();
    // Mapping for tft.setRotation(3): (landscape flipped)
    int16_t x = map(p.y, 0, 320, SW, 0);
    int16_t y = map(p.x, 0, 240, 0, SH);
    x = constrain(x, 0, SW - 1);
    y = constrain(y, 0, SH - 1);

    last_x = x; last_y = y;
    data->state = LV_INDEV_STATE_PRESSED;
    data->point.x = last_x;
    data->point.y = last_y;
  } else {
    data->state = LV_INDEV_STATE_RELEASED;
    data->point.x = last_x;
    data->point.y = last_y;
  }
}

// ---------- Simple UI: header + bank buttons + page ----------
lv_obj_t *header, *left_col, *content;
lv_obj_t *slider_cut, *slider_res, *slider_mod;
lv_obj_t *label_cut, *label_res, *label_mod;

static void draw_header() {
  header = lv_obj_create(lv_scr_act());
  lv_obj_set_size(header, SW, 24);
  lv_obj_set_style_bg_color(header, lv_color_hex(0x444444), 0);
  lv_obj_align(header, LV_ALIGN_TOP_MID, 0, 0);

  lv_obj_t *title = lv_label_create(header);
  lv_label_set_text(title, "Midibox LVGL GUI");
  lv_obj_align(title, LV_ALIGN_LEFT_MID, 6, 0);

  lv_obj_t *bank = lv_label_create(header);
  static char buf[16];
  snprintf(buf, sizeof(buf), "Bank %u", current_bank);
  lv_label_set_text(bank, buf);
  lv_obj_align(bank, LV_ALIGN_RIGHT_MID, -6, 0);
}

static void draw_left_banks() {
  left_col = lv_obj_create(lv_scr_act());
  lv_obj_set_size(left_col, 80, SH - 24);
  lv_obj_align(left_col, LV_ALIGN_BOTTOM_LEFT, 0, 0);
  lv_obj_set_style_pad_all(left_col, 6, 0);
  lv_obj_set_style_bg_color(left_col, lv_color_hex(0x111633), 0);

  for (int b = 1; b <= 4; ++b) {
    lv_obj_t *btn = lv_btn_create(left_col);
    lv_obj_set_width(btn, 68);
    lv_obj_set_height(btn, 40);
    lv_obj_align(btn, LV_ALIGN_TOP_MID, 0, (b - 1) * 48);
    if (b == current_bank) {
      lv_obj_set_style_bg_color(btn, lv_palette_main(LV_PALETTE_YELLOW), LV_STATE_DEFAULT);
    }
    lv_obj_set_user_data(btn, (void *)(intptr_t)b);
    lv_obj_add_event_cb(btn, [](lv_event_t *e){
      int b = (int)(intptr_t)lv_event_get_user_data(e);
      current_bank = b;
      // redraw content
      lv_obj_del(content);
      // update header text
      lv_obj_t *bankLbl = lv_obj_get_child(header, 1); // right label
      static char buf[16]; snprintf(buf, sizeof(buf), "Bank %u", current_bank);
      lv_label_set_text(bankLbl, buf);
      // draw new page
      // (for demo we always draw "Filter" page; extend with switch later)
      content = lv_obj_create(lv_scr_act());
      lv_obj_set_size(content, SW - 86, SH - 30);
      lv_obj_align(content, LV_ALIGN_BOTTOM_RIGHT, 0, 0);
      lv_obj_set_style_border_color(content, lv_palette_main(LV_PALETTE_RED), 0);
      lv_obj_set_style_border_width(content, 2, 0);

      // page widgets again
      // (in a real app you'd call page-specific builder functions)
      // re-create sliders:
      // (omitted here to keep the demo short—see initial draw below)
    }, LV_EVENT_CLICKED, (void *)(intptr_t)b);

    lv_obj_t *lbl = lv_label_create(btn);
    char txt[8]; snprintf(txt, sizeof(txt), "B%d", b);
    lv_label_set_text(lbl, txt);
    lv_obj_center(lbl);
  }
}

static void draw_filter_page() {
  content = lv_obj_create(lv_scr_act());
  lv_obj_set_size(content, SW - 86, SH - 30);
  lv_obj_align(content, LV_ALIGN_BOTTOM_RIGHT, 0, 0);
  lv_obj_set_style_border_color(content, lv_palette_main(LV_PALETTE_RED), 0);
  lv_obj_set_style_border_width(content, 2, 0);
  lv_obj_set_style_pad_all(content, 8, 0);
  lv_obj_set_style_bg_color(content, lv_color_hex(0x000000), 0);

  auto make_slider = [](const char* name, lv_coord_t y, lv_obj_t **out_slider, lv_obj_t **out_label){
    lv_obj_t *lbl = lv_label_create(content);
    lv_label_set_text(lbl, name);
    lv_obj_align(lbl, LV_ALIGN_TOP_LEFT, 6, y);

    lv_obj_t *s = lv_slider_create(content);
    lv_obj_set_width(s, 200);
    lv_obj_align(s, LV_ALIGN_TOP_LEFT, 80, y - 4);
    lv_slider_set_range(s, 0, 127);
    lv_obj_add_event_cb(s, [](lv_event_t *e){
      lv_obj_t *s = lv_event_get_target(e);
      int v = lv_slider_get_value(s);
      // TODO: send over UART as JSON CC (e.g., cutoff=74)
      // (we'll wire this after you confirm LVGL is up)
    }, LV_EVENT_VALUE_CHANGED, NULL);

    *out_slider = s;
    *out_label = lbl;
  };

  make_slider("Cutoff",     10, &slider_cut, &label_cut);
  make_slider("Resonance",  50, &slider_res, &label_res);
  make_slider("Mod Amt",    90, &slider_mod, &label_mod);
}

void setup() {
  // Backlight + TFT
  pinMode(TFT_BL, OUTPUT); digitalWrite(TFT_BL, HIGH);
  tft.init(); tft.setRotation(3);

  // Touch (I2C)
  Wire.begin(SDA_PIN, SCL_PIN);
  
  // Ensure CTP_RST on your board is tied to 3V3
  ts.begin(40, &Wire);

  // LVGL init
  lv_init();
  lv_disp_draw_buf_init(&draw_buf, buf1, NULL, SW * 40);
  lv_disp_drv_init(&disp_drv);
  disp_drv.hor_res = SW;
  disp_drv.ver_res = SH;
  disp_drv.flush_cb = my_disp_flush;
  disp_drv.draw_buf = &draw_buf;
  lv_disp_drv_register(&disp_drv);

  lv_indev_drv_init(&indev_drv);
  indev_drv.type = LV_INDEV_TYPE_POINTER;
  indev_drv.read_cb = my_touch_read;
  lv_indev_drv_register(&indev_drv);

  // Build UI
  draw_header();
  draw_left_banks();
  draw_filter_page();
}

void loop() {
  lv_timer_handler();   // run LVGL tasks
  delay(5);             // ~200 Hz UI loop
}
