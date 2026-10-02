# Laboratório 4: Comunicação entre processadores: código para copiar

Os blocos abaixo são os mesmos do manual, na mesma ordem. Copie daqui, e não do PDF: lá as linhas longas são quebradas.

## Parte A: Comunicação básica pela Bridge

**Passo 2** (sketch (C++))

```cpp
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
```

**Passo 3** (Python)

```python
# python/main.py — chama funcoes do sketch
from arduino.app_utils import App, Bridge
import time

# Passa parametros e recebe o retorno
print("7 + 3 =", Bridge.call("add_numbers", 7, 3))

# Le o sensor
voltage = Bridge.call("read_sensor")
print(f"Tensao no sensor: {voltage:.2f} V")

# Controla o LED
Bridge.call("set_led", True)
time.sleep(1)
Bridge.call("set_led", False)

App.run()
```

## Parte B: Medir a latência da Bridge

**Passo 5** (Python)

```python
import statistics

times = []
print("Medindo a latencia da Bridge (100 chamadas)...")
for _ in range(100):
    t0 = time.perf_counter()
    Bridge.call("read_sensor")
    times.append((time.perf_counter() - t0) * 1000)   # em ms

print(f"Media: {statistics.mean(times):.2f} ms")
print(f"Min:   {min(times):.2f} ms")
print(f"Max:   {max(times):.2f} ms")
print(f"Desvio padrao: {statistics.stdev(times):.2f} ms")
```

## Parte C: Laço de monitoramento de sensor

**Passo 7** (Python)

```python
# python/main.py — monitora A0 e acende o LED acima do limiar
from arduino.app_utils import App, Bridge
import time

THRESHOLD = 1.5   # volts

def loop():
    voltage = Bridge.call("read_sensor")
    if voltage > THRESHOLD:
        Bridge.call("set_led", True)
        print(f"ALERTA: {voltage:.2f} V acima do limiar")
    else:
        Bridge.call("set_led", False)
        print(f"Normal: {voltage:.2f} V")
    time.sleep(0.5)

App.run(user_loop=loop)
```

## Parte D: O caminho inverso, MCU avisando o Python

**Passo 9** (sketch (C++))

```cpp
unsigned long last = 0;

void loop() {
    if (millis() - last >= 1000) {
        last = millis();
        Bridge.notify("on_tick", (int)(millis() / 1000));   // avisa o Python, sem esperar
    }
}
```

**Passo 9** (Python)

```python
def on_tick(seconds: int):
    print(f"MCU ligado ha {seconds} s")

Bridge.provide("on_tick", on_tick)   # expoe a funcao ao sketch
```

## Parte E: Desafio, a foto que acende o LED

**Passo 11** (terminal)

```bash
cp -r /var/lib/arduino-app-cli/examples/core-and-foundational/01-led-blink/03-blinking-an-led-from-python/sketch ~/ArduinoApps/detect-foto/
ls ~/ArduinoApps/detect-foto/sketch
```

**Passo 12** (Python)

```python
        pessoa = any(d.get("class_name") == "person" for d in results.get("detection", []))
        Bridge.call("set_led_state", pessoa)
        print("Pessoa na foto:", pessoa, "-> LED", "aceso" if pessoa else "apagado")
```
