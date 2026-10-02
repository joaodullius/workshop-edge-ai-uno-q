# Laboratório 0: Preparando-se: código para copiar

Os blocos abaixo são os mesmos do manual, na mesma ordem. Copie daqui, e não do PDF: lá as linhas longas são quebradas.

## Parte A: Crie suas contas

## Parte B: Instale o Arduino App Lab

**Trecho** (terminal)

```bash
sudo apt install libwebkit2gtk-4.1-0
```

## Parte C: Conecte o UNO Q

## Parte D: Verifique o acesso por USB (ADB)

**Trecho** (terminal)

```bash
adb devices
adb shell
```

**Trecho** (terminal)

```bash
uname -a            # Linux ... aarch64
cat /etc/os-release # Debian GNU/Linux 13 (trixie)
free -h             # cerca de 3,6 GiB de RAM
df -h               # armazenamento interno (eMMC): / com ~10 GB e /home/arduino com ~18 GB
exit                # volta ao computador
```

## Parte E: Verifique o acesso por Wi-Fi (SSH)

**Trecho** (terminal)

```bash
ssh arduino@<nome-da-placa>.local
```

**Trecho** (terminal)

```bash
adb shell ip -4 addr show wlan0
```

## Parte F: Instale o conector do Arduino Cloud

**Trecho** (terminal)

```bash
sudo apt update && sudo apt install -y arduino-cloud-connector
systemctl status arduino-cloud-connector --no-pager | head -3
```
