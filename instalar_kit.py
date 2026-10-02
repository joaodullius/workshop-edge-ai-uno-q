#!/usr/bin/env python3
"""Copia o kit de apps do workshop para uma placa Arduino UNO Q e, se pedido, "aquece" os apps
(inicia cada um uma vez, para baixar os containers e compilar os sketches antes da aula).

Uso:
    python instalar_kit.py <nome-ou-ip-da-placa> <trilha> [--aquecer]

    trilha:    1h | 1h-cam | 3h | 3h-cam | completo
    --aquecer: inicia e para cada app da trilha uma vez (de 1 a 5 minutos por app)

Exemplos:
    python instalar_kit.py uno-q-07.local 1h --aquecer
    python instalar_kit.py 192.168.0.42 3h-cam

Não precisa de nenhuma biblioteca: usa os comandos ssh e scp do sistema (já vêm no Windows 10 ou mais novo,
no macOS e no Linux). A cópia pede a senha do usuário arduino, a menos que a chave SSH do computador
esteja instalada na placa. As trilhas estão em trilhas.txt. Faz o mesmo que instalar_kit.sh.

Os apps que usam webcam só iniciam com uma câmera ligada à placa. Se o instalador não encontrar uma câmera,
ele copia esses apps, não os aquece e lista no fim quais ficaram faltando.
"""
import argparse
import pathlib
import shutil
import subprocess
import sys

AQUI = pathlib.Path(__file__).resolve().parent
DESTINO = "/home/arduino/ArduinoApps"

# A placa responde com caracteres como "✓"; em terminais que não são UTF-8 isso não pode derrubar o instalador.
# Fora de um console (Git Bash, redirecionamento para arquivo), a saída vai em UTF-8.
for _fluxo in (sys.stdout, sys.stderr):
    try:
        if _fluxo.isatty():
            _fluxo.reconfigure(errors="replace")
        else:
            _fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def ler_trilhas():
    """Lê trilhas.txt e devolve {nome: [apps]}."""
    trilhas = {}
    for linha in (AQUI / "trilhas.txt").read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or ":" not in linha:
            continue
        nome, apps = linha.split(":", 1)
        trilhas[nome.strip()] = apps.split()
    return trilhas


def rodar(cmd, tolerar_erro=False):
    """Executa um comando e devolve a saída; encerra o script se ele falhar."""
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0 and not tolerar_erro:
        sys.exit(f"falhou: {' '.join(cmd)}\n{(r.stderr or r.stdout or '').strip()}")
    return (r.stdout or "").strip()


def main():
    ap = argparse.ArgumentParser(description="Instala o kit de apps do workshop em uma placa Arduino UNO Q.")
    ap.add_argument("placa", help="nome (uno-q-07.local) ou IP da placa")
    ap.add_argument("trilha", help="1h, 1h-cam, 3h, 3h-cam ou completo")
    ap.add_argument("aquecer_pos", nargs="?", choices=["aquecer"], help=argparse.SUPPRESS)
    ap.add_argument("--aquecer", action="store_true", help="inicia e para cada app da trilha uma vez")
    ap.add_argument("--usuario", default="arduino", help="usuário Linux da placa (padrão: arduino)")
    args = ap.parse_args()
    aquecer = args.aquecer or args.aquecer_pos == "aquecer"

    for ferramenta in ("ssh", "scp"):
        if not shutil.which(ferramenta):
            sys.exit(f"comando '{ferramenta}' não encontrado. No Windows, instale o Cliente OpenSSH (Configurações, Recursos opcionais).")

    trilhas = ler_trilhas()
    if args.trilha == "completo":
        apps = sorted(p.name for p in (AQUI / "apps").iterdir() if p.is_dir())
    elif args.trilha in trilhas and args.trilha != "precisa-de-webcam":
        apps = trilhas[args.trilha]
    else:
        sys.exit(f"trilha desconhecida: {args.trilha} (use 1h, 1h-cam, 3h, 3h-cam ou completo)")
    webcam = set(trilhas.get("precisa-de-webcam", []))
    alvo = f"{args.usuario}@{args.placa}"

    print(f"Placa: {args.placa}   trilha: {args.trilha}")
    for k, app in enumerate(apps, 1):
        origem = AQUI / "apps" / app
        if not origem.is_dir():
            sys.exit(f"app ausente na pasta apps/: {app}")
        # libera o container e a rede da instalação anterior ANTES de apagar a pasta: sem isso eles ficam órfãos na placa
        rodar(["ssh", alvo, f"arduino-app-cli app stop user:{app} >/dev/null 2>&1; "
                            f"arduino-app-cli app destroy user:{app} >/dev/null 2>&1; rm -rf {DESTINO}/{app}"])
        rodar(["scp", "-q", "-r", str(origem), f"{alvo}:{DESTINO}/"])
        print(f"[{k}/{len(apps)}] copiado {app}", flush=True)

    faltou = [a for a in apps if a in webcam]
    if aquecer:
        # Há uma câmera ligada à placa? (o decodificador Venus aparece como dispositivo de vídeo, mas não é câmera)
        cameras = rodar(["ssh", alvo, "v4l2-ctl --list-devices 2>/dev/null | grep -v '^[[:space:]]' | grep -v -i venus | grep -c . || true"],
                        tolerar_erro=True)
        tem_camera = cameras.strip().isdigit() and int(cameras.strip()) > 0
        if tem_camera:
            faltou = []
        for k, app in enumerate(apps, 1):
            if app in webcam and not tem_camera:
                print(f"[{k}/{len(apps)}] pulado (precisa de webcam, e a placa não está vendo nenhuma): {app}")
                continue
            print(f"[{k}/{len(apps)}] aquecendo {app} ... (até 2 minutos por app; cerca de 5 nos apps do Laboratório 6)", flush=True)
            print(rodar(["ssh", alvo, f"arduino-app-cli app start user:{app} 2>&1 | tail -1; sleep 8; "
                                      f"arduino-app-cli app stop user:{app} 2>&1 | tail -1"], tolerar_erro=True), flush=True)

    print("Pronto. Os apps aparecem em My Apps, no App Lab, com nomes que começam por WS.")
    if not aquecer:
        print("\nOs apps foram copiados SEM aquecer. A primeira partida de cada app com sketch vai levar até 2 minutos,\n"
              "e o primeiro app de IA em uma placa nova baixa um container de quase 1 GB (de 5 a 10 minutos).\n"
              "Para uma aula, rode de novo com a opção de aquecer.")
        if faltou:
            print(f"Dos apps copiados, {len(faltou)} só iniciam com uma webcam ligada à placa (lista em trilhas.txt).")
    if faltou and aquecer:
        print("\nATENÇÃO: estes apps usam webcam e NÃO foram aquecidos:")
        for app in faltou:
            print(f"  {app}")
        print("Antes da aula, com a placa no hub e a webcam ligada, rode de novo com a opção de aquecer,\n"
              "ou inicie cada um uma vez pelo App Lab. Os que têm sketch levam quase 2 minutos na primeira partida.")


if __name__ == "__main__":
    main()
