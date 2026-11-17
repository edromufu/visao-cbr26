# Relatório — pipeline de visão RoboCup (estrutura de linhas + YOLO)

Sessão de 11–12/11/2026, para o teste com a câmera real em **13/11/2026**.
Brief: `PROMPT_pipeline_visao.md` (Projeto "Visão"). Tudo o que não foi
executado aqui está marcado **NÃO TESTADO**.

## Resumo em 6 linhas

1. **P0 (calibração) pronto e testado:** calibrador OpenCV ao vivo (testado
   com cliques reais num Xvfb), calibrador HTML offline (núcleo conferido contra
   o Python) e captura de frames (com e sem ROS). Nas 2 fotos reais o campo
   passa de "não detectado" para **detectado** com 2 cliques.
2. **P1 (núcleo) pronto e testado:** III-C, IV-A, IV-B, elipse, fusão YOLO,
   modo sem ROS, gerador sintético e métricas; 88 testes.
3. **Cruzamentos no Webots (30 da verdade de terreno):** só o grafo dá
   precisão **0,30** e recall **0,10**; grafo + YOLO dá **0,63** e **0,40**
   (tipo certo em 12 de 12). A meta de 0,7 **não foi atingida**; as causas
   medidas estão na seção 3.
4. **Linhas:** cobertura das linhas longas 0,58 no Webots (igual à linha de
   base da etapa 1, com metade dos segmentos) e 0,86 no sintético (precisão
   0,87). Círculo central certo em 2 de 3.
5. **P2 (ROS 2) pronto, NÃO TESTADO em ROS:** nó fino, launch de simulação e
   de robô real, testes com `rclpy` simulado, flake8/pep257 sem avisos.
6. **P3:** documentação em `docs/` e roteiros 01–06 em `kit_visao/roteiros/`.

## 1. O que foi feito

### P0 — calibração de cor (`robocup_line_vision/calibration/`)

| Entregável | Arquivo | Estado |
|---|---|---|
| Calibrador ao vivo (câmera, imagens, tópico ROS opcional) | `calibrator_cv.py` | testado (sessão simulada + Xvfb com XTest); câmera real e tópico ROS NÃO TESTADOS |
| Calibrador HTML (arquivo único, offline) | `calibrador.html` (gerado de `tools/html/`) | testado no Chromium (Playwright) + equivalência com o Python |
| CSVs no formato da etapa 1 (`green_pixels.csv` denso, `white_pixels.csv`) + `calib_<data>.json` + `ultima/` | `core.py` | testado (os CSVs, lidos pelo código original, dão exatamente as faixas) |
| Recalibração rápida (R + 2 cliques), "usar o frame atual" (F), métricas de sanidade | `calibrator_cv.py`, `core.py` | testado |
| Tecla A (sugere V mínimo do branco para tirar placas/parede da fronteira) | `core.suggest_white_vmin` | testado (chega a 213 no Webots, o valor original) |
| Captura sem ROS / com ROS | `capture_frames.py` / `capture_frames_ros.py` | lógica testada; câmera e ROS NÃO TESTADOS |
| JSON do HTML → pasta versionada | `importar_json.py` | testado |

### P1 — núcleo (`robocup_line_vision/`)

* `stage1_adapter.py` usa o código original **sem alterar a lógica**. A
  saída é idêntica à do repositório original nos 6 frames. Há 3 linhas mudadas
  no `vendor/`, todas de importação e caminho (`vendor/VENDOR.md`).
* `graph_nodes.py` (III-C), `crossings.py` (IV-A), `lines.py` (IV-B + elipse),
  `fusion.py` + `detector.py` (YOLO `.pt` e `.onnx`), `camera_model.py`,
  `pipeline.py`, `params.py` + `config/params.yaml` (nenhum limiar espalhado no
  código).
* `python3 -m robocup_line_vision --camera N | --image ... | --video ...`, com
  overlay, FPS, `S` para salvar e `--sem-yolo`.
* `synthetic.py`: campo KidSize 9×6 m com a câmera do AUREA, poses aleatórias,
  ruído e borrão, e verdade de terreno automática.
* `evaluation.py` + `tools/avaliar_gt.py` + `tools/avaliar_sintetico.py`.

Detalhes por seção do artigo: `docs/arquitetura.md`. Decisões e desvios:
`docs/decisoes.md` (D1–D27).

### P2 — ROS 2 Humble

`ros/line_vision_node.py` é fino: a lógica fica toda no núcleo, e o nó só
converte as mensagens. Publica com os **mesmos nomes de tópico do nó `finder`**.
Lê a imagem por tópico (simulação) ou abre a câmera por índice (robô real,
como o `object_finder`). Usa `camera_info` quando recebe. Converte as
mensagens com numpy, sem `cv_bridge`. Publica `LandmarkArray`, opcional, com
IDs mapeados **por nome**. Launch: `launch/sim.launch.py` (com `soccer_ipm` e,
opcionalmente, o Webots do `my_package`) e `launch/real.launch.py`.
`package.xml` e `setup.py` seguem o padrão da EDROM (MIT, mantenedora EDROM).

### P3 — documentação

`docs/arquitetura.md`, `docs/decisoes.md`, `docs/calibracao.md`,
`docs/metricas.md`. Roteiros `kit_visao/roteiros/01` a `06`, cada um dizendo
onde roda e o que está NÃO TESTADO.

## 2. Números medidos (detalhes em `docs/metricas.md`)

### Calibração

| Teste | Resultado |
|---|---|
| Fotos reais (bitbots, eliza): calibração original | campo **NÃO** detectado (2/2) |
| Fotos reais: manual / rápida (2 cliques) | campo **detectado** (2/2 e 2/2); esqueleto rápida × manual F1 0,91 e 0,92 |
| 4 frames do Webots, manual + tecla A | esqueleto contra a verdade = igual à calibração original (P 0,65–0,98, R 0,66–0,93) |
| 32 frames perturbados (brilho, contraste, cor, gama) | original: campo em 3/32; rápida: campo em **32/32**, esqueleto no nível da referência em **27/32** (falham "claro ×1,35" e "frio": placas e linhas saturam na mesma cor) |
| HTML × Python | HSV igual em 16.777.216/16.777.216 cores; esqueleto ≤ 4 células diferentes; propostas iguais |
| Tempo de calibração com uma pessoa | **NÃO MEDIDO** (fluxo mínimo: R + 2 cliques + S) |

*Correção:* na mensagem do meio da sessão eu disse "26 de 32" para o
esqueleto recuperado. O número certo, pelo critério acima (precisão ≥
referência − 0,05), é **27 de 32**. Com o critério "precisão ≥ 0,8", são 23 de 32.

### Cruzamentos (verdade de terreno da usuária, 4 frames do Webots, raio 15 px)

| | precisão | recall | L | T | X | X de marca |
|---|---|---|---|---|---|---|
| só o grafo (artigo + extensões) | 0,30 | 0,10 | 0/14 | 1/10 | 2/6 | 0/7 |
| grafo + YOLO | **0,63** | **0,40** | 5/14 | 4/10 | 3/6 | 3/7 |
| linha de base anterior (medição da usuária, só `image_1`) | 0,22 | — | | | | |

Sintético (40 poses novas, sem YOLO): precisão 0,40, recall 0,22. O recall é
**0,40 entre 2 e 4 m**, 2/7 abaixo de 2 m e 0,09 acima de 4 m.

### Linhas e círculo

* Webots: linhas longas cobertas 11/19 (0,58), precisão 0,60. A linha de base
  da etapa 1 (polilinhas) tem 11/19 e 0,62, mas usa 112 segmentos contra os
  nossos 58.
* Sintético: cobertura 0,86, precisão 0,87 (com ruído e borrão: 0,42 e 0,96).
* Círculo central: 2 de 3 certos (centro a 14 e 3,4 px; eixo maior 0,99× e
  0,98×). Em `image_2` a elipse escolhida está errada.

### Tempo (CPU Xeon 2,1 GHz da nuvem, sem YOLO)

640×480: 5–33 ms por frame (30 a 187 FPS, conforme a quantidade de linha).
1080×720: 30–77 ms. YOLO em CPU: ~25–38 ms por frame depois do aquecimento.
**NUC: NÃO MEDIDO.**

### Testes

88 testes passam e 3 são pulados (linters do ament), tanto em Python 3.13
quanto em Python 3.10 com numpy 1.21.5 e OpenCV 4.5.4 (versões do Humble).
flake8 com os plugins do ament e pep257: 0 avisos. Instalação via `pip`
conferida (CSVs originais e o HTML vão junto).

## 3. Por que os cruzamentos não chegaram a 0,7 (medido, não suposto)

1. **Resolução da grade 1/8 com a câmera do AUREA** (FOV 45°, 0,70 m de
   altura, sem inclinação). Na verdade de terreno do Webots, a maioria dos
   cruzamentos fica longe: T e L da área do gol distante aparecem a ~1–2
   células um do outro (`image.png`: T 411,547 e L 401,554). No sintético, o
   recall acima de 4 m é 0,09 e entre 2 e 4 m é 0,40.
2. **Linha fina perto de linha grossa some do esqueleto.** No `image_1`, a
   linha do meio (relevo ~25) desaparece por 9 células ao cruzar o círculo
   (relevo ~190). Na configuração final, em 16 dos 30 cruzamentos o nó-chave
   mais próximo tem grau 0 ou 1, ou seja, a junção não se fechou. As
   conexões ponta→aresta (D11) e a extensão pelas retas (D10) melhoraram o
   sintético de P 0,21 / R 0,09 para P 0,46 / R 0,29 (semente de ajuste) e
   0,40 / 0,22 (semente nova), mas não resolvem tudo.
3. **Platô em linhas grossas** (borrão 5×5 da etapa 1, D20): perto da câmera o
   esqueleto corre na borda da linha.

O que o YOLO acrescenta: acerta muitos cruzamentos distantes (frame_webots:
4/4), mas sem `heading_rays`, por isso entra rebaixado (×0,5). O grafo dá as
direções. Os dois juntos são o melhor resultado medido.

## 4. Imagens

* Calibração: `docs/validacao_p0/real_bitbots.jpg`, `real_eliza.jpg`
  (original | manual | rápida), `webots_*.jpg`, `perturb_*.jpg`,
  `calibrador_opencv_xvfb.png`, `calibrador_html_chromium.png`.
* Cruzamentos, linhas e elipses contra a verdade de terreno:
  `docs/metricas_gt/eval_*_sem_yolo.jpg` e `eval_*_yolo.jpg`.
* Sintético: `docs/metricas_sintetico/sintetico_0*.jpg`.

Todas foram abertas e conferidas antes de escrever os números.

## 5. NÃO TESTADO (e por quê)

| Item | Por quê |
|---|---|
| Abrir a câmera real (USB, índice 2), no WSL/NUC/Windows | não há câmera na nuvem |
| HighGUI no WSLg | testado em Xvfb/Qt, não no WSLg |
| Tempo de calibração com uma pessoa (< 2 min) | sem usuário real |
| Qualquer coisa com ROS 2: `colcon build`, nó real, launch, `capture_frames_ros`, fonte `--ros-topico` do calibrador, `soccer_ipm`, `LandmarkArray` chegando no `localization_pkg` | sem ROS/Docker na nuvem; o nó só foi testado com `rclpy` e mensagens simulados |
| Webots + AUREA (`sim.launch.py`, `camera_info` real, conferir FOV 0,785/altura 0,70) | sem Webots |
| Docker da EDROM (`ros2_dev`) | o `docker-compose.yml` não estava no kit |
| Desempenho no NUC | sem NUC |
| Projeção ao chão no robô real (altura/inclinação da câmera, TF da cabeça) | sem robô; a homografia da EDROM é a identidade |
| `OnnxDetector` com o `best.onnx` da EDROM (`object_finder_onnx`) | testei o ONNX exportado do `best.pt`; o da EDROM tem outra data de treino |

## 6. Riscos para o dia 13

1. **WSL não enxergar a câmera** → captura no Windows (roteiro 04, 1B) +
   calibrador HTML. Treine esse caminho antes.
2. **Branco do fundo (paredes, placas, robôs) igual ao das linhas** → tecla A
   e conferir o esqueleto. Se a luz saturar (como "claro ×1,35"), baixe a
   exposição da câmera.
3. **Câmera real com FOV ≈ 92°** (fx ≈ 311 px em 640×480): as linhas ficam
   mais finas na imagem que no AUREA. É bom para o platô, ruim para linhas
   longe. Prefira olhar o campo de perto, com a cabeça inclinada.
4. **Dois nós disputando a câmera** (`object_finder` e este) → roteiro 06,
   seção 4.
5. **Distâncias para a localização** dependem de altura e inclinação reais da
   câmera; não publique `LandmarkArray` para o filtro sem validar.

## 7. Próximos passos sugeridos

* Com os frames reais do dia 13: marcar a verdade de terreno
  (`marcador_gt.html`) e rodar `tools/avaliar_gt.py`.
* Para a etapa 1 (III-B): borrão proporcional à largura da linha (D20).
* Classificar marcas (centro/pênalti) para o id 7 do `localization_pkg`.
* Adaptador `VisionData` (`vision2BhvTopic`) se este nó for substituir o
  `object_finder`.
