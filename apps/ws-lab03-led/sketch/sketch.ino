// sketch/sketch.ino — expõe set_led ao Python
#include <Arduino_RouterBridge.h>

void set_led(bool state) {
    digitalWrite(LED_BUILTIN, state ? LOW : HIGH);
}

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    Bridge.begin();
    Bridge.provide("set_led", set_led);   // agora o Python pode chamar "set_led"
}

void loop() {
    // pode ficar vazio: a Bridge atende as chamadas em segundo plano
}
