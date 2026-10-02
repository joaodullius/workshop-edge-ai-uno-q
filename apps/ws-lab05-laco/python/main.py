# python/main.py — tres formas de fechar o mesmo laco
from arduino.app_utils import App, Bridge
import time, statistics

def run_loop(label, body, n=200):
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        body()
        times.append((time.perf_counter() - t0) * 1000)
    avg = statistics.mean(times)
    print(f"{label}: media {avg:.2f} ms ({1000/avg:.0f} Hz), "
          f"min {min(times):.2f}, max {max(times):.2f}, jitter {statistics.stdev(times):.2f} ms")

def three_calls():                    # A) tres chamadas por ciclo
    raw = Bridge.call("read_sensor_raw")
    Bridge.call("set_servo", int(raw / 1024 * 180))
    Bridge.call("set_led", raw > 512)

def one_call():                       # B) uma chamada agrupada, com retorno
    Bridge.call("sense_and_act", 512)

def one_notify():                     # C) uma chamada agrupada, sem esperar
    Bridge.notify("sense_and_act", 512)

run_loop("A) 3 x call", three_calls)
run_loop("B) 1 x call", one_call)
run_loop("C) 1 x notify", one_notify)

App.run()
