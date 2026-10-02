from arduino.app_utils import App, Bridge
from arduino.app_bricks.arduino_cloud import ArduinoCloud
from collections import deque
import statistics

cloud = ArduinoCloud()   # a conexao e feita pelo servico da placa; sem credenciais aqui

# interval=30: o valor atual e publicado a cada 30 s
cloud.register("avg_temperature", value=0.0, interval=30)
cloud.register("avg_distance", value=0.0, interval=30)
# sem interval: publicado quando muda
cloud.register("alert_count", value=0)
cloud.register("status", value="OK")

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
        cloud.alert_count = alert_count
        cloud.status = f"ALERTA: {celsius:.1f} C"
    elif cloud.status != "OK":
        cloud.status = "OK"

    # As medias sao atualizadas a cada leitura; o Brick publica a cada 30 s
    if len(temp_window) >= 5:
        media_temp = round(statistics.mean(temp_window), 1)
        cloud.avg_temperature = media_temp
        if dist_window:
            cloud.avg_distance = round(statistics.mean(dist_window), 1)
        if sample_count % 10 == 0:
            print(f"Cloud: avg_temperature={media_temp} | alert_count={alert_count} | status={cloud.status}")

Bridge.provide("record_samples", record_samples)
App.run()
