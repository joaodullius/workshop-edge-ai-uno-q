# Laboratório 1: Seu primeiro app e os fundamentos do App Lab: código para copiar

Os blocos abaixo são os mesmos do manual, na mesma ordem. Copie daqui, e não do PDF: lá as linhas longas são quebradas.

## Parte A: Rodando o exemplo Blink

**Passo 3** (Python)

```python
from arduino.app_utils import *
import time

led_state = False

# Esta funcao e chamada repetidamente pelo App.run()
def loop():
    global led_state
    time.sleep(1)
    led_state = not led_state
    # Chama a funcao "set_led_state" definida no sketch, passando True ou False
    Bridge.call("set_led_state", led_state)

App.run(user_loop=loop)
```

**Passo 3** (sketch (C++))

```cpp
#include "Arduino_RouterBridge.h"

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    Bridge.begin();                                  // obrigatorio para usar a Bridge
    Bridge.provide("set_led_state", set_led_state);  // expoe a funcao para o Python
}

void loop() {
}

void set_led_state(bool state) {
    digitalWrite(LED_BUILTIN, state ? LOW : HIGH);   // LED_BUILTIN acende em LOW
}
```

## Parte B: Entendendo a estrutura do app

**Passo 5** (YAML)

```yaml
name: Blink LED from Python
icon: 🔴
description: This example shows how to make the LED blink alternately from Python.
```

## Parte C: Usando a linha de comando

**Passo 7** (terminal)

```bash
arduino-app-cli app list                                                         # lista apps e exemplos
arduino-app-cli app start examples:core-and-foundational/01-led-blink/03-blinking-an-led-from-python
arduino-app-cli app logs  examples:core-and-foundational/01-led-blink/03-blinking-an-led-from-python --all   # traz tambem a saida de execucoes anteriores
arduino-app-cli app stop  examples:core-and-foundational/01-led-blink/03-blinking-an-led-from-python
```

**Passo 8** (terminal)

```bash
arduino-app-cli app new "my-first-app"
ls /home/arduino/ArduinoApps/my-first-app
```

## Parte D: Controlando o LED pelo Arduino Cloud

**Trecho** (Python)

```python
from arduino.app_bricks.arduino_cloud import ArduinoCloud
from arduino.app_utils import App, Bridge

# A conexao com o Cloud e feita pelo servico da placa; nenhuma credencial aqui
iot_cloud = ArduinoCloud()

def led_callback(client: object, value: bool):
    # Chamado sempre que a variavel "led" muda na nuvem
    print(f"LED blink value updated from cloud: {value}")
    Bridge.call("set_led_state", value)   # repassa ao sketch, que controla o pino

iot_cloud.register("led", value=False, on_write=led_callback)

App.run()
```
