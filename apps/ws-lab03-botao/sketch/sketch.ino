// sketch/sketch.ino — lê o botão em D2 e reflete no LED
#include <Arduino_RouterBridge.h>

#define BUTTON_PIN D2

void setup() {
    Monitor.begin(115200);          // log do MCU; leia com arduino-app-cli monitor
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(BUTTON_PIN, INPUT);
    Bridge.begin();                 // obrigatório em todo sketch de app
    Monitor.println("Sketch do MCU iniciado");
}

void loop() {
    int pressed = digitalRead(BUTTON_PIN);
    // LED_BUILTIN acende com LOW no UNO Q
    digitalWrite(LED_BUILTIN, pressed ? LOW : HIGH);
    Monitor.println(pressed ? "Botao pressionado, LED ON" : "Botao solto, LED OFF");
    delay(100);                     // debounce simples
}
