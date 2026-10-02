# Laboratório 12: Quantização, encolhendo o modelo: código para copiar

Os blocos abaixo são os mesmos do manual, na mesma ordem. Copie daqui, e não do PDF: lá as linhas longas são quebradas.

## Parte A: Registre a linha de base (float32)

## Parte B: Exporte as duas versões

## Parte C: Meça na placa

**Passo 13** (terminal)

```bash
cp ~/ArduinoApps/model-cost/ws_probe.py ~/ArduinoApps/meu-detector/
docker exec meu-detector-main-1 python3 /app/ws_probe.py ws://ei-video-obj-detection-runner:4912
```
