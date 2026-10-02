from arduino.app_utils import App
import psutil, time

def monitor_loop():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    print(f"CPU {cpu:.0f}% | RAM {mem:.0f}%")
    time.sleep(4)

App.run(user_loop=monitor_loop)
