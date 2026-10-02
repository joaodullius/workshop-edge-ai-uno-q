# Laboratório 5: Laço de controle entre domínios: código para copiar

Os blocos abaixo são os mesmos do manual, na mesma ordem. Copie daqui, e não do PDF: lá as linhas longas são quebradas.

## Parte A: Adicionar a biblioteca Servo

## Parte B: Laço de controle simples

**Passo 3** (sketch (C++))

```cpp
// sketch/sketch.ino — sensor, atuadores e uma versao agrupada do ciclo
#include <Arduino_RouterBridge.h>
#include <Servo.h>

Servo myServo;

int read_sensor_raw() {
    return analogRead(A0);                       // 0 a 1023
}

void set_servo(int angle) {
    myServo.write(constrain(angle, 0, 180));
}

void set_led(bool state) {
    digitalWrite(LED_BUILTIN, state ? LOW : HIGH); // LED_BUILTIN e ativo em LOW
}

// Ciclo completo em uma unica chamada: le, decide, atua e devolve a leitura
int sense_and_act(int threshold) {
    int raw = analogRead(A0);
    myServo.write(constrain(raw * 180 / 1024, 0, 180));   // multiplica antes: divisao inteira
    digitalWrite(LED_BUILTIN, raw > threshold ? LOW : HIGH);
    return raw;
}

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(A0, INPUT);
    myServo.attach(9);                           // servo em D9
    Bridge.begin();
    Bridge.provide("read_sensor_raw", read_sensor_raw);
    Bridge.provide("set_servo", set_servo);
    Bridge.provide("set_led", set_led);
    Bridge.provide("sense_and_act", sense_and_act);
}

void loop() {}
```

**Passo 4** (Python)

```python
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
```

## Parte C: Entender os limites de desempenho

**Passo 6** (Python)

```python
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
```
