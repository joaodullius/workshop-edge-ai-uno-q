from arduino.app_utils import App
from arduino.app_peripherals.camera import Camera
import time, statistics

def medir(fps_pedido, n=100):
    cam = Camera(resolution=(640, 480), fps=fps_pedido)
    cam.start()
    frame = cam.capture()               # descarta o primeiro quadro (aquecimento)
    tempos = []
    for _ in range(n):
        t0 = time.perf_counter()
        frame = cam.capture()           # bloqueia ate o proximo quadro, respeitando o fps
        tempos.append((time.perf_counter() - t0) * 1000)
    cam.stop()
    media = statistics.mean(tempos)
    fps_real = 1000 / media
    taxa_mb = frame.nbytes * fps_real / 1024 / 1024
    print(f"fps pedido {fps_pedido}: media {media:.1f} ms, {fps_real:.1f} FPS, "
          f"min {min(tempos):.1f}, max {max(tempos):.1f}, {taxa_mb:.1f} MB/s")

medir(30)
medir(60)
medir(10)
App.run()
