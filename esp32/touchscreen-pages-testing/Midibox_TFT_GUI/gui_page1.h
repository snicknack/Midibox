#pragma once
#include <TFT_eSPI.h>
inline void drawPage1(TFT_eSPI &tft){
  tft.setTextColor(TFT_WHITE,TFT_BLACK);
  tft.drawString("Filter", 96, 40, 2);
  tft.drawRect(96, 62, 100, 24, TFT_WHITE);
  tft.drawString("Resonance", 96, 96, 2);
  tft.drawRect(96,118, 100, 24, TFT_WHITE);
  tft.drawString("Mod Amt", 96,152, 2);
  tft.drawRect(96,174, 100, 24, TFT_WHITE);
}
