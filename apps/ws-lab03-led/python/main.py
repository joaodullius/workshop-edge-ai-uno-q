# python/main.py — pisca o LED do MCU a partir do Python
from arduino.app_utils import App, Bridge
import time

state = False

def loop():
    global state
    state = not state
    Bridge.call("set_led", state)
    print("LED do MCU:", "ON" if state else "OFF")
    time.sleep(1)

App.run(user_loop=loop)   # o App Lab chama loop() repetidamente
