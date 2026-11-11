#include <Arduino.h>
#include <Wire.h>
#include <TFT_eSPI.h>
#include <Adafruit_FT6206.h>

#include "gui_page1.h"
#include "gui_page2.h"
#include "gui_page3.h"
#include "gui_common.h"

TFT_eSPI tft;
Adafruit_FT6206 ts;
int currentBank = 1;

void setup() {
  Serial.begin(115200);
  delay(300);
  Serial.println("\nBOOT");

  // Backlight (tie panel LED/BL to 3V3 if you don't use this pin)
#ifndef TFT_BL
#define TFT_BL 32
#endif
  pinMode(TFT_BL, OUTPUT);
  digitalWrite(TFT_BL, HIGH);

  tft.init();
  tft.setRotation(3);               // 0..3 as you like

  Wire.begin(21,22);
  bool ok = ts.begin(40, &Wire);    // FT6236 @ 0x38
  Serial.println(ok ? "Touch OK" : "Touch NOT found");

  drawChrome(tft, currentBank);
  drawPage1(tft);

  Serial.println("UI ready");
}

void loop() {
  static uint32_t hb=0;
  if (millis()-hb>1000) { hb=millis(); Serial.println("heartbeat"); }

  int16_t x,y;
  if (pointToScreen(ts,x,y)) {
    Serial.printf("Touch: %d,%d\n", x, y);
    tft.fillCircle(x, y, 3, TFT_YELLOW);

    int prev = currentBank;
    handleTouchBankButtons(x,y,currentBank);
    if (currentBank != prev) {
      tft.fillScreen(TFT_BLACK);
      drawChrome(tft, currentBank);
      switch (currentBank) {
        case 1: drawPage1(tft); break;
        case 2: drawPage2(tft); break;
        case 3: drawPage3(tft); break;
        default: drawPage1(tft); break;
      }
    }
  }
}
