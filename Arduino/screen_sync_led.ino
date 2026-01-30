#include <Adafruit_NeoPixel.h>

#define LED_PIN 6
#define NUM_LEDS 34

Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  Serial.begin(115200);
  strip.begin();
  strip.setBrightness(200);
  strip.show();
}

void loop() {
  if (Serial.available() > 0) {
    for (int i = 0; i < NUM_LEDS; i++) {
      while (Serial.available() < 3);
      strip.setPixelColor(
        i,
        Serial.read(),
        Serial.read(),
        Serial.read()
      );
    }
    strip.show();
  }
}
