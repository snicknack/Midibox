#pragma once
#include <TFT_eSPI.h>
#include <Adafruit_FT6206.h>

#define SW 320
#define SH 240

inline void drawChrome(TFT_eSPI &tft, int bank){
  tft.fillScreen(TFT_BLACK);
  tft.fillRect(0,0,SW,24,TFT_DARKGREY);
  tft.setTextColor(TFT_WHITE,TFT_DARKGREY);
  tft.setTextDatum(TL_DATUM);
  tft.drawString("Midibox Touch GUI",6,4);
  tft.drawRightString(String("Bank ")+bank, SW-6,4,2);

  for (int b=1;b<=4;++b){
    int y=30+(b-1)*50;
    uint16_t col=(b==bank)?TFT_YELLOW:TFT_NAVY;
    tft.fillRoundRect(6,y,70,40,6,col);
    tft.drawRoundRect(6,y,70,40,6,TFT_WHITE);
    tft.setTextColor(TFT_WHITE,col);
    tft.drawCentreString(String("B")+b, 41, y+12, 2);
  }

  tft.drawRect(86,30, SW-92, SH-36, TFT_RED);
}

inline bool pointToScreen(Adafruit_FT6206 &ts, int16_t &sx, int16_t &sy){
  if(!ts.touched()) return false;
  TS_Point p=ts.getPoint();               // FT6236 raw x~0..240, y~0..320
  // mapping for setRotation(3)
  sx = map(p.y, 0, 320, SW, 0);
  sy = map(p.x, 0, 240, 0, SH);
  if (sx<0) sx=0; if (sx>SW-1) sx=SW-1;
  if (sy<0) sy=0; if (sy>SH-1) sy=SH-1;
  return true;
}

inline void handleTouchBankButtons(int x,int y,int &bank){
  for (int b=1;b<=4;++b){
    int bx=6, by=30+(b-1)*50, bw=70, bh=40;
    if (x>=bx && x<bx+bw && y>=by && y<by+bh){ bank=b; return; }
  }
}
