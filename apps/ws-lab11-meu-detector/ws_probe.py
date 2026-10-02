# ws_probe.py: escuta o runner de modelos por 20 s e resume o tempo de inferencia
import asyncio, json, time, sys

URL = sys.argv[1] if len(sys.argv) > 1 else "ws://ei-video-obj-detection-runner:4912"

async def main():
    import websockets
    async with websockets.connect(URL, max_size=None) as ws:
        inicio = time.time()
        tempos = []
        n = 0
        while time.time() - inicio < 20:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=5)
            except asyncio.TimeoutError:
                print("nenhuma mensagem em 5 s (ha alguem na frente da camera?)")
                continue
            n += 1
            dado = json.loads(msg)
            if "timeMs" in dado:              # mensagens de resultado trazem o tempo de inferencia
                tempos.append(dado["timeMs"])
        duracao = time.time() - inicio
        print(f"{n} mensagens em {duracao:.1f} s = {n / duracao:.2f} resultados/s")
        if tempos:
            print(f"inferencia: media {sum(tempos) / len(tempos):.1f} ms, "
                  f"min {min(tempos)} ms, max {max(tempos)} ms (n={len(tempos)})")

asyncio.run(main())
