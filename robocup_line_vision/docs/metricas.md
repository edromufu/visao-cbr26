# Métricas medidas

Todas medidas nesta sessão (11–12/11/2026), na nuvem: CPU Intel Xeon 2,1 GHz,
2 núcleos, Python 3.13 e, para os testes de compatibilidade, Python 3.10 com
as versões do Ubuntu 22.04/Humble (numpy 1.21.5, OpenCV 4.5.4, SciPy 1.8,
pandas 1.3.5). O YOLO rodou com ultralytics 8.3.189 em CPU. Nada foi medido no
robô, no WSL nem no NUC.

Para reproduzir:

```bash
python3 tools/validar_calibracao.py --kit <kit_visao> --seg <repositório original da etapa 1> --saida docs/validacao_p0
python3 tools/avaliar_gt.py --kit <kit_visao> --saida docs/metricas_gt --rotulo _sem_yolo
python3 tools/avaliar_gt.py --kit <kit_visao> --modelo modelo/best.pt --saida docs/metricas_gt --rotulo _yolo
python3 tools/avaliar_sintetico.py -n 40 --seed 11 --saida docs/metricas_sintetico [--variantes]
python3 tools/medir_fps.py --kit <kit_visao> [--modelo modelo/best.pt]
python3 tools/html/test_core_node.py /tmp/js <imagens>     # equivalência do calibrador HTML
python3 -m pytest test/                                    # testes unitários
```

## 1. Calibração (P0) — `docs/validacao_p0/`

### Equivalência com o código original

* Adaptador × repositório original da etapa 1 rodado na própria pasta, nos 6
  frames do kit: máscaras branca e verde, máscara do campo, `campo_detectado`,
  esqueleto e polilinhas **idênticos** (6/6).
* Limiar do branco do CSV original: `[45, 0, 213]`–`[164, 43, 255]` (igual ao
  brief).
* `white_pixels.csv` gerado pela ferramenta, lido pela fórmula original:
  devolve **exatamente** a faixa escolhida (7 faixas de teste, inclusive
  extremos 0 e 255; e 6 faixas geradas pelo HTML).

### (i) Webots, calibração manual simulada (pinceladas sobre as linhas da verdade de terreno + retângulos de carpete)

Precisão/recall do esqueleto contra a verdade de terreno (tolerância 1 célula):

| frame | calibração original | proposta automática | após a tecla A |
|---|---|---|---|
| frame_webots | 0,88 / 0,93 | 0,26 / 0,53 | **0,88 / 0,93** |
| image | 0,92 / 0,66 | 0,47 / 0,58 | **0,92 / 0,66** |
| image_1 | 0,98 / 0,73 | 0,53 / 0,59 | **0,98 / 0,73** |
| image_2 | 0,65 / 0,78 | 0,67 / 0,78 | **0,65 / 0,78** |

Campo detectado nos 4. A proposta automática pega as placas de publicidade
(V = 212) como branco. A tecla A sugeriu **V mín. = 213**, o mesmo valor da
calibração original, e recuperou a qualidade dela.

### (ii) Fotos reais (NAO/SPL)

| foto | calibração original | manual (4 retângulos + 3 pinceladas) | rápida (2 cliques) | esqueleto rápida × manual (F1) |
|---|---|---|---|---|
| bitbots | campo **NÃO** | campo **SIM** (verde H55–75 S89–255 V15–109; branco S≤41 V≥176) | campo **SIM** | 0,91 |
| eliza | campo **NÃO** | campo **SIM** (verde H49–68 S118–255 V95–207; branco S≤55 V≥225) | campo **SIM** | 0,92 |

Overlays: `docs/validacao_p0/real_*.jpg` (original | manual | rápida).

### (iii) Perturbações nos 4 frames do Webots (8 tipos × 4 = 32 casos)

Tipos: escuro ×0,55, claro ×1,35, contraste 0,6 e 1,5, quente, frio, gama 1,8,
escuro + quente.

* Calibração original: campo detectado em **3 de 32**.
* Recalibração rápida (2 cliques + tecla A automática): campo detectado em
  **32 de 32**; esqueleto volta ao nível da calibração original sem
  perturbação (precisão ≥ referência − 0,05) em **27 de 32**. Falham
  "claro ×1,35" (3 frames) e "frio" (2 frames): o branco satura e placas e
  linhas ficam com a mesma cor (D21).

### Calibrador HTML × Python (`tools/html/test_core_node.py`)

* HSV: **16.777.216 de 16.777.216** cores iguais ao `cv2.COLOR_BGR2HSV`.
* 6 imagens × 3 faixas: campo detectado igual em 18/18; células de campo
  diferentes ≤ 13 de 14.018; esqueleto com ≤ 4 células diferentes; propostas de
  faixa iguais em 6/6; sugestão de V mín. igual em 18/18.
* Teste de ponta a ponta no Chromium: abrir foto real → R → 2 cliques → S →
  3 arquivos baixados → lidos pelo Python: campo detectado, 138 células de
  esqueleto (iguais ao calibrador OpenCV).

### Interface

* Calibrador OpenCV rodado num Xvfb (Qt) com cliques e teclas reais (XTest):
  R → clique no verde → clique na linha → campo SIM, OK → S → pasta versionada
  criada. Capturas de tela: `docs/validacao_p0/calibrador_opencv_xvfb.png` e
  `docs/validacao_p0/calibrador_html_chromium.png`.
* **Tempo de calibração com uma pessoa: NÃO MEDIDO.** O fluxo mínimo é R + 2
  cliques + S.

## 2. Cruzamentos na verdade de terreno da usuária (4 frames do Webots)

37 cruzamentos marcados = 30 "de cruzamento" (14 L, 10 T, 6 X) + 7 "X de
marca" (centro/pênalti). Raio de casamento 15 px. Detecções que caem numa
marca não contam como falso positivo de cruzamento.

| configuração | det | TP | FP | FN | precisão | recall | tipo certo entre os TP |
|---|---|---|---|---|---|---|---|
| grafo (artigo + extensões), sem YOLO | 10 | 3 | 7 | 27 | **0,30** | **0,10** | 1 de 3 |
| grafo + fusão YOLO (`best.pt`) | 19 | 12 | 7 | 18 | **0,63** | **0,40** | 12 de 12 |
| linha de base anterior (medição da usuária, só image_1) | 27 | 6 | 21 | 6 | 0,22 | — | — |

Por tipo (com YOLO): L 5/14, T 4/10, X 3/6. Marcas: 3 de 7 (só com YOLO).

Por imagem (com YOLO): frame_webots 4/4 (1 FP), image 1/8, image_1 3/8
(4 FP), image_2 4/10 (2 FP).

**Meta (precisão e recall ≥ 0,7): não atingida.** Causas medidas:

1. **Cruzamentos distantes e pequenos.** No Webots a câmera está a 0,70 m,
   sem inclinação e com FOV de 45°. Os cruzamentos da área do gol distante
   ficam a ~1–2 células um do outro na grade 1/8 (ex.: T 411,547 e L 401,554
   em `image.png`): não dá para separá-los nessa resolução, que é a do
   artigo.
2. **Linha fina perto de linha grossa some do esqueleto** (D10). No
   `image_1`, a linha do meio (relevo ~25) desaparece por 9 células ao cruzar o
   círculo (relevo ~190). Diagnóstico por cruzamento, com a configuração final
   sem YOLO: em 16 dos 30, o nó-chave mais próximo tem grau 0 ou 1 (linha não
   conectada na junção). Antes das conexões ponta→aresta e da distância
   candidata 7, eram 21 dos 30.
3. **Platô em linhas grossas** (D20, código original).

Nos overlays (`docs/metricas_gt/eval_*.jpg`, verde = verdade, cinza = marca,
laranja/rosa/vermelho = L/T/X detectados, caixas = YOLO) dá para ver cada
caso.

## 3. Linhas e círculo (Webots)

| | linhas longas (≥ 30 px) cobertas | precisão das linhas detectadas |
|---|---|---|
| IV-B (este pacote, sem YOLO) | 11/19 (0,58) | 35/58 (0,60) |
| IV-B com YOLO (máscara de traves/robôs) | 10/19 (0,53) | 34/55 (0,62) |
| linha de base: polilinhas da etapa 1 (`_extrair_segmentos_conectados`) | 11/19 (0,58) | 70/112 (0,62) |

A IV-B cobre o mesmo que a linha de base com **metade dos segmentos**
(58 × 112): são retas inteiras, não pedaços de polilinha. As 15 linhas curtas
(< 30 px, traços das marcas e lados curtos da área do gol) não são cobertas
(0/15).

Círculo central: 3 círculos na verdade de terreno. **2 de 3 acertados**
(`image.png`: centro a 14 px, eixo maior 0,99× o real; `image_1.png`: 3,4 px,
0,98×). Em `image_2.png` a elipse escolhida está errada (276 px fora).

## 4. Campo sintético (KidSize 9×6 m, câmera do AUREA, 40 poses, semente 11)

Semente diferente da usada para ajustar parâmetros (7). Sem YOLO (o detector
não foi treinado nesse visual). Calibração pela recalibração rápida simulada.

| | precisão | recall | recall < 2 m | recall 2–4 m | recall ≥ 4 m |
|---|---|---|---|---|---|
| cruzamentos | 0,40 | 0,22 | 2/7 | 16/40 (0,40) | 5/56 (0,09) |
| cruzamentos, com ruído de brilho e borrão | 0,48 | 0,15 | 6/14 | 6/35 | 1/40 |

Linhas longas: cobertura **0,86** (143/167), precisão **0,87** (195/224); com
ruído: 0,42 e 0,96 (o borrão apaga linhas finas). Campo detectado em 40/40.

## 5. Tempo por frame (sem YOLO, mediana, 1 processo)

| imagem | 1080×720 | 640×480 |
|---|---|---|
| frame_webots (pouca linha) | 30 ms (33 FPS) | 5 ms (187 FPS) |
| image_2 (vista com muita linha) | 77 ms (13 FPS) | 33 ms (30 FPS) |

Etapas em image_2 @ 640×480: etapa 1 = 3,8 ms, III-C = 10,0, IV-B = 4,7,
IV-A (+ extensão) = 14,5, fusão = 0,3. YOLO `best.pt` em CPU: ~25–38 ms por
frame depois do aquecimento (o primeiro frame leva > 1 s). **No NUC: NÃO
MEDIDO.**

## 6. Testes automáticos

* `pytest test/`: **88 passaram**, 3 pulados (linters do ament, que só
  existem no Docker/ROS). Iguais em Python 3.13 (numpy 2.5, OpenCV 5.0) e
  Python 3.10 (numpy 1.21.5, OpenCV 4.5.4).
* `flake8` com os plugins do ament (import-order google, quotes, builtins,
  comprehensions), 120 colunas: **0 avisos**. `pydocstyle --convention=pep257`
  (ignorando D401): **0 avisos**. `py_compile` de todos os `.py`: ok.
* Nó ROS com `rclpy` e mensagens simuladas: 3 testes (tópicos iguais aos do
  nó `finder`, `MarkingArray` com `heading_rays`, `FieldBoundary`, imagem de debug e
  `LandmarkArray`).
