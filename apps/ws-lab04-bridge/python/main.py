# python/main.py — chama funcoes do sketch
from arduino.app_utils import App, Bridge
import time

# Passa parametros e recebe o retorno
print("7 + 3 =", Bridge.call("add_numbers", 7, 3))

# Le o sensor
voltage = Bridge.call("read_sensor")
print(f"Tensao no sensor: {voltage:.2f} V")

# Controla o LED
Bridge.call("set_led", True)
time.sleep(1)
Bridge.call("set_led", False)

import statistics

times = []
print("Medindo a latencia da Bridge (100 chamadas)...")
for _ in range(100):
    t0 = time.perf_counter()
    Bridge.call("read_sensor")
    times.append((time.perf_counter() - t0) * 1000)   # em ms

print(f"Media: {statistics.mean(times):.2f} ms")
print(f"Min:   {min(times):.2f} ms")
print(f"Max:   {max(times):.2f} ms")
print(f"Desvio padrao: {statistics.stdev(times):.2f} ms")

App.run()
