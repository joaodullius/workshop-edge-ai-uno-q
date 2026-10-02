# Laboratório 6: Sensores Modulino e painel na nuvem: código para copiar

Os blocos abaixo são os mesmos do manual, na mesma ordem. Copie daqui, e não do PDF: lá as linhas longas são quebradas.

## Parte A: O primeiro sensor

**Passo 2** (YAML)

```yaml
profiles:
  default:
    platforms:
      - platform: arduino:zephyr
    libraries:
      - Arduino_Modulino (0.7.0)
      - dependency: ArduinoGraphics (1.1.4)
      - dependency: Arduino_HS300x (1.0.0)
      - dependency: Arduino_LPS22HB (1.0.2)
      - dependency: Arduino_LSM6DSOX (1.1.2)
      - dependency: Arduino_LTR381RGB (1.0.0)
      - dependency: STM32duino VL53L4CD (1.0.5)
      - dependency: STM32duino VL53L4ED (1.0.1)
default_profile: default
```

**Passo 2** (terminal)

```bash
cp /var/lib/arduino-app-cli/examples/inspirational/common/home-climate-monitoring-and-storage/sketch/sketch.yaml ~/ArduinoApps/modulino-test/sketch/
```

**Passo 3** (sketch (C++))

```cpp
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
```

**Passo 4** (Python)

```python
from arduino.app_utils import App, Bridge

def record_sensor_samples(celsius: float, humidity: float):
    # Chamado pelo sketch a cada segundo
    estado = "quente" if celsius > 28 else "ok"
    print(f"Temp: {celsius:.1f} C | Umidade: {humidity:.0f} % | {estado}")

Bridge.provide("record_sensor_samples", record_sensor_samples)

App.run()
```

**Passo 4** (sketch (C++))

```cpp
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
```

**Passo 4** (Python)

```python
from arduino.app_utils import App, Bridge

def record_distance(cm: float):
    print(f"Distancia: {cm:.1f} cm")

Bridge.provide("record_distance", record_distance)

App.run()
```

## Parte B: Leitura de dois sensores

**Passo 6** (terminal)

```bash
cp ~/ArduinoApps/modulino-test/sketch/sketch.yaml ~/ArduinoApps/sensor-dashboard/sketch/
```

**Passo 7** (sketch (C++))

```cpp
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
```

**Passo 8** (Python)

```python
from arduino.app_utils import App, Bridge

def record_samples(celsius: float, humidity: float, cm: float):
    print(f"Temp: {celsius:.1f} C | Umid: {humidity:.0f} % | Dist: {cm:.1f} cm")
    if celsius > 30:
        print(f"  ALERTA: temperatura {celsius:.1f} C acima de 30 C")
    if 0 <= cm < 10:
        print(f"  ALERTA: objeto a {cm:.1f} cm")

Bridge.provide("record_samples", record_samples)
App.run()
```

## Parte C: Agregação local

**Passo 10** (Python)

```python
from arduino.app_utils import App, Bridge
from collections import deque
import statistics

# Janela das ultimas 30 leituras (30 segundos a 1 Hz)
temp_window = deque(maxlen=30)
dist_window = deque(maxlen=30)
alert_count = 0
sample_count = 0

def record_samples(celsius: float, humidity: float, cm: float):
    global alert_count, sample_count
    sample_count += 1
    temp_window.append(celsius)
    if cm >= 0:                     # -1 e "sem leitura valida" e nao entra na media
        dist_window.append(cm)

    if celsius > 30:
        alert_count += 1

    # Resumo a cada 5 leituras
    if sample_count % 5 == 0:
        media_dist = f"{statistics.mean(dist_window):.1f} cm" if dist_window else "sem leitura"
        print(f"Media temp: {statistics.mean(temp_window):.1f} C | "
              f"Media dist: {media_dist} | Alertas: {alert_count}")

Bridge.provide("record_samples", record_samples)
App.run()
```

## Parte D: Envio para o Arduino Cloud

**Passo 14** (Python)

```python
from arduino.app_utils import App, Bridge
from arduino.app_bricks.arduino_cloud import ArduinoCloud
from collections import deque
import statistics

cloud = ArduinoCloud()   # a conexao e feita pelo servico da placa; sem credenciais aqui

# interval=30: o valor atual e publicado a cada 30 s
cloud.register("avg_temperature", value=0.0, interval=30)
cloud.register("avg_distance", value=0.0, interval=30)
# sem interval: publicado quando muda
cloud.register("alert_count", value=0)
cloud.register("status", value="OK")

temp_window = deque(maxlen=30)
dist_window = deque(maxlen=30)
alert_count = 0
sample_count = 0

def record_samples(celsius: float, humidity: float, cm: float):
    global alert_count, sample_count
    sample_count += 1
    temp_window.append(celsius)
    if cm >= 0:                     # -1 e "sem leitura valida" e nao entra na media
        dist_window.append(cm)

    if celsius > 30:
        alert_count += 1
        cloud.alert_count = alert_count
        cloud.status = f"ALERTA: {celsius:.1f} C"
    elif cloud.status != "OK":
        cloud.status = "OK"

    # As medias sao atualizadas a cada leitura; o Brick publica a cada 30 s
    if len(temp_window) >= 5:
        media_temp = round(statistics.mean(temp_window), 1)
        cloud.avg_temperature = media_temp
        if dist_window:
            cloud.avg_distance = round(statistics.mean(dist_window), 1)
        if sample_count % 10 == 0:
            print(f"Cloud: avg_temperature={media_temp} | alert_count={alert_count} | status={cloud.status}")

Bridge.provide("record_samples", record_samples)
App.run()
```

## Parte E: O painel
