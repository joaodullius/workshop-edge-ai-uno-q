# Laboratório 14: Construindo um agente de borda: código para copiar

Os blocos abaixo são os mesmos do manual, na mesma ordem. Copie daqui, e não do PDF: lá as linhas longas são quebradas.

## Parte A: Da inferência ao rastreamento com estado

**Passo 1** (YAML)

```yaml
bricks:
  - arduino:video_image_classification:
      model: person-classification
```

**Passo 2** (sketch (C++))

```cpp
// sketch/sketch.ino — LED e matriz de LED comandados pelo Python
#include <Arduino_RouterBridge.h>
#include <Arduino_LED_Matrix.h>
#include <vector>

Arduino_LED_Matrix matrix;
uint8_t frame[104] = {0};                 // o desenho atual: 8 linhas x 13 colunas, brilho de 0 a 7

void set_led_state(bool state) {
    digitalWrite(LED_BUILTIN, state ? LOW : HIGH);   // LED_BUILTIN acende em LOW
}

// Chamada pelo Python: recebe os 104 valores do desenho
void draw(std::vector<uint8_t> newFrame) {
    size_t len = min(newFrame.size(), sizeof(frame));
    memcpy(frame, newFrame.data(), len);
}

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);      // comeca apagado
    matrix.begin();
    matrix.setGrayscaleBits(3);           // 3 bits de brilho: valores de 0 a 7
    matrix.clear();
    Bridge.begin();
    Bridge.provide("set_led_state", set_led_state);
    Bridge.provide("draw", draw);
}

void loop() {
    matrix.draw(frame);                   // mostra o desenho atual
    delay(10);
}
```

**Passo 3** (Python)

```python
from arduino.app_utils import App, Bridge, Frame
from arduino.app_bricks.video_imageclassification import VideoImageClassification
import time

stream = VideoImageClassification(confidence=0.3, debounce_sec=0.0)

# O que a matriz de LED mostra em cada estado do agente (8 linhas x 13 colunas, brilho de 0 a 7)
ICONES = {
    "IDLE": Frame.from_rows([        # dois olhos: vigiando
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 7, 7, 7, 0, 0, 0, 0, 0, 7, 7, 7, 0],
        [7, 0, 0, 0, 7, 0, 0, 0, 7, 0, 0, 0, 7],
        [7, 0, 7, 0, 7, 0, 0, 0, 7, 0, 7, 0, 7],
        [7, 0, 7, 0, 7, 0, 0, 0, 7, 0, 7, 0, 7],
        [7, 0, 0, 0, 7, 0, 0, 0, 7, 0, 0, 0, 7],
        [0, 7, 7, 7, 0, 0, 0, 0, 0, 7, 7, 7, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]).to_board_bytes(),
    "ALERT": Frame.from_rows([       # triangulo de aviso: alerta
        [0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 7, 0, 0, 0, 7, 0, 0, 0, 0],
        [0, 0, 0, 7, 0, 0, 7, 0, 0, 7, 0, 0, 0],
        [0, 0, 7, 0, 0, 0, 7, 0, 0, 0, 7, 0, 0],
        [0, 7, 0, 0, 0, 0, 7, 0, 0, 0, 0, 7, 0],
        [7, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 7],
        [7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7],
    ]).to_board_bytes(),
    "COOLDOWN": Frame.from_rows([    # pausa: espera entre alertas
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 7, 7, 7, 0, 0, 0, 7, 7, 7, 0, 0],
        [0, 0, 7, 7, 7, 0, 0, 0, 7, 7, 7, 0, 0],
        [0, 0, 7, 7, 7, 0, 0, 0, 7, 7, 7, 0, 0],
        [0, 0, 7, 7, 7, 0, 0, 0, 7, 7, 7, 0, 0],
        [0, 0, 7, 7, 7, 0, 0, 0, 7, 7, 7, 0, 0],
        [0, 0, 7, 7, 7, 0, 0, 0, 7, 7, 7, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]).to_board_bytes(),
}

class DetectionTracker:
    """Memoria e regras de decisao do agente."""

    CONFIDENCE_THRESHOLD = 0.6   # confianca minima para contar como pessoa
    SUSTAIN_SECONDS = 2.0        # presenca continua necessaria para alertar
    CLEAR_SECONDS = 2.0          # ausencia necessaria para encerrar o alerta
    COOLDOWN_SECONDS = 5.0       # espera minima entre dois alertas
    HISTORY_SECONDS = 10.0       # quanto tempo de historico e mantido

    def __init__(self):
        self.history = []            # lista de (timestamp, pessoa_presente: bool)
        self.state = "IDLE"          # IDLE, ALERT ou COOLDOWN
        self.presence_start = None   # quando a presenca atual comecou
        self.last_seen = 0.0         # ultima vez que uma pessoa foi vista
        self.alert_start = None
        self.cooldown_start = 0.0
        self.total_alerts = 0

    def update(self, results: dict) -> str:
        now = time.time()
        present = results.get("person", 0.0) >= self.CONFIDENCE_THRESHOLD

        # Memoria: guarda a observacao e descarta o que ficou velho
        self.history.append((now, present))
        self.history = [(t, p) for t, p in self.history if now - t < self.HISTORY_SECONDS]

        if present:
            # Uma presenca nova comeca depois de uma ausencia de CLEAR_SECONDS
            if self.presence_start is None or now - self.last_seen > self.CLEAR_SECONDS:
                self.presence_start = now
            self.last_seen = now

        return self._evaluate(now)

    def _ratio(self, now, seconds):
        """Fracao de observacoes recentes com pessoa presente."""
        recent = [p for t, p in self.history if now - t < seconds]
        return (sum(recent) / len(recent)) if recent else 0.0

    def _evaluate(self, now):
        absent_for = now - self.last_seen

        if self.state == "IDLE":
            # Dispara so quando a presenca ja dura SUSTAIN_SECONDS
            # e a pessoa aparece em mais de 60 % das observacoes desse periodo
            sustained = (self.presence_start is not None
                         and absent_for <= self.CLEAR_SECONDS
                         and now - self.presence_start >= self.SUSTAIN_SECONDS
                         and self._ratio(now, self.SUSTAIN_SECONDS) > 0.6)
            if sustained:
                self.state = "ALERT"
                self.alert_start = now
                self.total_alerts += 1
                return "ALERT_NEW"
            return "MONITORING"

        if self.state == "ALERT":
            # Encerra quando ninguem e visto ha CLEAR_SECONDS
            if absent_for >= self.CLEAR_SECONDS:
                duration = now - self.alert_start
                self.state = "COOLDOWN"
                self.cooldown_start = now
                return f"ALERT_CLEARED ({duration:.1f}s)"
            return "ALERT_ACTIVE"

        if self.state == "COOLDOWN":
            # A espera conta a partir do fim do alerta
            if now - self.cooldown_start > self.COOLDOWN_SECONDS:
                self.state = "IDLE"
            return "COOLDOWN"

        return "MONITORING"
```

## Parte B: Conectando o agente às ações

**Passo 4** (Python)

```python
tracker = DetectionTracker()
led_on = False
events = 0

def set_led(state: bool):
    global led_on
    if state != led_on:
        led_on = state
        Bridge.call("set_led_state", state)

estado_na_matriz = None

def mostra_estado():
    """Desenha na matriz o icone do estado do agente, so quando o estado muda."""
    global estado_na_matriz
    if tracker.state != estado_na_matriz:
        estado_na_matriz = tracker.state
        Bridge.call("draw", ICONES[tracker.state])

def on_results(results: dict):
    global events
    events += 1
    status = tracker.update(results)

    if status == "ALERT_NEW":
        set_led(True)
        print(f">>> ALERTA #{tracker.total_alerts}: presenca sustentada")
    elif status.startswith("ALERT_CLEARED"):
        set_led(False)
        print(f"<<< Alerta encerrado. {status}")
    elif status == "ALERT_ACTIVE":
        pass                      # LED continua aceso
    else:
        set_led(False)            # padrao seguro: LED apagado

    mostra_estado()               # a matriz acompanha o estado do agente

    if events % 50 == 0:
        print(f"Agente em {tracker.state} | {tracker.total_alerts} alertas ate agora | "
              f"memoria: {len(tracker.history)} resultados")

stream.on_detect_all(on_results)
App.run()
```

## Parte C: Analisando o comportamento

**Passo 6** (Python)

```python
    if status == "ALERT_NEW" or status.startswith("ALERT_CLEARED"):
        print(f"EVENTO {time.strftime('%H:%M:%S')}: {status}")
```
