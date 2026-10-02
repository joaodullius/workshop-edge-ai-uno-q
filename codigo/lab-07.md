# Laboratório 7: Noções básicas de câmera e captura de imagem: código para copiar

Os blocos abaixo são os mesmos do manual, na mesma ordem. Copie daqui, e não do PDF: lá as linhas longas são quebradas.

## Parte A: Montando a placa com a webcam

## Parte B: Verificando a câmera

**Passo 4** (terminal)

```bash
ssh arduino@<nome-da-placa>.local
```

**Passo 5** (terminal)

```bash
v4l2-ctl --list-devices
```

**Passo 6** (terminal)

```bash
v4l2-ctl --list-formats-ext -d /dev/video0
```

## Parte C: Capturando imagens com o periférico Camera

**Passo 8** (Python)

```python
from arduino.app_utils import App
from arduino.app_peripherals.camera import Camera
from arduino.app_utils.image import compress_to_jpeg

# A primeira camera encontrada (USB antes de CSI) e usada. Sem camera, levanta excecao.
camera = Camera(resolution=(640, 480), fps=30)
camera.start()

frame = camera.capture()            # numpy array (altura, largura, canais), ordem BGR
print("Formato:", frame.shape)      # (480, 640, 3)
print("Tipo:", frame.dtype)         # uint8
print(f"Tamanho em memoria: {frame.nbytes} bytes ({frame.nbytes/1024:.0f} KB)")

jpeg = compress_to_jpeg(frame=frame, quality=90)
with open("/app/captured_image.jpg", "wb") as f:   # /app e a pasta do app na placa
    f.write(jpeg.tobytes())
print(f"JPEG salvo: {jpeg.nbytes} bytes")

camera.stop()
App.run()   # mantem o app aberto ate voce clicar em Stop
```

**Passo 9** (terminal)

```bash
scp arduino@<nome-da-placa>.local:/home/arduino/ArduinoApps/camera-test/captured_image.jpg .
```

**Passo 10** (Python)

```python
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
```

## Parte D: Entendendo os dados da imagem

**Passo 11** (Python)

```python
from arduino.app_utils import App
from arduino.app_peripherals.camera import Camera
import cv2

camera = Camera(resolution=(640, 480), fps=30)
camera.start()
frame = camera.capture()
camera.stop()

altura, largura = frame.shape[:2]
pixel = frame[altura // 2, largura // 2]        # pixel central
print("Pixel central (BGR):", pixel)
print(f"  Azul: {pixel[0]}  Verde: {pixel[1]}  Vermelho: {pixel[2]}")

cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # 3 canais -> 1 canal
print(f"Colorida: {frame.shape} ({frame.nbytes} bytes)")
print(f"Cinza:    {cinza.shape} ({cinza.nbytes} bytes)")
print(f"Economia: {(1 - cinza.nbytes / frame.nbytes) * 100:.0f}%")
App.run()
```
