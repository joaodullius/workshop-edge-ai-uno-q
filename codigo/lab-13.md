# Laboratório 13: Implantando e medindo seu sistema: código para copiar

Os blocos abaixo são os mesmos do manual, na mesma ordem. Copie daqui, e não do PDF: lá as linhas longas são quebradas.

## Parte A: A aplicação completa

**Passo 3** (terminal)

```bash
cp -r /var/lib/arduino-app-cli/examples/core-and-foundational/01-led-blink/03-blinking-an-led-from-python/sketch ~/ArduinoApps/deploy-final/
```

**Passo 3** (sketch (C++))

```cpp
#include <Arduino_RouterBridge.h>

// LED_BUILTIN acende em LOW
void set_led_state(bool state) {
    digitalWrite(LED_BUILTIN, state ? LOW : HIGH);
}

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);              // comeca apagado
    Bridge.begin();
    Bridge.provide("set_led_state", set_led_state);
}

void loop() {}
```

**Passo 4** (Python)

```python
from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from datetime import datetime, UTC
import time

ui = WebUI()
detection_stream = VideoObjectDetection(confidence=0.5, debounce_sec=0.0)
ui.on_message("override_th", lambda sid, th: detection_stream.override_threshold(th))

frame_count = 0
start_time = time.time()
detections_log = []
led_on = False

def on_detections(detections: dict):
    global frame_count, led_on
    frame_count += 1
    timestamp = time.time() - start_time

    # Registra cada deteccao e envia para a pagina web
    for class_name, instances in detections.items():
        for det in instances:
            detections_log.append({"time": timestamp, "class": class_name,
                                   "confidence": det.get("confidence", 0)})
            ui.send_message("detection", message={"content": class_name,
                                                  "confidence": det.get("confidence"),
                                                  "timestamp": datetime.now(UTC).isoformat()})

    # Aciona o LED do MCU quando ha pessoa na cena
    person = "person" in detections
    if person != led_on:
        led_on = person
        Bridge.call("set_led_state", led_on)

    # Relatorio periodico
    if frame_count % 50 == 0:
        fps = frame_count / (time.time() - start_time)
        print(f"Quadros: {frame_count} | {fps:.1f} resultados/s | Deteccoes: {len(detections_log)}")

detection_stream.on_detect_all(on_detections)
App.run()
```

## Parte B: Monitoramento do sistema

**Passo 6** (terminal)

```bash
ssh arduino@<nome-da-placa>.local
```

**Passo 7** (terminal)

```bash
# Uso de CPU por processo. O runner do modelo aparece com o comeco do nome do modelo, como yolo-x-+
top -bn2 -d1 | grep -E "Cpu|python|gst|yolo|person|face|mobilenet" | tail -8

# Memoria
free -h

# Quais zonas termicas existem e qual e qual
for z in /sys/class/thermal/thermal_zone*; do echo "$(basename $z) $(cat $z/type) $(cat $z/temp)"; done
```

**Passo 7** (terminal)

```bash
# Temperatura da CPU, em graus, com uma casa decimal
awk '{printf "%.1f\n", $1/1000}' /sys/class/thermal/thermal_zone3/temp
```

## Parte C: Teste sustentado

**Passo 9** (terminal)

```bash
while true; do echo "$(date +%T) $(awk '{printf "%.1f", $1/1000}' /sys/class/thermal/thermal_zone3/temp) C"; sleep 60; done
```

## Parte D: Alternativa, monitoramento de dentro do app

**Trecho** (terminal)

```bash
echo "psutil" > ~/ArduinoApps/monitor-app/python/requirements.txt
```

**Trecho** (Python)

```python
from arduino.app_utils import App
import psutil, time

def monitor_loop():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    print(f"CPU {cpu:.0f}% | RAM {mem:.0f}%")
    time.sleep(4)

App.run(user_loop=monitor_loop)
```

## Parte E: Relatório de desempenho
