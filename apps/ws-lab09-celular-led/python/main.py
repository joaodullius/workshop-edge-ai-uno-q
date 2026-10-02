# python/main.py — deteccao ao vivo com contador de resultados (versao B, celular)
import secrets
import string
import time
from datetime import datetime, UTC

from arduino.app_utils import App, Bridge
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
