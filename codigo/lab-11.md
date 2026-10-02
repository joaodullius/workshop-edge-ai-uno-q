# Laboratório 11: Treine o seu modelo: código para copiar

Os blocos abaixo são os mesmos do manual, na mesma ordem. Copie daqui, e não do PDF: lá as linhas longas são quebradas.

## Parte A: Criar o projeto no Edge Impulse

## Parte B: Coletar e rotular os dados

## Parte C: Projetar e treinar o modelo

## Parte D: Implantar no UNO Q

## Parte E: Escrever e rodar a aplicação de inferência

**Passo 16** (Python)

```python
# python/main.py — inferência em tempo real com o modelo treinado
from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from datetime import datetime, UTC

ui = WebUI()   # serve a página do exemplo em :7000; sem esta linha a página não abre

# confidence=0.5: só reporta detecções em que o modelo tem mais de 50% de certeza.
# Experimente 0.3 (mais detecções, mais alarmes falsos) ou 0.8 (menos, mais confiáveis).
# debounce_sec=0.0: entrega todos os resultados, sem intervalo mínimo entre dois iguais.
detection_stream = VideoObjectDetection(confidence=0.5, debounce_sec=0.0)

# O controle de confiança da página envia a mensagem "override_th"
ui.on_message("override_th", lambda sid, threshold: detection_stream.override_threshold(threshold))

def on_detections(detections: dict):
    # Formato: {"caneca": [{"confidence": 0.91, "bounding_box_xyxy": (x1, y1, x2, y2)}], ...}
    for label, instances in detections.items():
        for det in instances:
            print(f"{label}: {round(det['confidence'] * 100)} %  caixa={det['bounding_box_xyxy']}")
            ui.send_message("detection", message={
                "content": label,
                "confidence": det.get("confidence"),
                "timestamp": datetime.now(UTC).isoformat(),
            })

detection_stream.on_detect_all(on_detections)

App.run()
```
