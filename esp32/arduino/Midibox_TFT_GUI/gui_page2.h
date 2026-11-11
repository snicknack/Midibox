#pragma once
#include <TFT_eSPI.h>
inline void drawPage2(TFT_eSPI &tft){
  const char* names[4]={"Attack","Decay","Sustain","Release"};
  for (int i=0;i<4;i++){
    int y=40+i*45;
    tft.drawString(names[i], 96, y, 2);
    tft.drawRect(160, y+20, 120, 24, TFT_WHITE);
  }
}
