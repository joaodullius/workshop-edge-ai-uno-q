#include <Arduino_RouterBridge.h>

void set_led_state(bool on) {
    digitalWrite(LED_BUILTIN, on ? LOW : HIGH);   // LED_BUILTIN acende em LOW
}

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);              // comeca apagado
    Bridge.begin();
    Bridge.provide("set_led_state", set_led_state);
}

void loop() {}
