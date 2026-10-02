# Workshop Edge AI com Arduino UNO Q: kit de apps e manual

Material de apoio para o workshop de Edge AI com a placa Arduino UNO Q 4GB:

- **`manual/`**: o Manual do Laboratório de IA Edge 1, com 16 laboratórios (PDF);
- **`slides/`**: os slides dos 16 laboratórios, em PDF, na mesma ordem do manual;
- **`codigo/`**: todos os blocos de código do manual, um arquivo por laboratório, prontos para copiar (no PDF as linhas longas são quebradas);
- **`apps/`**: apps prontos do Arduino App Lab, com amostras para todos os laboratórios que têm código de app;
- **`scripts/`**: os scripts dos laboratórios que não rodam como app (Laboratórios 10 e 15);
- **`instalar_kit.sh`** e **`instalar_kit.py`**: instaladores que copiam os apps para uma placa e a deixam pronta para a aula;
- **`trilhas.txt`**: quais apps entram em cada trilha do workshop;
- **`fotos-de-teste/`**: duas fotos para o laboratório de IA em uma foto, uma com pessoa e uma sem.

O manual traz o passo a passo completo de cada laboratório; os slides são o resumo usado em aula, com o código principal e os números de referência. Em um workshop curto o instrutor conduz só alguns laboratórios, ou só algumas partes deles; com este material e uma placa, dá para fazer depois o que ficou de fora.

Testado com Arduino App Lab 0.10.0, `arduino-app-cli` 0.13.0 e Bricks da série 0.12.

## Instalação em uma placa

Pré-requisitos: a placa já passou pela configuração inicial (Laboratório 0 do manual), está ligada e acessível por SSH a partir do seu computador, pelo nome (`<nome>.local`) ou pelo IP.

Há dois instaladores, que fazem a mesma coisa. Use o que for mais prático.

**Python** (Windows, macOS ou Linux; não precisa de nenhuma biblioteca, só dos comandos `ssh` e `scp` do sistema):

```
python instalar_kit.py <nome-ou-ip-da-placa> <trilha> [--aquecer]
```

**Bash** (Git Bash no Windows, ou o terminal no macOS e no Linux):

```bash
bash instalar_kit.sh <nome-ou-ip-da-placa> <trilha> [aquecer]
```

| Trilha | O que instala |
|---|---|
| `1h` | workshop de 1 hora, sem câmera: Laboratórios 1, 2 e 4 |
| `1h-cam` | workshop de 1 hora, com câmera: Laboratórios 1, 8, 9 e 14 |
| `3h` | workshop de 3 horas, sem câmera: Laboratórios 1 a 5 |
| `3h-cam` | workshop de 3 horas, com câmera: Laboratórios 1, 2, 4, 8, 9 e 14 |
| `completo` | todos os apps da pasta `apps/` |

Exemplos:

```
python instalar_kit.py uno-q-07.local 1h --aquecer
bash instalar_kit.sh 192.168.0.42 3h-cam
```

O que o instalador faz:

1. Copia os apps da trilha para `/home/arduino/ArduinoApps/` na placa. Se já existir um app com o mesmo nome (`ws-lab…`), ele é substituído; os outros apps da placa não são tocados.
2. Com a opção de aquecer, inicia e para cada app uma vez. Isso baixa o container do modelo de IA (quase 1 GB na primeira vez) e compila o sketch de cada app, para que essa espera não aconteça durante a aula.

Depois da instalação os apps aparecem em **My Apps**, no App Lab, com nomes que começam por "WS".

Tempos medidos em uma placa:

| Operação | Tempo |
|---|---|
| Copiar os 32 apps (trilha `completo`, sem aquecer) | cerca de 1 min 30 s |
| Copiar e aquecer a trilha `1h` (6 apps) | cerca de 11 minutos |
| Copiar e aquecer a trilha `1h-cam`, com a webcam ligada (9 apps aquecidos) | cerca de 13 min 30 s |
| Copiar e aquecer a trilha `1h-cam`, sem câmera na placa (4 apps aquecidos, 5 pulados) | estimado em 7 minutos; não medido |
| Copiar e aquecer as trilhas `3h` e `3h-cam` | estimado em 15 a 20 minutos; não medido |
| Copiar e aquecer a trilha `completo` | estimado em 50 minutos; não medido |
| Primeira partida de um app com sketch | de 1 min 40 s a 2 min |
| Primeira partida de um app com a biblioteca Modulino (Laboratório 6) | cerca de 4 min 40 s |

Observações:

- A cópia pede a senha do usuário `arduino` a cada app, a menos que a chave SSH do seu computador esteja instalada na placa.
- Os apps que usam webcam só iniciam com a câmera ligada à placa. Se o instalador não encontra uma câmera, ele copia esses apps, não os aquece e lista no fim quais ficaram faltando. Com a placa já no hub e a webcam conectada, rode o instalador de novo com a opção de aquecer (ou inicie cada um uma vez pelo App Lab): os que têm sketch levam quase 2 minutos na primeira partida. A lista desses apps está em `trilhas.txt`.
- Rodar o instalador de novo devolve os apps `ws-…` ao estado original. Use isso entre uma turma e outra, sempre com a opção de aquecer: a reinstalação apaga também o sketch já compilado de cada app, e sem aquecer a primeira partida de cada um volta a levar de 1 min 40 s a 2 min.
- Durante o aquecimento o instalador fica até 2 minutos sem imprimir nada em cada app. É a compilação do sketch.
- Se um app não iniciar no aquecimento, o instalador mostra a mensagem de erro dele e o lista de novo no fim, depois do "Pronto". Quando encontra uma webcam, ele avisa que os apps de vídeo também serão aquecidos.
- Sem a opção de aquecer, o instalador só copia os arquivos (cerca de 15 segundos para a trilha `3h`). Serve para atualizar os apps, não para preparar uma aula: a primeira partida de cada app vai compilar o sketch, e em uma placa nova o primeiro app de IA baixa o container do modelo, o que leva de 5 a 10 minutos.
- O instalador só mexe nos apps da trilha pedida. Apps `ws-…` de outra trilha, instalados antes, continuam na placa como estavam; para atualizar todos, use a trilha `completo`.

## Amostras por laboratório

"Rodado na placa" diz se a amostra foi executada em uma placa real, do início ao fim, com a saída conferida.

| Lab | App (pasta em `apps/`) | O que é | Precisa de | Rodado na placa |
|---|---|---|---|---|
| 0 | não há | preparação da placa e do computador; não tem código de app | | |
| 1 | `ws-lab01-blink` | Parte A: o Python pisca o LED do microcontrolador | | sim |
| 1 | `ws-lab01-matriz` | Parte B: o Python desenha uma figura na matriz de LED da placa | | sim |
| 1 | `ws-lab01-cloud` | Parte E: o painel do Arduino Cloud acende o LED | conta Arduino Cloud | inicia sem erro; painel não testado |
| 2 | `ws-lab02-webui` | Parte A: página web servida pela placa | | sim |
| 2 | `ws-lab02-foto` | Parte C: detecção de objetos em uma foto enviada pelo navegador | | sim |
| 3 | `ws-lab03-botao` | Parte B: o sketch lê um botão em D2 e acende o LED | botão ou jumper | inicia; botão não testado |
| 3 | `ws-lab03-led` | Partes C e D: o Python pisca o LED pela Bridge | | sim |
| 4 | `ws-lab04-bridge` | Partes A e B: funções do sketch chamadas pelo Python, com a latência medida | | sim |
| 4 | `ws-lab04-monitor` | Partes C e D: laço de monitoramento e o MCU avisando o Python | | sim |
| 4 | `ws-lab04-desafio-partida` | Parte E: ponto de partida do desafio (app da foto, já com o sketch do LED e da matriz) | | inicia; o desafio é escrever o Python |
| 4 | `ws-lab04-desafio` | Parte E: gabarito. Com pessoa na foto, o LED acende e a matriz mostra um rosto feliz; sem pessoa, um X | | sim |
| 5 | `ws-lab05-laco-simples` | Parte B: laço de controle com três chamadas por ciclo | servo e potenciômetro, opcionais | sim, sem servo |
| 5 | `ws-lab05-laco` | Parte C: três formas de fechar o mesmo laço | servo e potenciômetro, opcionais | sim, sem servo |
| 6 | `ws-lab06-thermo` | Parte A: o MCU lê o Modulino Thermo | Modulino Thermo | sim, sem o sensor (leituras em zero) |
| 6 | `ws-lab06-semaforo` | variação: semáforo com Modulino Distance e Pixels | Modulino Distance e Pixels | inicia; sem os sensores não imprime nada |
| 6 | `ws-lab06-agregacao` | Parte C: média móvel e alertas, com o sketch de dois sensores da Parte B | Modulino Thermo e Distance | sim, sem os sensores |
| 6 | `ws-lab06-cloud` | Parte D: médias e alertas publicados no Arduino Cloud | Modulinos, conta Arduino Cloud | sim, sem os sensores; painel não testado |
| 7 | `ws-lab07-captura` | captura um quadro e salva em JPEG | webcam | não |
| 7 | `ws-lab07-fps` | mede a taxa de captura | webcam | não |
| 7 | `ws-lab07-pixels` | pixels, ordem BGR e escala de cinza | webcam | não |
| 8 | `ws-lab08-classificacao` | classificação em vídeo, com a sonda `ws_probe.py` na pasta do app | webcam | não |
| 8 e 9 | `ws-lab09-video` | detecção de objetos ao vivo, ponto de partida; traz a sonda `ws_probe.py` | webcam | não (o mesmo app com LED e matriz rodou) |
| 8 e 9 | `ws-lab09-pessoa` | classificador de pessoa, com contador, LED e um boneco na matriz | webcam | sim, com webcam |
| 9 | `ws-lab09-video-led` | Parte C: gabarito. Com uma pessoa na cena, o LED acende e a matriz mostra um boneco | webcam | sim, com webcam |
| 9 | `ws-lab09-celular` | versão B: detecção com o vídeo do celular, ponto de partida | celular com Arduino IoT Remote | inicia e mostra a senha de pareamento; o mesmo app com LED e matriz rodou com um celular |
| 9 | `ws-lab09-celular-led` | versão B: gabarito com contador, LED e matriz | celular com Arduino IoT Remote | sim, com um celular Android |
| 10 | `scripts/lab10/` | `tamanho.py` e `resolucao.py`: cálculos de memória de modelos | | sim |
| 11 | `ws-lab11-meu-detector` | app para o modelo treinado no Edge Impulse; o `.eim` é importado pelo App Lab. Traz a sonda `ws_probe.py` | webcam, conta Edge Impulse | não |
| 12 | não há | usa o app do Laboratório 11, que já traz a sonda do Laboratório 8 | | |
| 13 | `ws-lab13-deploy` | gabarito do app completo: detecção, página web, LED e relatório | webcam | não |
| 13 | `ws-lab13-monitor` | Parte D: CPU e memória com `psutil`, instalado pelo `requirements.txt` | internet na placa | sim |
| 14 | `ws-lab14-agente` | gabarito do agente de borda, um alarme de presença; a matriz mostra o estado (dois olhos, triângulo de aviso, pausa) | webcam | sim, com webcam |
| 15 | `ws-lab15-benchmark` | Parte A: intervalo entre resultados, com P95 e P99 | webcam | não |
| 15 | `ws-lab15-agente-watchdog` | Parte C: o agente com watchdog. Sem resultados por 5 s, desliga o alarme e pisca um X na matriz | webcam | sim, com webcam (cabo desligado e religado) |
| 15 | `scripts/lab15/monitor.sh` | Parte B: registra CPU, memória e temperatura; roda no terminal da placa | | sim |

O código de cada amostra é o mesmo dos blocos de código do manual; as que são cópia direta de um exemplo oficial mantêm os comentários originais, em inglês. Os apps marcados "sim, com webcam" rodaram com uma Logitech BRIO e uma pessoa na cena, com a matriz e o LED conferidos a olho. Os demais apps que precisam de webcam foram verificados quanto ao código e à compilação do sketch; sem câmera, a placa responde `No Camera Device Found` ao tentar iniciá-los (nos do Laboratório 7, o erro `CameraOpenError` aparece no console).

## A matriz de LED

A matriz de LED da placa (8 linhas por 13 colunas) aparece em cinco laboratórios: o aluno desenha uma figura no Laboratório 1; o desafio do Laboratório 4 mostra um rosto feliz ou um X conforme a foto; no Laboratório 9 um boneco aparece enquanto há uma pessoa na cena; e nos Laboratórios 14 e 15 a matriz mostra o estado do agente. O desenho é sempre uma grade de números no Python, enviada ao microcontrolador pela Bridge.

## Hardware

- **Sem câmera:** placa Arduino UNO Q 4GB, cabo USB-C com dados e um computador com o Arduino App Lab.
- **Com webcam:** a placa tem uma única porta USB-C, então é preciso um hub USB-C com Power Delivery, uma fonte de 3 A e uma webcam USB; o computador fala com a placa pela rede Wi-Fi.
- **Com celular como câmera:** o app Arduino IoT Remote no celular, na mesma rede Wi-Fi da placa.

## Origem dos arquivos

Vários apps partem dos exemplos oficiais do Arduino App Lab, distribuídos sob a licença MPL-2.0; os arquivos derivados mantêm o cabeçalho de licença original. As fotos de teste vêm dos mesmos exemplos.
