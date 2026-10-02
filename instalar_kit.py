#!/usr/bin/env python3
"""Copia o kit de apps do workshop para uma placa Arduino UNO Q e, se pedido, "aquece" os apps
(inicia cada um uma vez, para baixar os containers e compilar os sketches antes da aula).

Uso:
    python instalar_kit.py <nome-ou-ip-da-placa> <trilha> [--aquecer]

    trilha:    1h | 1h-cam | 3h | 3h-cam | completo
    --aquecer: inicia e para cada app sem câmera da trilha (de 1 a 5 minutos por app)

Exemplos:
    python instalar_kit.py uno-q-07.local 1h --aquecer
    python instalar_kit.py 192.168.0.42 3h-cam

Não precisa de nenhuma biblioteca: usa os comandos ssh e scp do sistema (já vêm no Windows 10 ou mais novo,
no macOS e no Linux). A cópia pede a senha do usuário arduino, a menos que a chave SSH do computador
esteja instalada na placa. As trilhas estão em trilhas.txt. Faz o mesmo que instalar_kit.sh.
"""
import argparse
import pathlib
import shutil
import subprocess
import sys

AQUI = pathlib.Path(__file__).resolve().parent
DESTINO = "/home/arduino/ArduinoApps"


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


def rodar(cmd, mostrar=False):
    """Executa um comando e devolve a saída; encerra o script se ele falhar."""
    r = subprocess.run(cmd, capture_output=not mostrar, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.exit(f"falhou: {' '.join(cmd)}\n{(r.stderr or r.stdout or '').strip()}")
    return (r.stdout or "").strip()


def main():
    ap = argparse.ArgumentParser(description="Instala o kit de apps do workshop em uma placa Arduino UNO Q.")
    ap.add_argument("placa", help="nome (uno-q-07.local) ou IP da placa")
    ap.add_argument("trilha", help="1h, 1h-cam, 3h, 3h-cam ou completo")
    ap.add_argument("aquecer_pos", nargs="?", choices=["aquecer"], help=argparse.SUPPRESS)
    ap.add_argument("--aquecer", action="store_true", help="inicia e para cada app sem câmera uma vez")
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
    for app in apps:
        origem = AQUI / "apps" / app
        if not origem.is_dir():
            sys.exit(f"app ausente na pasta apps/: {app}")
        rodar(["ssh", alvo, f"rm -rf {DESTINO}/{app}"])
        rodar(["scp", "-q", "-r", str(origem), f"{alvo}:{DESTINO}/"])
        print(f"copiado {app}", flush=True)

    if aquecer:
        # Os apps de vídeo com webcam não iniciam sem câmera; aquece só os que não dependem dela.
        for app in apps:
            if app in webcam:
                print(f"pulado (precisa de webcam): {app}")
                continue
            print(f"aquecendo {app} ...", flush=True)
            saida = rodar(["ssh", alvo, f"arduino-app-cli app start user:{app} 2>&1 | tail -1; sleep 8; "
                                        f"arduino-app-cli app stop user:{app} 2>&1 | tail -1"])
            print(saida)
    print("Pronto. Os apps aparecem em My Apps, no App Lab, com nomes que começam por WS.")


if __name__ == "__main__":
    main()
