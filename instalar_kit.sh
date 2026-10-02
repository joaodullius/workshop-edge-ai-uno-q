#!/bin/bash
# Copia o kit de apps do workshop para uma placa e, se pedido, "aquece" os apps
# (inicia cada um uma vez, para baixar os containers e compilar os sketches antes da aula).
#
# Uso (no computador do instrutor, com Git Bash, macOS ou Linux):
#   bash instalar_kit.sh <nome-ou-ip-da-placa> <trilha> [aquecer]
#
#   trilha:  1h | 1h-cam | 3h | 3h-cam | completo
#   aquecer: inicia e para cada app da trilha uma vez (de 1 a 5 minutos por app)
#
# Exemplos:
#   bash instalar_kit.sh uno-q-07.local 1h aquecer
#   bash instalar_kit.sh 192.168.0.42 3h-cam
#
# A cópia pede a senha do usuário arduino, a menos que a chave SSH do computador esteja instalada na placa.
# Há uma versão equivalente em Python: instalar_kit.py. As trilhas estão em trilhas.txt.
# Os apps que usam webcam só iniciam com uma câmera ligada à placa. Sem câmera, o script os copia,
# não os aquece e lista no fim quais ficaram faltando.
set -e
PLACA="$1"; TRILHA="$2"; AQUECER="$3"
AQUI="$(cd "$(dirname "$0")" && pwd)"
[ -n "$PLACA" ] && [ -n "$TRILHA" ] || { sed -n 2,18p "$0"; exit 1; }

lista() { grep "^$1:" "$AQUI/trilhas.txt" | cut -d: -f2 | tr -d '\r'; }

if [ "$TRILHA" = "completo" ]; then
  APPS="$(ls "$AQUI/apps")"
else
  APPS="$(lista "$TRILHA")"
  [ -n "$APPS" ] || { echo "trilha desconhecida: $TRILHA (use 1h, 1h-cam, 3h, 3h-cam ou completo)"; exit 1; }
fi
WEBCAM=" $(lista precisa-de-webcam) "

echo "Placa: $PLACA   trilha: $TRILHA"
FALTOU=""
TOTAL=$(echo $APPS | wc -w | tr -d " ")
K=0
for a in $APPS; do
  K=$((K+1))
  [ -d "$AQUI/apps/$a" ] || { echo "app ausente na pasta apps/: $a"; exit 1; }
  # libera o container e a rede da instalação anterior ANTES de apagar a pasta: sem isso eles ficam órfãos na placa
  ssh "arduino@$PLACA" "arduino-app-cli app stop user:$a >/dev/null 2>&1; arduino-app-cli app destroy user:$a >/dev/null 2>&1; rm -rf /home/arduino/ArduinoApps/$a"
  scp -q -r "$AQUI/apps/$a" "arduino@$PLACA:/home/arduino/ArduinoApps/"
  echo "[$K/$TOTAL] copiado $a"
  case "$WEBCAM" in *" $a "*) FALTOU="$FALTOU $a" ;; esac
done

if [ "$AQUECER" = "aquecer" ]; then
  # Há uma câmera ligada à placa? (o decodificador Venus aparece como dispositivo de vídeo, mas não é câmera)
  CAMERAS=$(ssh "arduino@$PLACA" "v4l2-ctl --list-devices 2>/dev/null | grep -v '^[[:space:]]' | grep -v -i venus | grep -c . || true")
  [ "${CAMERAS:-0}" -gt 0 ] 2>/dev/null && FALTOU=""
  K=0
  for a in $APPS; do
    K=$((K+1))
    case " $FALTOU " in *" $a "*) echo "[$K/$TOTAL] pulado (precisa de webcam, e a placa não está vendo nenhuma): $a"; continue ;; esac
    echo "[$K/$TOTAL] aquecendo $a ... (até 2 minutos por app; cerca de 5 nos apps do Laboratório 6)"
    ssh "arduino@$PLACA" "arduino-app-cli app start user:$a 2>&1 | tail -1; sleep 8; arduino-app-cli app stop user:$a 2>&1 | tail -1" || true
  done
fi
echo "Pronto. Os apps aparecem em My Apps, no App Lab, com nomes que começam por WS."
if [ "$AQUECER" != "aquecer" ]; then
  echo
  echo "Os apps foram copiados SEM aquecer. A primeira partida de cada app com sketch vai levar até 2 minutos,"
  echo "e o primeiro app de IA em uma placa nova baixa um container de quase 1 GB (de 5 a 10 minutos)."
  echo "Para uma aula, rode de novo com a opção de aquecer."
fi
if [ -n "$FALTOU" ] && [ "$AQUECER" = "aquecer" ]; then
  echo
  echo "ATENÇÃO: estes apps usam webcam e NÃO foram aquecidos:"
  for a in $FALTOU; do echo "  $a"; done
  echo "Antes da aula, com a placa no hub e a webcam ligada, rode de novo com a opção de aquecer,"
  echo "ou inicie cada um uma vez pelo App Lab. Os que têm sketch levam quase 2 minutos na primeira partida."
fi
