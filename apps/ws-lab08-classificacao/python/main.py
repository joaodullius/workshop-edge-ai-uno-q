from arduino.app_utils import App
from arduino.app_bricks.video_imageclassification import VideoImageClassification
import time

stream = VideoImageClassification(confidence=0.3, debounce_sec=0.0)
contagem = 0
inicio = None                      # o relogio comeca no primeiro resultado

def ao_classificar(resultados: dict):
    # resultados: {"rotulo": confianca, ...}, so os acima do limiar
    global contagem, inicio
    if inicio is None:
        inicio = time.time()
    contagem += 1
    if contagem <= 3:
        print("Resultado:", resultados)
    if contagem % 30 == 0:
        taxa = contagem / (time.time() - inicio)
        print(f"{taxa:.1f} resultados/s")

stream.on_detect_all(ao_classificar)
App.run()
