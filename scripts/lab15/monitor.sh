#!/bin/bash
# Registra CPU (usuario+sistema), memoria usada e temperatura da CPU a cada 6 ou 7 s
echo "Hora,CPU%,Mem_MB,Temp_C"
while true; do
  CPU=$(top -bn2 -d1 | grep 'Cpu(s)' | tail -1 | awk '{print $2 + $4}')
  MEM=$(free -m | awk '/Mem:/ {print $3}')
  TEMP=$(cat /sys/class/thermal/thermal_zone3/temp 2>/dev/null || echo 0)
  TEMP_C=$(echo "scale=1; $TEMP / 1000" | bc)
  echo "$(date +%H:%M:%S),$CPU,$MEM,$TEMP_C"
  sleep 5
done
