# Laboratório 8: O custo do modelo: tamanho, resolução e latência: código para copiar

Os blocos abaixo são os mesmos do manual, na mesma ordem. Copie daqui, e não do PDF: lá as linhas longas são quebradas.

## Parte A: Linha de base com o modelo padrão de detecção

**Passo 1** (YAML)

```yaml
bricks:
  - arduino:video_object_detection
  - arduino:web_ui
```

## Parte B: Trocando o modelo

**Passo 4** (YAML)

```yaml
bricks:
  - arduino:video_object_detection:
      model: face-detection
  - arduino:web_ui
```

**Passo 5** (YAML)

```yaml
name: model-cost-cls
icon: 🎥
description: "Custo do modelo, classificação"
bricks:
  - arduino:video_image_classification
```

**Passo 5** (Python)

```python
from arduino.app_utils import App
from arduino.app_bricks.video_imageclassification import VideoImageClassification
import time

stream = VideoImageClassification(confidence=0.3, debounce_sec=0.0)
contagem = 0
inicio = time.time()

def ao_classificar(resultados: dict):
    # resultados: {"rotulo": confianca, ...}, so os acima do limiar
    global contagem
    contagem += 1
    if contagem <= 3:
        print("Resultado:", resultados)
    if contagem % 30 == 0:
        taxa = contagem / (time.time() - inicio)
        print(f"{taxa:.1f} resultados/s")

stream.on_detect_all(ao_classificar)
App.run()
```

**Passo 6** (YAML)

```yaml
name: model-cost-cls
icon: 🎥
description: "Custo do modelo, classificação"
bricks:
  - arduino:video_image_classification:
      model: person-classification
```

## Parte C: Medindo pelo WebSocket

**Passo 7** (terminal)

```bash
nano ~/ArduinoApps/model-cost-cls/ws_probe.py
```

**Passo 7** (terminal)

```bash
cp ~/ArduinoApps/model-cost-cls/ws_probe.py ~/ArduinoApps/model-cost/
```

**Passo 7** (Python)

```python
# ws_probe.py: escuta o runner de modelos por 20 s e resume o tempo de inferencia
import asyncio, json, time, sys

URL = sys.argv[1] if len(sys.argv) > 1 else "ws://ei-video-obj-detection-runner:4912"

async def main():
    import websockets
    async with websockets.connect(URL, max_size=None) as ws:
        inicio = time.time()
        tempos = []
        n = 0
        while time.time() - inicio < 20:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=5)
            except asyncio.TimeoutError:
                print("nenhuma mensagem em 5 s (ha alguem na frente da camera?)")
                continue
            n += 1
            dado = json.loads(msg)
            if "timeMs" in dado:              # mensagens de resultado trazem o tempo de inferencia
                tempos.append(dado["timeMs"])
        duracao = time.time() - inicio
        print(f"{n} mensagens em {duracao:.1f} s = {n / duracao:.2f} resultados/s")
        if tempos:
            print(f"inferencia: media {sum(tempos) / len(tempos):.1f} ms, "
                  f"min {min(tempos)} ms, max {max(tempos)} ms (n={len(tempos)})")

asyncio.run(main())
```

**Passo 8** (terminal)

```bash
# app com video_object_detection
docker exec model-cost-main-1 python3 /app/ws_probe.py ws://ei-video-obj-detection-runner:4912

# app com video_image_classification
docker exec model-cost-cls-main-1 python3 /app/ws_probe.py ws://ei-video-classification-runner:4912
```

## Parte D: Compare e analise

**Passo 11** (Python)

```python
from arduino.app_peripherals.camera import Camera

camera = Camera(resolution=(640, 480), fps=30)
stream = VideoImageClassification(camera=camera, confidence=0.3, debounce_sec=0.0)
```
