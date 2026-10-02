from arduino.app_utils import App, Bridge

def record_sensor_samples(celsius: float, humidity: float):
    # Chamado pelo sketch a cada segundo
    estado = "quente" if celsius > 28 else "ok"
    print(f"Temp: {celsius:.1f} C | Umidade: {humidity:.0f} % | {estado}")

Bridge.provide("record_sensor_samples", record_sensor_samples)

App.run()
