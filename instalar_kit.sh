#!/bin/bash
# Copia o kit de apps do workshop para uma placa e, se pedido, "aquece" os apps
# (inicia cada um uma vez, para baixar os containers e compilar os sketches antes da aula).
#
# Uso (no computador do instrutor, com Git Bash, macOS ou Linux):
#   bash instalar_kit.sh <nome-ou-ip-da-placa> <trilha> [aquecer]
#
#   trilha:  1h | 1h-cam | 3h | 3h-cam | completo
#   aquecer: inicia e para cada app sem câmera da trilha (de 1 a 3 minutos por app)
#
# Exemplos:
#   bash instalar_kit.sh uno-q-07.local 1h aquecer
#   bash instalar_kit.sh 192.168.0.42 3h-cam
#
# A cópia pede a senha do usuário arduino, a menos que a chave SSH do computador esteja instalada na placa.
set -e
PLACA="$1"; TRILHA="$2"; AQUECER="$3"
AQUI="$(cd "$(dirname "$0")" && pwd)"
[ -n "$PLACA" ] && [ -n "$TRILHA" ] || { sed -n 2,16p "$0"; exit 1; }

SEM_CAM_1H="ws-lab01-blink ws-lab02-foto ws-lab04-bridge ws-lab04-desafio-partida ws-lab04-desafio"
COM_CAM_1H="ws-lab01-blink ws-lab09-video ws-lab09-celular ws-lab09-celular-led ws-lab09-pessoa ws-lab09-video-led ws-lab14-agente"
case "$TRILHA" in
  1h)       APPS="$SEM_CAM_1H" ;;
  1h-cam)   APPS="$COM_CAM_1H" ;;
  3h)       APPS="$SEM_CAM_1H ws-lab05-laco" ;;
  3h-cam)   APPS="$SEM_CAM_1H $COM_CAM_1H" ;;
  completo) APPS="$(ls "$AQUI/apps")" ;;
  *) echo "trilha desconhecida: $TRILHA"; exit 1 ;;
esac
APPS="$(echo $APPS | tr ' ' '\n' | sort -u | tr '\n' ' ')"

echo "Placa: $PLACA   trilha: $TRILHA"
for a in $APPS; do
  [ -d "$AQUI/apps/$a" ] || { echo "app ausente na pasta apps/: $a"; exit 1; }
  ssh "arduino@$PLACA" "rm -rf /home/arduino/ArduinoApps/$a"
  scp -q -r "$AQUI/apps/$a" "arduino@$PLACA:/home/arduino/ArduinoApps/"
  echo "copiado $a"
done

if [ "$AQUECER" = "aquecer" ]; then
  # Os apps de vídeo com webcam não iniciam sem câmera; aquece só os que não dependem dela.
  for a in $APPS; do
    case "$a" in ws-lab09-video|ws-lab09-video-led|ws-lab09-pessoa|ws-lab13-deploy|ws-lab14-agente) echo "pulado (precisa de webcam): $a"; continue ;; esac
    echo "aquecendo $a ..."
    ssh "arduino@$PLACA" "arduino-app-cli app start user:$a 2>&1 | tail -1; sleep 8; arduino-app-cli app stop user:$a 2>&1 | tail -1"
  done
fi
echo "Pronto. Os apps aparecem em My Apps, no App Lab, com nomes que começam por WS."
