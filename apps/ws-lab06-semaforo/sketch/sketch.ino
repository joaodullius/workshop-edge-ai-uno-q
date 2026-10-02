#include <Arduino_Modulino.h>
#include <Arduino_RouterBridge.h>

ModulinoDistance distance;
ModulinoPixels   leds;

void setup() {
    Bridge.begin();
    Modulino.begin(Wire1);
    distance.begin();
    leds.begin();
}

void loop() {
    if (distance.available()) {
        float cm = distance.get() / 10.0;          // get() devolve milimetros
        uint8_t r = cm < 10 ? 255 : (cm < 50 ? 255 : 0);
        uint8_t g = cm < 10 ? 0   : 255;
        for (int i = 0; i < 8; i++) leds.set(i, r, g, 0, 25);
        leds.show();
        Bridge.notify("record_distance", cm);      // e o Python recebe a leitura
    }
    delay(500);
}
