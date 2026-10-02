# python/main.py — deteccao ao vivo, contador e LED (versao A, webcam)
from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from datetime import datetime, UTC
import time

ui = WebUI()
detection_stream = VideoObjectDetection(confidence=0.5, debounce_sec=0.0)

ui.on_message("override_th", lambda sid, threshold: detection_stream.override_threshold(threshold))

contagem = 0
inicio = time.time()

def send_detections_to_ui(detections: dict):
    global contagem
    contagem += 1

    pessoa = "person" in detections
    Bridge.call("set_led_state", pessoa)           # AGIR: LED acende com pessoa na cena
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
