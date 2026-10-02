#include <Arduino_RouterBridge.h>

// LED_BUILTIN acende em LOW
void set_led_state(bool state) {
    digitalWrite(LED_BUILTIN, state ? LOW : HIGH);
}

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);              // comeca apagado
    Bridge.begin();
    Bridge.provide("set_led_state", set_led_state);
}

void loop() {}
