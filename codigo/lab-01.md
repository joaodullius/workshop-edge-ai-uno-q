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

## Parte B: Uma figura na matriz de LED

**Passo 5** (terminal)

```bash
arduino-app-cli app new "minha-matriz" --from-app examples:core-and-foundational/02-led-matrix/02-led-matrix-frame
```

**Passo 6** (Python)

```python
from arduino.app_utils import App, Bridge, Frame
import numpy as np

# Cada numero e o brilho de um LED: 0 apagado, 7 brilho maximo (8 linhas x 13 colunas)
frame_array = np.array(
    [
        [7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 7],
        [0, 0, 7, 7, 0, 0, 0, 0, 0, 7, 7, 0, 0],
        [0, 0, 0, 0, 7, 7, 0, 7, 7, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 7, 7, 7, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 7, 7, 7, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 7, 7, 0, 7, 7, 0, 0, 0, 0],
        [0, 0, 7, 7, 0, 0, 0, 0, 0, 7, 7, 0, 0],
        [7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 7],
    ],
    dtype=np.uint8,
)

frame = Frame(frame_array)            # confere se a grade tem 8 linhas e 13 colunas
frame_bytes = frame.to_board_bytes()  # transforma a grade nos 104 bytes que o sketch recebe

Bridge.call("draw", frame_bytes)      # envia o desenho ao MCU

App.run()
```

**Passo 6** (sketch (C++))

```cpp
#include <Arduino_RouterBridge.h>
#include <Arduino_LED_Matrix.h>
#include <vector>

Arduino_LED_Matrix matrix;

const uint8_t FRAME_ROWS = 8;
const uint8_t FRAME_COLS = 13;
const uint8_t FRAME_SIZE = FRAME_ROWS * FRAME_COLS;

uint8_t frame[FRAME_SIZE] = {0};      // o desenho atual; comeca apagado

void setup() {
    matrix.begin();
    matrix.setGrayscaleBits(3);       // 3 bits de brilho: valores de 0 a 7
    matrix.clear();
    Bridge.begin();
    Bridge.provide("draw", draw);     // expoe a funcao "draw" para o Python
}

void loop() {
    matrix.draw(frame);               // mostra o desenho atual
    delay(10);
}

// Chamada pelo Python: copia o desenho recebido para a memoria do sketch
void draw(std::vector<uint8_t> newFrame) {
    size_t len = min(newFrame.size(), (size_t)FRAME_SIZE);
    memcpy(frame, newFrame.data(), len);
}
```

**Passo 7** (Python)

```python
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 7, 7, 0, 0, 0, 7, 7, 0, 0, 0],
        [0, 0, 7, 7, 7, 7, 0, 7, 7, 7, 7, 0, 0],
        [0, 0, 7, 7, 7, 7, 7, 7, 7, 7, 7, 0, 0],
        [0, 0, 0, 7, 7, 7, 7, 7, 7, 7, 0, 0, 0],
        [0, 0, 0, 0, 7, 7, 7, 7, 7, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 7, 7, 7, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0],
```

## Parte C: Entendendo a estrutura do app

**Passo 8** (YAML)

```yaml
name: Blink LED from Python
icon: 🔴
description: This example shows how to make the LED blink alternately from Python.
```

## Parte D: Usando a linha de comando

**Passo 10** (terminal)

```bash
arduino-app-cli app list                                                         # lista apps e exemplos
arduino-app-cli app start examples:core-and-foundational/01-led-blink/03-blinking-an-led-from-python
arduino-app-cli app logs  examples:core-and-foundational/01-led-blink/03-blinking-an-led-from-python --all   # traz tambem a saida de execucoes anteriores
arduino-app-cli app stop  examples:core-and-foundational/01-led-blink/03-blinking-an-led-from-python
```

**Passo 11** (terminal)

```bash
arduino-app-cli app new "my-first-app"
ls /home/arduino/ArduinoApps/my-first-app
```

## Parte E: Controlando o LED pelo Arduino Cloud

**Passo 14** (Python)

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
