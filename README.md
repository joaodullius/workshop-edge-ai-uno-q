# Workshop Edge AI com Arduino UNO Q: kit de apps e manual

Material de apoio para o workshop de Edge AI com a placa Arduino UNO Q 4GB:

- **`manual/`**: o Manual do Laboratório de IA Edge 1, com 16 laboratórios (PDF);
- **`apps/`**: apps prontos do Arduino App Lab, um ponto de partida ou gabarito para cada bloco do workshop;
- **`instalar_kit.sh`**: script que copia os apps para uma placa e a deixa pronta para a aula;
- **`fotos-de-teste/`**: duas fotos para o laboratório de IA em uma foto, uma com pessoa e uma sem.

Testado com Arduino App Lab 0.10.0, `arduino-app-cli` 0.13.0 e Bricks da série 0.12.

## Instalação em uma placa

Pré-requisitos: a placa já passou pela configuração inicial (Laboratório 0 do manual), está ligada e acessível por SSH a partir do seu computador, pelo nome (`<nome>.local`) ou pelo IP.

No computador do instrutor (Git Bash no Windows, ou o terminal no macOS e no Linux), dentro desta pasta:

```bash
bash instalar_kit.sh <nome-ou-ip-da-placa> <trilha> [aquecer]
```

| Trilha | O que instala |
|---|---|
| `1h` | workshop de 1 hora, sem câmera |
| `1h-cam` | workshop de 1 hora, com câmera |
| `3h` | workshop de 3 horas, sem câmera |
| `3h-cam` | workshop de 3 horas, com câmera |
| `completo` | todos os apps |

Exemplos:

```bash
bash instalar_kit.sh uno-q-07.local 1h aquecer
bash instalar_kit.sh 192.168.0.42 3h-cam
```

O que o script faz:

1. Copia os apps da trilha para `/home/arduino/ArduinoApps/` na placa. Se já existir um app com o mesmo nome (`ws-lab…`), ele é substituído; os outros apps da placa não são tocados.
2. Com a opção `aquecer`, inicia e para cada app uma vez. Isso baixa o container do modelo de IA (quase 1 GB na primeira vez) e compila o sketch de cada app, para que essa espera não aconteça durante a aula. Conte com 1 a 3 minutos por app; a trilha `1h` levou cerca de 9 minutos em uma placa.

Depois da instalação os apps aparecem em **My Apps**, no App Lab, com nomes que começam por "WS".

Observações:

- A cópia pede a senha do usuário `arduino` a cada app, a menos que a chave SSH do seu computador esteja instalada na placa (`ssh-copy-id arduino@<placa>`).
- Os apps de vídeo com webcam não iniciam sem a câmera ligada. O script só os copia e avisa; com a placa já no hub e a webcam conectada, inicie cada um uma vez pelo App Lab.
- Rodar o script de novo devolve os apps `ws-…` ao estado original. Use isso entre uma turma e outra.

## Os apps

| App (nome em My Apps) | Pasta | Laboratório do manual | Precisa de câmera |
|---|---|---|---|
| WS Lab 1 Blink | `ws-lab01-blink` | 1: o Python pisca o LED do microcontrolador | não |
| WS Lab 2 IA em uma foto | `ws-lab02-foto` | 2, Parte C: detecção de objetos em uma foto enviada pelo navegador | não |
| WS Lab 4 Bridge | `ws-lab04-bridge` | 4, Partes A e B: funções do sketch chamadas pelo Python, com a latência medida | não |
| WS Lab 4 Desafio (partida) | `ws-lab04-desafio-partida` | 4, Parte E: ponto de partida do desafio | não |
| WS Lab 4 Desafio foto e LED | `ws-lab04-desafio` | 4, Parte E: gabarito, o LED acende quando a foto tem uma pessoa | não |
| WS Lab 5 Laço de controle | `ws-lab05-laco` | 5, Parte C: três formas de fechar um laço de controle | não |
| WS Lab 9 Detecção ao vivo | `ws-lab09-video` | 8 e 9: detecção de objetos em vídeo | webcam |
| WS Lab 9 Classificador de pessoa | `ws-lab09-pessoa` | 8 e 9: modelo leve de pessoa, com contador e LED | webcam |
| WS Lab 9 Detecção e LED | `ws-lab09-video-led` | 9, Parte C: gabarito, o LED acende com uma pessoa na cena | webcam |
| WS Lab 9 Celular como câmera | `ws-lab09-celular` | 9, versão B: detecção com o vídeo do celular | celular |
| WS Lab 9 Celular e LED | `ws-lab09-celular-led` | 9, versão B: gabarito com contador e LED | celular |
| WS Lab 13 Sistema completo | `ws-lab13-deploy` | 13: gabarito do app completo | webcam |
| WS Lab 14 Agente de borda | `ws-lab14-agente` | 14: gabarito do agente | webcam |

O código de cada app é o mesmo dos blocos de código do manual.

## Hardware

- **Sem câmera:** placa Arduino UNO Q 4GB, cabo USB-C com dados e um computador com o Arduino App Lab.
- **Com webcam:** a placa tem uma única porta USB-C, então é preciso um hub USB-C com Power Delivery, uma fonte de 3 A e uma webcam USB; o computador fala com a placa pela rede Wi-Fi.
- **Com celular como câmera:** o app Arduino IoT Remote no celular, na mesma rede Wi-Fi da placa.

## Estado da validação

- Os apps sem câmera foram executados em uma placa, do início ao fim, seguindo o manual.
- Os apps com webcam foram verificados quanto ao código e à compilação do sketch; a execução com câmera do texto final do manual ainda não foi repetida.
- A versão com celular foi testada até a página do código QR; o pareamento com o celular ainda não foi feito.

## Origem dos arquivos

Vários apps partem dos exemplos oficiais do Arduino App Lab, distribuídos sob a licença MPL-2.0; os arquivos derivados mantêm o cabeçalho de licença original. As fotos de teste vêm dos mesmos exemplos.
