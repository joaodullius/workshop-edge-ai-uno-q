// sketch/sketch.ino — LED e matriz de LED comandados pelo Python
#include <Arduino_RouterBridge.h>
#include <Arduino_LED_Matrix.h>
#include <vector>

Arduino_LED_Matrix matrix;
uint8_t frame[104] = {0};                 // o desenho atual: 8 linhas x 13 colunas, brilho de 0 a 7

void set_led_state(bool state) {
    digitalWrite(LED_BUILTIN, state ? LOW : HIGH);   // LED_BUILTIN acende em LOW
}

// Chamada pelo Python: recebe os 104 valores do desenho
void draw(std::vector<uint8_t> newFrame) {
    size_t len = min(newFrame.size(), sizeof(frame));
    memcpy(frame, newFrame.data(), len);
}

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);      // comeca apagado
    matrix.begin();
    matrix.setGrayscaleBits(3);           // 3 bits de brilho: valores de 0 a 7
    matrix.clear();
    Bridge.begin();
    Bridge.provide("set_led_state", set_led_state);
    Bridge.provide("draw", draw);
}

void loop() {
    matrix.draw(frame);                   // mostra o desenho atual
    delay(10);
}
