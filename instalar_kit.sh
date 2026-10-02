#!/bin/bash
# Copia o kit de apps do workshop para uma placa e, se pedido, "aquece" os apps
# (inicia cada um uma vez, para baixar os containers e compilar os sketches antes da aula).
#
# Uso (no computador do instrutor, com Git Bash, macOS ou Linux):
#   bash instalar_kit.sh <nome-ou-ip-da-placa> <trilha> [aquecer]
#
#   trilha:  1h | 1h-cam | 3h | 3h-cam | completo
#   aquecer: inicia e para cada app sem câmera da trilha (de 1 a 5 minutos por app)
#
# Exemplos:
#   bash instalar_kit.sh uno-q-07.local 1h aquecer
#   bash instalar_kit.sh 192.168.0.42 3h-cam
#
# A cópia pede a senha do usuário arduino, a menos que a chave SSH do computador esteja instalada na placa.
# Há uma versão equivalente em Python: instalar_kit.py. As trilhas estão em trilhas.txt.
set -e
PLACA="$1"; TRILHA="$2"; AQUECER="$3"
AQUI="$(cd "$(dirname "$0")" && pwd)"
[ -n "$PLACA" ] && [ -n "$TRILHA" ] || { sed -n 2,16p "$0"; exit 1; }

lista() { grep "^$1:" "$AQUI/trilhas.txt" | cut -d: -f2 | tr -d '\r'; }

if [ "$TRILHA" = "completo" ]; then
  APPS="$(ls "$AQUI/apps")"
else
  APPS="$(lista "$TRILHA")"
  [ -n "$APPS" ] || { echo "trilha desconhecida: $TRILHA (use 1h, 1h-cam, 3h, 3h-cam ou completo)"; exit 1; }
fi
WEBCAM=" $(lista precisa-de-webcam) "

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
    case "$WEBCAM" in *" $a "*) echo "pulado (precisa de webcam): $a"; continue ;; esac
    echo "aquecendo $a ..."
    ssh "arduino@$PLACA" "arduino-app-cli app start user:$a 2>&1 | tail -1; sleep 8; arduino-app-cli app stop user:$a 2>&1 | tail -1"
  done
fi
echo "Pronto. Os apps aparecem em My Apps, no App Lab, com nomes que começam por WS."
