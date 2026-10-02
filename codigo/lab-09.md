# Laboratório 9: Aplicação de visão em tempo real: código para copiar

Os blocos abaixo são os mesmos do manual, na mesma ordem. Copie daqui, e não do PDF: lá as linhas longas são quebradas.

## Parte A: Partindo do exemplo oficial

**Passo 2** (YAML)

```yaml
bricks:
  - arduino:video_object_detection
  - arduino:web_ui
```

**Passo 2** (Python)

```python
from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from datetime import datetime, UTC

ui = WebUI()
detection_stream = VideoObjectDetection(confidence=0.5, debounce_sec=0.0)

# O controle deslizante da pagina envia "override_th"; repassamos ao Brick
ui.on_message("override_th", lambda sid, threshold: detection_stream.override_threshold(threshold))

def send_detections_to_ui(detections: dict):
    # detections: {"person": [{"confidence": 0.94, "bounding_box_xyxy": (x1, y1, x2, y2)}], ...}
    for label, instances in detections.items():
        for det in instances:
            ui.send_message("detection", message={
                "content": label,
                "confidence": det.get("confidence"),
                "timestamp": datetime.now(UTC).isoformat(),
            })

detection_stream.on_detect_all(send_detections_to_ui)

App.run()
```

**Passo 2** (Python)

```python
camera = WebSocketCamera(secret=secret, encrypt=True, resolution=resolution)
detection = VideoObjectDetection(camera, confidence=0.5, debounce_sec=0.0)
```

## Parte B: Medindo o desempenho de ponta a ponta

**Passo 4** (Python)

```python
# python/main.py — deteccao ao vivo com contador de resultados (versao A, webcam)
from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from datetime import datetime, UTC
import time

ui = WebUI()
detection_stream = VideoObjectDetection(confidence=0.5, debounce_sec=0.0)

ui.on_message("override_th", lambda sid, threshold: detection_stream.override_threshold(threshold))

contagem = 0
inicio = None                                      # o relogio comeca no primeiro resultado

def send_detections_to_ui(detections: dict):
    global contagem, inicio
    if inicio is None:
        inicio = time.time()
    contagem += 1

    for label, instances in detections.items():
        for det in instances:
            ui.send_message("detection", message={
                "content": label,
                "confidence": det.get("confidence"),
                "timestamp": datetime.now(UTC).isoformat(),
            })

    if contagem % 30 == 0:
        decorrido = time.time() - inicio
        print(f"Desempenho: {contagem / decorrido:.1f} resultados/s "
              f"({1000 * decorrido / contagem:.0f} ms por resultado) | total {contagem}")

detection_stream.on_detect_all(send_detections_to_ui)

App.run()
```

**Passo 4** (Python)

```python
# python/main.py — deteccao ao vivo com contador de resultados (versao B, celular)
import secrets
import string
import time
from datetime import datetime, UTC

from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from arduino.app_peripherals.camera import WebSocketCamera

# Senha de seis digitos do pareamento; ela vai dentro do codigo QR
secret = ''.join(secrets.choice(string.digits) for _ in range(6))

ui = WebUI()
camera = WebSocketCamera(secret=secret, encrypt=True, resolution=(480, 640))   # video em pe, como o celular
camera.on_status_changed(lambda evt_type, data: ui.send_message(evt_type, data))

detection_stream = VideoObjectDetection(camera, confidence=0.5, debounce_sec=0.0)

# Quando o navegador abre a pagina, ela recebe os dados para desenhar o codigo QR
ui.on_connect(lambda sid: ui.send_message("welcome", {
    "client_name": camera.name, "secret": secret, "status": camera.status,
    "protocol": camera.protocol, "ip": camera.ip, "port": camera.port}))
ui.on_message("override_th", lambda sid, threshold: detection_stream.override_threshold(threshold))

contagem = 0
inicio = None                                      # o relogio comeca no primeiro resultado

def send_detections_to_ui(detections: dict):
    global contagem, inicio
    if inicio is None:
        inicio = time.time()
    contagem += 1

    for label, instances in detections.items():
        for det in instances:
            ui.send_message("detection", {
                "content": label,
                "confidence": det.get("confidence"),
                "timestamp": datetime.now(UTC).isoformat(),
            })

    if contagem % 30 == 0:
        decorrido = time.time() - inicio
        print(f"Desempenho: {contagem / decorrido:.1f} resultados/s "
              f"({1000 * decorrido / contagem:.0f} ms por resultado) | total {contagem}")

detection_stream.on_detect_all(send_detections_to_ui)

App.run()
```

## Parte C: Fechando o ciclo com o MCU

**Passo 6** (terminal)

```bash
cp -r /var/lib/arduino-app-cli/examples/core-and-foundational/01-led-blink/03-blinking-an-led-from-python/sketch ~/ArduinoApps/vision-app/
ls ~/ArduinoApps/vision-app/sketch
```

**Passo 6** (sketch (C++))

```cpp
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
```

**Passo 7** (Python)

```python
# python/main.py — deteccao ao vivo, contador, LED e matriz (versao A, webcam)
from arduino.app_utils import App, Bridge, Frame
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from datetime import datetime, UTC
import time

ui = WebUI()
detection_stream = VideoObjectDetection(confidence=0.5, debounce_sec=0.0)

ui.on_message("override_th", lambda sid, threshold: detection_stream.override_threshold(threshold))

# Desenho para a matriz de LED: 8 linhas x 13 colunas, brilho de 0 (apagado) a 7
PESSOA = Frame.from_rows([
    [0, 0, 0, 0, 0, 7, 7, 7, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 7, 7, 7, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 7, 7, 7, 7, 7, 7, 7, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 7, 0, 0, 0, 7, 0, 0, 0, 0],
]).to_board_bytes()
APAGADA = bytes(104)                               # 104 zeros: matriz apagada

contagem = 0
inicio = None                                      # o relogio comeca no primeiro resultado

def send_detections_to_ui(detections: dict):
    global contagem, inicio
    if inicio is None:
        inicio = time.time()
    contagem += 1

    pessoa = "person" in detections
    Bridge.call("set_led_state", pessoa)           # AGIR: LED acende com pessoa na cena
    Bridge.call("draw", PESSOA if pessoa else APAGADA)   # e a matriz mostra o boneco
    if pessoa:
        print("PESSOA DETECTADA - LED ligado")

    for label, instances in detections.items():
        for det in instances:
            ui.send_message("detection", message={
                "content": label,
                "confidence": det.get("confidence"),
                "timestamp": datetime.now(UTC).isoformat(),
            })

    if contagem % 30 == 0:
        decorrido = time.time() - inicio
        print(f"Desempenho: {contagem / decorrido:.1f} resultados/s "
              f"({1000 * decorrido / contagem:.0f} ms por resultado) | total {contagem}")

detection_stream.on_detect_all(send_detections_to_ui)

App.run()
```

## Parte D: Trocando para o modelo leve (versão A)

**Passo 8** (YAML)

```yaml
bricks:
  - arduino:video_image_classification:
      model: person-classification
  - arduino:web_ui
```

**Passo 8** (terminal)

```bash
cp -r ~/ArduinoApps/vision-app/sketch ~/ArduinoApps/vision-app-fast/
```

**Passo 8** (Python)

```python
# python/main.py — classificador de pessoa, contador, LED e matriz
from arduino.app_utils import App, Bridge, Frame
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_imageclassification import VideoImageClassification
from datetime import datetime, UTC
import json
import time

ui = WebUI()
detection_stream = VideoImageClassification(confidence=0.5, debounce_sec=0.0)

ui.on_message("override_th", lambda sid, threshold: detection_stream.override_threshold(threshold))

# Desenho para a matriz de LED: 8 linhas x 13 colunas, brilho de 0 (apagado) a 7
PESSOA = Frame.from_rows([
    [0, 0, 0, 0, 0, 7, 7, 7, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 7, 7, 7, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 7, 7, 7, 7, 7, 7, 7, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 7, 0, 0, 0, 7, 0, 0, 0, 0],
]).to_board_bytes()
APAGADA = bytes(104)                               # 104 zeros: matriz apagada

contagem = 0
inicio = None                                      # o relogio comeca no primeiro resultado

def send_detections_to_ui(classifications: dict):
    # classifications: {"person": 0.90} ou {"non person": 0.97}
    global contagem, inicio
    if inicio is None:
        inicio = time.time()
    contagem += 1

    pessoa = "person" in classifications
    Bridge.call("set_led_state", pessoa)
    Bridge.call("draw", PESSOA if pessoa else APAGADA)

    entradas = [{"content": label, "confidence": confidence,
                 "timestamp": datetime.now(UTC).isoformat()}
                for label, confidence in classifications.items()]
    ui.send_message("classifications", message=json.dumps(entradas))

    if contagem % 30 == 0:
        decorrido = time.time() - inicio
        print(f"Desempenho: {contagem / decorrido:.1f} resultados/s | total {contagem}")

detection_stream.on_detect_all(send_detections_to_ui)

App.run()
```
