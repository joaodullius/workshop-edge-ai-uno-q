from arduino.app_utils import App, Bridge
from collections import deque
import statistics

# Janela das ultimas 30 leituras (30 segundos a 1 Hz)
temp_window = deque(maxlen=30)
dist_window = deque(maxlen=30)
alert_count = 0
sample_count = 0

def record_samples(celsius: float, humidity: float, cm: float):
    global alert_count, sample_count
    sample_count += 1
    temp_window.append(celsius)
    if cm >= 0:                     # -1 e "sem leitura valida" e nao entra na media
        dist_window.append(cm)

    if celsius > 30:
        alert_count += 1

    # Resumo a cada 5 leituras
    if sample_count % 5 == 0:
        media_dist = f"{statistics.mean(dist_window):.1f} cm" if dist_window else "sem leitura"
        print(f"Media temp: {statistics.mean(temp_window):.1f} C | "
              f"Media dist: {media_dist} | Alertas: {alert_count}")

Bridge.provide("record_samples", record_samples)
App.run()
