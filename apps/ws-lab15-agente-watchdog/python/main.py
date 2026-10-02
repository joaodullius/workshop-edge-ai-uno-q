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

import threading

tracker = DetectionTracker()
led_on = False
events = 0
last_result_time = None          # horario do ultimo resultado; o watchdog so vale depois do primeiro
WATCHDOG_TIMEOUT = 5.0           # segundos sem resultado para considerar falha
safe_mode = False

# Aviso de falha: um X, que o watchdog faz piscar enquanto o modelo nao responde
ICONES["FALHA"] = Frame.from_rows([
    [7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 7],
    [0, 0, 7, 7, 0, 0, 0, 0, 0, 7, 7, 0, 0],
    [0, 0, 0, 0, 7, 7, 0, 7, 7, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 7, 7, 7, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 7, 7, 7, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 7, 7, 0, 7, 7, 0, 0, 0, 0],
    [0, 0, 7, 7, 0, 0, 0, 0, 0, 7, 7, 0, 0],
    [7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 7],
]).to_board_bytes()
pisca = False

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
    global events, last_result_time
    last_result_time = time.time()            # sinal de vida para o watchdog
    events += 1
    status = tracker.update(results)

    if status == "ALERT_NEW" or status.startswith("ALERT_CLEARED"):
        print(f"EVENTO {time.strftime('%H:%M:%S')}: {status}")

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

def watchdog_check():
    """Se o modelo parou de responder, leva o sistema para o estado seguro e avisa da falha."""
    global safe_mode, led_on, estado_na_matriz, pisca
    parado = (last_result_time is not None
              and time.time() - last_result_time > WATCHDOG_TIMEOUT)
    if parado and not safe_mode:
        safe_mode = True
        print(f"WATCHDOG {time.strftime('%H:%M:%S')}: FALHA, sem resultados ha "
              f"{WATCHDOG_TIMEOUT:.0f} s (camera desconectada?). Entrando em modo seguro.")
        tracker.state = "IDLE"            # o agente esquece o alerta em curso
        tracker.presence_start = None     # e volta a exigir presenca sustentada
        led_on = False
        try:
            Bridge.call("set_led_state", False)   # estado seguro: alarme desligado
        except Exception as e:
            print(f"WATCHDOG: falha ao falar com o MCU: {e}")
    elif not parado and safe_mode:
        safe_mode = False
        print(f"WATCHDOG {time.strftime('%H:%M:%S')}: resultados voltaram. Operacao normal.")

    if safe_mode:                         # a falha fica visivel: um X piscando na matriz
        pisca = not pisca
        estado_na_matriz = "FALHA"        # faz mostra_estado() redesenhar quando os resultados voltarem
        try:
            Bridge.call("draw", ICONES["FALHA"] if pisca else bytes(104))
        except Exception as e:
            print(f"WATCHDOG: falha ao falar com o MCU: {e}")

def watchdog_loop():
    while True:                           # roda em paralelo ao resto do app
        time.sleep(0.5)                   # confere duas vezes por segundo; e tambem o ritmo do X que pisca
        watchdog_check()

threading.Thread(target=watchdog_loop, daemon=True).start()

stream.on_detect_all(on_results)
App.run()
