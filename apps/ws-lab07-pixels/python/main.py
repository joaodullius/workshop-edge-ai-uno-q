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
