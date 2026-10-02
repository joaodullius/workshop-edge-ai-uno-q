# Laboratório 3: Os dois mundos, Linux e o MCU: código para copiar

Os blocos abaixo são os mesmos do manual, na mesma ordem. Copie daqui, e não do PDF: lá as linhas longas são quebradas.

## Parte A: Explorar o lado Linux

**Passo 2** (terminal)

```bash
uname -a                      # kernel 6.16, arquitetura aarch64
cat /etc/os-release           # Debian 13 (trixie)
nproc                         # 4 núcleos
free -h                       # 3,6 GiB de RAM e 1,8 GiB de swap
ls /home/arduino/ArduinoApps/ # seus apps
ls /var/lib/arduino-app-cli/examples/   # exemplos do App Lab
ps aux | grep -E "python|docker" | head  # processos dos apps e do Docker
```

**Passo 3** (terminal)

```bash
python3 --version                 # Python do host
pip list 2>/dev/null | grep -i arduino   # não imprime nada: o host nem tem o pip
docker images                     # python-apps-base e ei-models-runner
```

## Parte B: Editar o sketch no App Lab

**Passo 5** (sketch (C++))

```cpp
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
```

**Passo 6** (Python)

```python
from arduino.app_utils import App
App.run()
```

**Passo 7** (terminal)

```bash
arduino-app-cli monitor
```

## Parte C: Entender a Bridge

**Trecho** (sketch (C++))

```cpp
// sketch/sketch.ino — expõe set_led ao Python
#include <Arduino_RouterBridge.h>

void set_led(bool state) {
    digitalWrite(LED_BUILTIN, state ? LOW : HIGH);
}

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    Bridge.begin();
    Bridge.provide("set_led", set_led);   // agora o Python pode chamar "set_led"
}

void loop() {
    // pode ficar vazio: a Bridge atende as chamadas em segundo plano
}
```

**Trecho** (Python)

```python
from arduino.app_utils import App, Bridge

Bridge.call("set_led", True)   # executa set_led(true) no MCU e espera a resposta
```

## Parte D: Controlar o LED do MCU a partir do Python

**Passo 9** (Python)

```python
# python/main.py — pisca o LED do MCU a partir do Python
from arduino.app_utils import App, Bridge
import time

state = False

def loop():
    global state
    state = not state
    Bridge.call("set_led", state)
    print("LED do MCU:", "ON" if state else "OFF")
    time.sleep(1)

App.run(user_loop=loop)   # o App Lab chama loop() repetidamente
```
