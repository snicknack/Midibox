// Pico W - Keybed SPI Sniffer (8-bit, windowed, stable DIFF)
// SCLK -> GP2, DATA (keybed DOUT/MISO) -> GP3, GND common
// LED blinks once per full capture window.

#include "hardware/gpio.h"

// -------------------- Pins --------------------
const uint8_t PIN_SCLK = 2;   // GP2
const uint8_t PIN_DATA = 3;   // GP3 (connect to keybed DOUT / MISO)

// -------------------- Timing (tune these) --------------------
// Arm a new capture window when no SCLK edges for >= IDLE_US
const uint32_t IDLE_US     = 6000;    // try 3000–8000 if needed
// Capture window length; your rig needed ~140 ms to contain a full scan
const uint32_t CAPTURE_US  = 140000;  // 140 ms window
// Reject SCLK echo edges closer than this (≈ one SCLK period ~2 µs)
const uint32_t MIN_EDGE_US = 2;

// -------------------- Buffer sizes --------------------
const uint16_t BYTES_MAX = 2000;  // headroom for long frames
const uint8_t  PRINT_LIMIT = 8;   // max changes to print per frame

// -------------------- State --------------------
volatile uint8_t  buf[BYTES_MAX];
volatile uint16_t byteCount = 0;
volatile uint8_t  bitCount  = 0;
volatile uint8_t  curByte   = 0;

volatile bool     capturing = false;
volatile bool     frameReady = false;
volatile uint16_t frameBytes = 0;

volatile uint32_t lastEdge = 0;
volatile uint32_t windowEnd = 0;

inline uint8_t fastReadDATA() { return gpio_get(PIN_DATA) ? 1 : 0; }

// -------------------- ISR --------------------
void onClkEdge() {
  uint32_t now = micros();
  uint32_t dt  = now - lastEdge;

  // Kill ringing/echo edges
  if (dt < MIN_EDGE_US) return;

  // First edge after idle -> open window
  if (!capturing && dt > IDLE_US) {
    capturing = true;
    byteCount = 0; bitCount = 0; curByte = 0;
    windowEnd = now + CAPTURE_US;
  }
  lastEdge = now;

  if (!capturing) return;

  // 8-bit MSB-first shift-in
  curByte = (curByte << 1) | fastReadDATA();
  if (++bitCount == 8) {
    if (byteCount < BYTES_MAX) buf[byteCount++] = curByte;
    bitCount = 0;
    curByte  = 0;
  }
}

// -------------------- Setup --------------------
void setup() {
  pinMode(PIN_SCLK, INPUT);           // leave clock unbiased
  pinMode(PIN_DATA, INPUT_PULLUP);    // important: stop DATA from floating when Hi-Z
  pinMode(LED_BUILTIN, OUTPUT);

  Serial.begin(115200);
  while (!Serial) { delay(1); }
  Serial.println("Pico W 8-bit keybed sniffer (windowed, stable DIFF)…");

  lastEdge = micros();
  // Try RISING first; if bytes look bit-shifted, change to FALLING.
  attachInterrupt(digitalPinToInterrupt(PIN_SCLK), onClkEdge, RISING);
}

// -------------------- Main loop --------------------
void loop() {
  uint32_t now = micros();

  // Close the capture window when time’s up
  if (capturing && (int32_t)(now - windowEnd) >= 0) {
    noInterrupts();
    frameBytes = byteCount;
    capturing  = false;
    frameReady = true;
    interrupts();
  }

  // History buffers for stability filter
  static uint8_t prev[BYTES_MAX];
  static uint8_t prev2[BYTES_MAX];
  static bool havePrev = false, havePrev2 = false;

  if (frameReady) {
    noInterrupts();
    uint16_t n = frameBytes;
    if (n > BYTES_MAX) n = BYTES_MAX;
    static uint8_t local[BYTES_MAX];
    for (uint16_t i = 0; i < n; ++i) local[i] = buf[i];
    frameReady = false;
    interrupts();

    // Heartbeat: once per full capture window (~7 Hz with 140 ms)
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));

    // Header preview (first 12 bytes) to verify stability / alignment
    Serial.print("FRAME "); Serial.print(n); Serial.print("  HDR:");
    uint16_t show = (n < 12 ? n : 12);
    for (uint16_t i = 0; i < show; ++i) {
      uint8_t v = local[i];
      if (v < 0x10) Serial.print('0');
      Serial.print(v, HEX); Serial.print(' ');
    }

    // 3-frame stability: only report bits that changed and stayed changed
    uint16_t printed = 0;
    if (havePrev && havePrev2) {
      Serial.print("  DIFF:");
      for (uint16_t i = 0; i < n; ++i) {
        uint8_t a = local[i], b = prev[i], c = prev2[i];
        uint8_t changed    = a ^ b;
        uint8_t same_as_b  = ~(a ^ c);       // 1s where a == c
        uint8_t stableMask = changed & same_as_b; // changed and remained
        if (stableMask) {
          // Report individual bits (MSB-first index 0..7)
          for (uint8_t bit = 0; bit < 8; ++bit) {
            uint8_t m = (1u << (7 - bit));
            if (stableMask & m) {
              uint8_t val = (a & m) ? 1 : 0;
              Serial.print(" ["); Serial.print(i); Serial.print('.');
              Serial.print(bit); Serial.print("]="); Serial.print(val);
              if (++printed >= PRINT_LIMIT) break;
            }
          }
        }
        if (printed >= PRINT_LIMIT) break;
      }
      if (printed == 0) Serial.print(" (none)");
    } else {
      Serial.print("  (learning baseline…)"); // first two frames
    }
    Serial.println();

    // Rotate history for next comparison
    if (havePrev) { for (uint16_t i = 0; i < n; ++i) prev2[i] = prev[i]; havePrev2 = true; }
    for (uint16_t i = 0; i < n; ++i) prev[i] = local[i];
    havePrev = true;
  }
}
