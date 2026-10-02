from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI

# Serve os arquivos da pasta assets/ em http://<nome-da-placa>.local:7000
web_ui = WebUI()

App.run()
