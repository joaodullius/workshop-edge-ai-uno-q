#include <Arduino_Modulino.h>
#include <Arduino_RouterBridge.h>

ModulinoThermo thermo;
ModulinoDistance distance;

unsigned long previousMillis = 0;
const long interval = 1000;  // uma leitura por segundo

void setup() {
    Bridge.begin();
    Modulino.begin(Wire1);   // no UNO Q os Modulinos ficam no Wire1
    thermo.begin();
    distance.begin();
}

void loop() {
    unsigned long now = millis();
    if (now - previousMillis >= interval) {
        previousMillis = now;
        float celsius  = thermo.getTemperature();
        float humidity = thermo.getHumidity();
        // get() devolve milimetros; convertemos para cm. Sem leitura valida, enviamos -1
        float cm       = distance.available() ? distance.get() / 10.0 : -1;
        // Envia as tres leituras ao Python de uma vez, sem esperar resposta
        Bridge.notify("record_samples", celsius, humidity, cm);
    }
}
