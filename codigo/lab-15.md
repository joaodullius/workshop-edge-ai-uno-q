# Laboratório 15: Benchmarking e confiabilidade: código para copiar

Os blocos abaixo são os mesmos do manual, na mesma ordem. Copie daqui, e não do PDF: lá as linhas longas são quebradas.

## Parte A: O benchmark

**Passo 2** (Python)

```python
from arduino.app_utils import App
from arduino.app_bricks.video_imageclassification import VideoImageClassification
import time, statistics

stream = VideoImageClassification(confidence=0.3, debounce_sec=0.0)

# Um benchmark justo descarta o inicio (modelo carregando, caches frios)
# e mede um numero fixo de resultados em regime.
WARMUP = 30          # resultados descartados no inicio
MEASURE = 300        # resultados medidos (de 30 a 60 s, conforme a webcam)

timestamps = []      # instante de chegada de cada resultado medido
count = 0
done = False

def on_results(results: dict):
    global count, done
    if done:
        return
    count += 1
    if count <= WARMUP:
        if count == WARMUP:
            print(f"Aquecimento concluido ({WARMUP} resultados). Medindo...")
        return
    timestamps.append(time.perf_counter())
    if len(timestamps) == MEASURE:
        done = True
        report()

def report():
    # Intervalos entre resultados consecutivos, em ms: uma unica diferenca
    intervals = [(b - a) * 1000 for a, b in zip(timestamps, timestamps[1:])]
    intervals_sorted = sorted(intervals)
    avg = statistics.mean(intervals)
    p95 = intervals_sorted[int(len(intervals_sorted) * 0.95)]
    p99 = intervals_sorted[int(len(intervals_sorted) * 0.99)]
    print("=" * 50)
    print(f"RESULTADOS ({len(intervals)} intervalos)")
    print("=" * 50)
    print(f"Intervalo medio:  {avg:.1f} ms  ({1000/avg:.1f} resultados/s)")
    print(f"Desvio padrao:    {statistics.stdev(intervals):.1f} ms")
    print(f"Minimo / Maximo:  {min(intervals):.1f} / {max(intervals):.1f} ms")
    print(f"P95:              {p95:.1f} ms")
    print(f"P99:              {p99:.1f} ms")

stream.on_detect_all(on_results)
App.run()
```

## Parte B: Saúde do sistema

**Passo 4** (terminal)

```bash
cat > ~/monitor.sh <<'EOF'
#!/bin/bash
# Registra CPU (usuario+sistema), memoria usada e temperatura da CPU a cada 6 ou 7 s
echo "Hora,CPU%,Mem_MB,Temp_C"
while true; do
  CPU=$(top -bn2 -d1 | grep 'Cpu(s)' | tail -1 | awk '{print $2 + $4}')
  MEM=$(free -m | awk '/Mem:/ {print $3}')
  TEMP=$(cat /sys/class/thermal/thermal_zone3/temp 2>/dev/null || echo 0)
  TEMP_C=$(echo "scale=1; $TEMP / 1000" | bc)
  echo "$(date +%H:%M:%S),$CPU,$MEM,$TEMP_C"
  sleep 5
done
EOF
bash ~/monitor.sh | tee ~/system_log.csv
```

**Passo 5** (terminal)

```bash
scp arduino@<nome-da-placa>.local:~/system_log.csv .
```

## Parte C: Tolerância a falhas

**Passo 7** (Python)

```python
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
```

**Passo 9** (terminal)

```bash
arduino-app-cli app logs user:smart-agent | grep -a -E "EVENTO|WATCHDOG" | tail -20
```

## Parte D: Relatório de referência
