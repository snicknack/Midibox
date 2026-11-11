#pragma once
#include <TFT_eSPI.h>
inline void drawPage3(TFT_eSPI &tft){
  tft.setTextColor(TFT_WHITE,TFT_BLACK);
  tft.drawString("Bank3: LFO / FX", 96, 60, 2);
}
