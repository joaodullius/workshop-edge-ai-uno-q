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
