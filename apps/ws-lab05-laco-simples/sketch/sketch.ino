// sketch/sketch.ino — sensor, atuadores e uma versao agrupada do ciclo
#include <Arduino_RouterBridge.h>
#include <Servo.h>

Servo myServo;

int read_sensor_raw() {
    return analogRead(A0);                       // 0 a 1023
}

void set_servo(int angle) {
    myServo.write(constrain(angle, 0, 180));
}

void set_led(bool state) {
    digitalWrite(LED_BUILTIN, state ? LOW : HIGH); // LED_BUILTIN e ativo em LOW
}

// Ciclo completo em uma unica chamada: le, decide, atua e devolve a leitura
int sense_and_act(int threshold) {
    int raw = analogRead(A0);
    myServo.write(constrain(raw * 180 / 1024, 0, 180));   // multiplica antes: divisao inteira
    digitalWrite(LED_BUILTIN, raw > threshold ? LOW : HIGH);
    return raw;
}

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(A0, INPUT);
    myServo.attach(9);                           // servo em D9
    Bridge.begin();
    Bridge.provide("read_sensor_raw", read_sensor_raw);
    Bridge.provide("set_servo", set_servo);
    Bridge.provide("set_led", set_led);
    Bridge.provide("sense_and_act", sense_and_act);
}

void loop() {}
