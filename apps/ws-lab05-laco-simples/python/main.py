# python/main.py — laco de controle com medicao de frequencia e jitter
from arduino.app_utils import App, Bridge
import time, statistics

loop_times = []

def control_cycle():
    # SENTIR: ler o sensor no MCU
    raw = Bridge.call("read_sensor_raw")
    # PENSAR: decidir no MPU
    angle = int(raw / 1024 * 180)         # mapeia 0-1023 para 0-180 graus
    led_on = raw > 512
    # AGIR: comandar atuadores no MCU
    Bridge.call("set_servo", angle)
    Bridge.call("set_led", led_on)
    return raw, angle

print("Laco de controle: 200 iteracoes")
for i in range(200):
    t0 = time.perf_counter()
    raw, angle = control_cycle()
    loop_ms = (time.perf_counter() - t0) * 1000
    loop_times.append(loop_ms)
    if i % 20 == 0:
        print(f"Iteracao {i}: sensor={raw}, angulo={angle}, ciclo={loop_ms:.1f} ms ({1000/loop_ms:.0f} Hz)")

avg = statistics.mean(loop_times)
print(f"\nEstatisticas do laco:")
print(f"  Media:  {avg:.2f} ms ({1000/avg:.0f} Hz)")
print(f"  Min:    {min(loop_times):.2f} ms")
print(f"  Max:    {max(loop_times):.2f} ms")
print(f"  Jitter: {statistics.stdev(loop_times):.2f} ms")

App.run()
