// sketch/sketch.ino — funções expostas ao Python pela Bridge
#include <Arduino_RouterBridge.h>

float read_sensor() {
    return analogRead(A0) * 3.3 / 1024.0;    // tensão em A0, em volts
}

void set_led(bool state) {
    digitalWrite(LED_BUILTIN, state ? LOW : HIGH);   // LED_BUILTIN e ativo em LOW
}

int add_numbers(int a, int b) {
    return a + b;
}

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(A0, INPUT);
    Bridge.begin();                                   // inicializa a Bridge
    Bridge.provide("read_sensor", read_sensor);       // expoe cada funcao pelo nome
    Bridge.provide("set_led", set_led);
    Bridge.provide("add_numbers", add_numbers);
}

void loop() {
    // vazio: a Bridge atende as chamadas em segundo plano
}
