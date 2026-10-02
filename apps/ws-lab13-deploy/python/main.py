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
