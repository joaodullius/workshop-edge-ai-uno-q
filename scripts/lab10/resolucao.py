# Tamanho do buffer de entrada por resolucao
resolucoes = [(48, 48), (96, 96), (160, 160), (224, 224), (320, 320), (416, 416)]

base = 224 * 224                                   # referencia: a entrada do MobileNetV2

print(f"{'Resolucao':<12} {'RGB (KB)':>10} {'Cinza (KB)':>11} {'vs 224x224':>11}")
print("-" * 47)
for w, h in resolucoes:
    rgb = w * h * 3 / 1024
    cinza = w * h * 1 / 1024
    print(f"{f'{w}x{h}':<12} {rgb:>10.1f} {cinza:>11.1f} {w * h / base:>10.2f}x")
