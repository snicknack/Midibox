// Pico W – Keybed SPI Sniffer (16-bit words, windowed, stable DIFF)
// SCLK -> GP2 (33–68 Ω series, optional 22–47 pF to GND at Pico)
// DATA -> GP3 (keybed DOUT/MISO). Add 47–33 kΩ pull-up to 3V3 if floating.
// GND  -> GND (common)
//
// This captures a full scan window, packs 16-bit MSB-first words,
// prints a short header preview, and only reports indices that
// changed and stayed changed across 2 frames (stability filter).

#include "hardware/gpio.h"

// ---------------- Pins ----------------
const uint8_t PIN_SCLK = 2;  // GP2
const uint8_t PIN_DATA = 3;  // GP3 (keybed DOUT/MISO)

// ------------- Tuning -----------------
// Start a capture on first edge after >= IDLE_US idle
const uint32_t IDLE_US     = 6000;     // try 3000–8000 if needed
// Capture window long enough to hold one full scan on your rig
const uint32_t CAPTURE_US  = 140000;   // 140 ms; trim down later if stable
// Ignore SCLK echo edges closer than this (~ one SCLK period ~2 µs)
const uint32_t MIN_EDGE_US = 2;

// ------------- Buffers ----------------
const uint16_t WORDS_MAX   = 2000;     // plenty of headroom
const uint8_t  PRINT_LIMIT = 8;        // limit DIFF items per frame

volatile uint16_t buf[WORDS_MAX];
volatile uint16_t wordCount = 0;
volatile uint8_t  bitCount  = 0;
volatile uint16_t curWord   = 0;

volatile bool     capturing = false;
volatile bool     frameReady = false;
volatile uint16_t frameWords = 0;

volatile uint32_t lastEdge = 0;
volatile uint32_t windowEnd = 0;

// Fast read of DATA pin
inline uint8_t fastReadDATA() { return gpio_get(PIN_DATA) ? 1 : 0; }

// ------------- ISR --------------------
void onClkEdge() {
  uint32_t now = micros();
  uint32_t dt  = now - lastEdge;

  if (dt < MIN_EDGE_US) return;        // kill ringing/echo edges

  // First edge after idle -> open a new window
  if (!capturing && dt > IDLE_US) {
    capturing  = true;
    wordCount  = 0;
    bitCount   = 0;
    curWord    = 0;
    windowEnd  = now + CAPTURE_US;
  }
  lastEdge = now;

  if (!capturing) return;

  // ----- 16-bit MSB-first -----
  curWord = (curWord << 1) | fastReadDATA();
  if (++bitCount == 16) {
    if (wordCount < WORDS_MAX) buf[wordCount++] = curWord;
    bitCount = 0;
    curWord  = 0;
  }
}

// ------------- Setup ------------------
void setup() {
  pinMode(PIN_SCLK, INPUT_PULLUP);           // leave clock unbiased
  pinMode(PIN_DATA, INPUT_PULLUP);    // helps if line floats between bursts
  pinMode(LED_BUILTIN, OUTPUT);

  Serial.begin(115200);
  while (!Serial) { delay(1); }
  Serial.println("Pico W 16-bit keybed sniffer (windowed, stable DIFF)…");

  lastEdge = micros();
  // Try RISING first; if words look bit-shifted, switch to FALLING.
  attachInterrupt(digitalPinToInterrupt(PIN_SCLK), onClkEdge, FALLING);
}

// ------------- Main loop --------------
void loop() {
  uint32_t now = micros();

  // Close the capture window when time's up
  if (capturing && (int32_t)(now - windowEnd) >= 0) {
    noInterrupts();
    frameWords = wordCount;
    capturing  = false;
    frameReady = true;
    interrupts();
  }

  // History for stability filtering
  static uint16_t prev[WORDS_MAX];
  static uint16_t prev2[WORDS_MAX];
  static bool havePrev = false, havePrev2 = false;

  if (frameReady) {
    noInterrupts();
    uint16_t n = frameWords;
    if (n > WORDS_MAX) n = WORDS_MAX;
    static uint16_t local[WORDS_MAX];
    for (uint16_t i = 0; i < n; ++i) local[i] = buf[i];
    frameReady = false;
    interrupts();

    // Heartbeat: toggles once per full capture window
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));

    // Header preview to check stability/alignment
    Serial.print("FRAME "); Serial.print(n); Serial.print("  HDR:");
    uint16_t show = (n < 8 ? n : 8);
    for (uint16_t i = 0; i < show; ++i) {
      uint16_t v = local[i];
      if (v < 0x1000) Serial.print('0');
      if (v < 0x0100) Serial.print('0');
      if (v < 0x0010) Serial.print('0');
      Serial.print(v, HEX); Serial.print(' ');
    }

    // 2-frame stability DIFF: report indices that changed and stayed changed
    uint16_t printed = 0;
    if (havePrev) {
      Serial.print("  DIFF:");
      for (uint16_t i = 0; i < n; ++i) {
        bool changed = (local[i] != prev[i]);
        bool stable  = havePrev2 && (prev[i] == prev2[i]); // last state persisted
        if (changed && stable) {
          Serial.print(" ["); Serial.print(i); Serial.print("]=");
          uint16_t v = local[i];
          if (v < 0x1000) Serial.print('0');
          if (v < 0x0100) Serial.print('0');
          if (v < 0x0010) Serial.print('0');
          Serial.print(v, HEX);
          if (++printed >= PRINT_LIMIT) break;
        }
      }
      if (printed == 0) Serial.print(" (none)");
    } else {
      Serial.print("  (baseline…)"); // first frame learns baseline
    }
    Serial.println();

    // Rotate histories
    if (havePrev) { for (uint16_t i = 0; i < n; ++i) prev2[i] = prev[i]; havePrev2 = true; }
    for (uint16_t i = 0; i < n; ++i) prev[i] = local[i];
    havePrev = true;
  }
}
