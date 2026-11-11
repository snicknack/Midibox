#include <WiFi.h>
void setup() {
  Serial.begin(115200);
  delay(200);
  WiFi.mode(WIFI_STA);
  WiFi.disconnect(true);
  delay(500);
  Serial.println("\nScanning...");
}
void loop() {
  int n = WiFi.scanNetworks();
  Serial.printf("Found %d networks:\n", n);
  for (int i=0; i<n; i++) {
    Serial.printf("%2d: %s (%d dBm) %s\n", i+1, WiFi.SSID(i).c_str(), WiFi.RSSI(i),
                  (WiFi.encryptionType(i)==WIFI_AUTH_OPEN)?"open":"secured");
  }
  Serial.println("----");
  delay(2000);
}
