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
