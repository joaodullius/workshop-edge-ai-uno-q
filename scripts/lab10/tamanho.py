# Analise de tamanho de modelos: parametros x bytes por parametro
modelos = {
    "MobileNetV2":      {"params": 3_400_000,  "input": (224, 224, 3)},
    "MobileNetV1-0.25": {"params": 470_000,    "input": (128, 128, 3)},
    "EfficientNet-B0":  {"params": 5_300_000,  "input": (224, 224, 3)},
    "ResNet-50":        {"params": 25_600_000, "input": (224, 224, 3)},
    "YOLOv8-nano":      {"params": 3_200_000,  "input": (640, 640, 3)},
    "Tiny-YOLO":        {"params": 6_900_000,  "input": (416, 416, 3)},
}

print(f"{'Modelo':<20} {'Parametros':>12} {'FP32 (MB)':>10} {'INT8 (MB)':>10} {'Economia':>9}")
print("-" * 66)
for nome, info in modelos.items():
    fp32_mb = info["params"] * 4 / 1_000_000       # 4 bytes por peso; MB = 1 milhao de bytes
    int8_mb = info["params"] * 1 / 1_000_000       # 1 byte por peso
    economia = (1 - int8_mb / fp32_mb) * 100
    print(f"{nome:<20} {info['params']:>12,} {fp32_mb:>10.1f} {int8_mb:>10.1f} {economia:>8.0f}%")

print("\nRAM visivel no UNO Q (free -h): ~3,6 GiB")
print("Sistema + containers do App Lab em repouso: ~0,7 GiB")
print("Disponivel para modelo e aplicacao: ~2,9 GiB")
