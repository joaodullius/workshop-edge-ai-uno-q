from arduino.app_utils import App, Bridge

def record_distance(cm: float):
    print(f"Distancia: {cm:.1f} cm")

Bridge.provide("record_distance", record_distance)

App.run()
