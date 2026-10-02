# Laboratório 2: Bricks do App Lab e IA em uma foto: código para copiar

Os blocos abaixo são os mesmos do manual, na mesma ordem. Copie daqui, e não do PDF: lá as linhas longas são quebradas.

## Parte A: Adicionando e usando um Brick

**Passo 2** (YAML)

```yaml
bricks:
  - arduino:web_ui
```

**Passo 3** (Python)

```python
from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI

# Serve os arquivos da pasta assets/ em http://<nome-da-placa>.local:7000
web_ui = WebUI()

App.run()
```

**Passo 4** (HTML)

```html
<!DOCTYPE html>
<html>
<head><title>My First Brick App</title></head>
<body>
<h1>Hello from UNO Q!</h1>
<p>This web page is served directly from your Arduino board.</p>
<p>Hora no seu navegador: <span id="time"></span></p>
<script>
setInterval(() => {
  document.getElementById('time').textContent = new Date().toLocaleTimeString();
}, 1000);
</script>
</body>
</html>
```

## Parte B: Explorando a API de um Brick

**Passo 6** (Python)

```python
from arduino.app_bricks.object_detection import ObjectDetection

detector = ObjectDetection()            # limiar de confianca padrao: 0.3

with open("assets/image.jpg", "rb") as f:
    img = f.read()

out = detector.detect(img)              # aceita bytes JPEG/PNG ou uma imagem PIL
# out = {"detection": [{"class_name": "person", "confidence": "87.30",
#                       "bounding_box_xyxy": [x1, y1, x2, y2]}, ...]}
for det in out.get("detection", []):
    print(det["class_name"], det["confidence"], det["bounding_box_xyxy"])
```

## Parte C: IA em uma foto

**Passo 10** (Python)

```python
        n_obj = len(results.get("detection", [])) if results else 0
        print(f"Deteccao: {n_obj} objetos em {diff:.0f} ms")
```

## Parte D: Bricks e containers Docker
