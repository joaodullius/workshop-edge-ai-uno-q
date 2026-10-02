# python/main.py — monitora A0 e acende o LED acima do limiar
from arduino.app_utils import App, Bridge
import time

THRESHOLD = 1.5   # volts

def loop():
    voltage = Bridge.call("read_sensor")
    if voltage > THRESHOLD:
        Bridge.call("set_led", True)
        print(f"ALERTA: {voltage:.2f} V acima do limiar")
    else:
        Bridge.call("set_led", False)
        print(f"Normal: {voltage:.2f} V")
    time.sleep(0.5)

def on_tick(seconds: int):
    print(f"MCU ligado ha {seconds} s")

Bridge.provide("on_tick", on_tick)   # expoe a funcao ao sketch

App.run(user_loop=loop)
