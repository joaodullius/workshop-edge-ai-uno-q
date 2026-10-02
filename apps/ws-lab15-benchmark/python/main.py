from arduino.app_utils import App
from arduino.app_bricks.video_imageclassification import VideoImageClassification
import time, statistics

stream = VideoImageClassification(confidence=0.3, debounce_sec=0.0)

# Um benchmark justo descarta o inicio (modelo carregando, caches frios)
# e mede um numero fixo de resultados em regime.
WARMUP = 30          # resultados descartados no inicio
MEASURE = 300        # resultados medidos (cerca de 30 s a 10 resultados/s)

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
