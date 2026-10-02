#include <Arduino_Modulino.h>
#include <Arduino_RouterBridge.h>

ModulinoThermo thermo;

unsigned long previousMillis = 0;
const long interval = 1000;          // uma leitura por segundo

void setup() {
  Bridge.begin();
  Modulino.begin(Wire1);             // barramento Qwiic do UNO Q
  thermo.begin();
}

void loop() {
  unsigned long now = millis();
  if (now - previousMillis >= interval) {
    previousMillis = now;
    float celsius  = thermo.getTemperature();
    float humidity = thermo.getHumidity();
    // Envia as duas leituras ao Python, sem esperar resposta
    Bridge.notify("record_sensor_samples", celsius, humidity);
  }
}
