# python/main.py — classificador de pessoa, contador e LED
from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_imageclassification import VideoImageClassification
from datetime import datetime, UTC
import json
import time

ui = WebUI()
detection_stream = VideoImageClassification(confidence=0.5, debounce_sec=0.0)

ui.on_message("override_th", lambda sid, threshold: detection_stream.override_threshold(threshold))

contagem = 0
inicio = time.time()

def send_detections_to_ui(classifications: dict):
    # classifications: {"person": 0.90} ou {"non person": 0.97}
    global contagem
    contagem += 1

    pessoa = "person" in classifications
    Bridge.call("set_led_state", pessoa)

    entradas = [{"content": label, "confidence": confidence,
                 "timestamp": datetime.now(UTC).isoformat()}
                for label, confidence in classifications.items()]
    ui.send_message("classifications", message=json.dumps(entradas))

    if contagem % 30 == 0:
        decorrido = time.time() - inicio
        print(f"Desempenho: {contagem / decorrido:.1f} resultados/s | total {contagem}")

detection_stream.on_detect_all(send_detections_to_ui)

App.run()
