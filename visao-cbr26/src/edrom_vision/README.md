# visao-cbr26 — branch giovanna

> Os comandos abaixo partem da raiz do repositório (a pasta que contém `requirements.txt`).

Mesma estrutura da branch `ivan` (`visao-cbr26/src/edrom_vision/{object_finder, soccer_interfaces}`,
câmera pelo `usb_cam`, mensagens `soccer_interfaces`; os pacotes de IPM entram depois), com a visão por
**estrutura de linhas** (Schulz, Liu, Stückler, Behnke, *Line Structure-based Localization for
Soccer Robots*, Humanoids 2009) integrada ao YOLO no pacote `object_finder`.

## Teste rápido

```bash
pip install -r requirements.txt
cd visao-cbr26 && colcon build --symlink-install && source install/setup.bash
ros2 launch object_finder vision.launch.py video_device:=/dev/video2   # câmera USB (padrão: /dev/video0)
ros2 launch object_finder vision.launch.py simulacao:=true              # ou no Webots
```

Para descobrir o dispositivo da câmera: `v4l2-ctl --list-devices`. Use o primeiro `/dev/videoN` da câmera, porque o segundo é só de metadados.
Antes de testar no campo real, calibre o verde e o branco (`ros2 run object_finder calibrador`, ver abaixo).

## Funcionalidades

| Funcionalidade | Onde (`object_finder/object_finder/`) |
|---|---|
| Fronteira do campo e esqueleto das linhas (III-A/III-B, código original da etapa 1) | `vendor/`, `stage1_adapter.py` |
| Nós e conexões sobre o esqueleto (III-C) | `graph_nodes.py` |
| Cruzamentos L/T/X com `heading_rays` (IV-A) + extensão por interseção de retas/elipse | `crossings.py` |
| Linhas por split-and-merge e elipse do círculo central (IV-B) | `lines.py` |
| Fusão com o YOLO: caixas mascaram o branco, rejeição fora do campo, confirmação de cruzamentos, T→X | `fusion.py` |
| Detector YOLO: `.pt` (ultralytics), `.onnx` (só onnxruntime) ou sem YOLO | `detector.py` |
| Projeção ao chão própria (fov, `.npy` da EDROM ou `camera_info`): distância/ângulo de cruzamentos e linhas | `camera_model.py` |
| Todos os limiares num YAML | `params.py`, `config/params.yaml` |
| Orquestração sem ROS, diagnósticos (rejeitados, verificação, tempos) e resumo JSON | `pipeline.py` |
| Overlay de debug (fronteira, esqueleto, grafo, linhas, cruzamentos, YOLO, FPS) | `overlay.py` |
| Nó ROS 2 (`finder`) e conversão de mensagens | `connecting_and_showing.py`, `msg_conversion.py` |
| Modo sem ROS (câmera, imagens ou vídeo) | `__main__.py` (`line_vision`) |
| Calibração de cor: calibrador OpenCV, calibrador HTML offline, captura de frames, importação do JSON | `calibration/` |
| Campo sintético e métricas | `synthetic.py`, `evaluation.py`, `tools/` |

## Tópicos do nó `vision`

| Tópico | Tipo | Observação |
|---|---|---|
| `balls_in_image`, `goal_posts_in_image`, `robots_in_image` | `soccer_vision_2d_msgs` | só detecções dentro do campo |
| `markings_in_image` | `soccer_vision_2d_msgs/MarkingArray` | `intersections` com `heading_rays`, `segments`, `ellipses` |
| `field_boundary_in_image` | `soccer_vision_2d_msgs/FieldBoundary` | só quando o campo é detectado |
| `processed_image_topic` | `sensor_msgs/Image` | overlay (`publish_debug_image`) |
| `line_vision/markings_relative` | `soccer_vision_3d_msgs/MarkingArray` | opcional (`publish_projection`), ver abaixo |

Todos os nomes podem ser trocados pelos parâmetros `topics.*`. O nó assina `image_topic`
(padrão `/camera/image_raw`, do `usb_cam`) e `camera_info_topic` (padrão `/camera/camera_info`).

### Projeção ao chão própria

Os tópicos `*_in_image` estão em pixels; o IPM (`soccer_ipm`) que os leva ao chão entra depois.
Independente dele, o nó projeta sozinho cruzamentos e linhas com `publish_projection:=True`:

* `line_vision/markings_relative` (`soccer_vision_3d_msgs/MarkingArray`), `frame_id` =
  `projection_frame` (padrão `base_footprint`): referencial do robô no chão, sob a câmera,
  `x` à frente e `y` à esquerda, em metros. Não colide com o `markings_relative` que o `soccer_ipm` vai publicar.
* `intersections`: `center` (distância/ângulo do pipeline), `num_rays`, `rays` (os `heading_rays`
  levados ao chão como vetores unitários; vazio quando só o YOLO viu o cruzamento) e `confidence`.
* `segments`: extremos projetados. Elipses não são projetadas.
* Modelo da câmera: o `camera_info` (intrínsecos) + `camera.altura_m` e `camera.pitch_rad`
  (pitch positivo = câmera para baixo). Sem `camera_info`, vale `camera.modelo` do `params.yaml`
  (`fov` ou `edrom` com os `.npy`).

## Como rodar

```bash
pip install -r requirements.txt      # + onnxruntime se for usar modelo .onnx sem ultralytics
cd visao-cbr26
colcon build
source install/setup.bash

# robô real (usb_cam + visão), com a calibração de cor de object_finder/config/
ros2 launch object_finder vision.launch.py
# com projeção própria
ros2 launch object_finder vision.launch.py \
    publish_projection:=True camera_altura_m:=0.45 camera_pitch_rad:=0.3
# simulação (Webots/AUREA): mesmo argumento da branch diego
ros2 launch object_finder vision.launch.py simulacao:=true [start_webots:=True]
```

Argumentos do launch: `video_device`, `camera_name`, `camera_info_url`, `simulacao`,
`start_webots`, `calib_dir` (padrão: `config/`), `model_path`
(`.pt`/`.onnx`), `use_yolo`, `img_output` (janela OpenCV), `publish_debug_image`,
`processing_fps` (taxa máxima; 0 = todos os frames), `params_file`, `publish_projection`,
`camera_altura_m`, `camera_pitch_rad`. Liste com `ros2 launch object_finder vision.launch.py --show-args`.

Limiares do pipeline: `object_finder/config/params.yaml` (todas as chaves com os valores padrão;
`params_file:=` aponta para outro arquivo).

### Sem ROS

```bash
ros2 run object_finder line_vision --camera 0      # janela ao vivo (calibração de config/; --calib troca)
ros2 run object_finder line_vision --image foto.png pasta/ --sem-janela --saida out/   # overlays + JSON
ros2 run object_finder line_vision --video jogo.mp4 --sem-yolo
```
(ou `python3 -m object_finder ...` a partir de `visao-cbr26/src/edrom_vision/object_finder`).

## Calibração de cor

A etapa 1 precisa saber o verde do carpete (`green_pixels.csv`, LUT exata) e o branco das linhas
(`white_pixels.csv`, limiar média ± 2 desvios). A calibração fica em
**`object_finder/config/`** (`green_pixels.csv`, `white_pixels.csv`, `calib.json`) e é a que o
`vision.launch.py` usa. Ela começa com os valores do Webots (cópia de `calib/padrao_webots`, que fica
como referência); no campo real, calibre antes do jogo.

**Calibrador OpenCV**:

```bash
ros2 run object_finder calibrador          # sobe o usb_cam junto (feche o vision.launch antes)
```

Recalibração rápida: **R**, clique no carpete verde, clique no meio de uma linha branca, confira o
painel (`campo SIM`; amarelo = fronteira, vermelho = esqueleto, magenta = branco) e **S** para salvar.
Salvar **sobrescreve** a calibração em `config/` (no `src/`, que vai para o git, e no `install/`, que
o nó lê): o próximo `ros2 launch` já usa a nova, sem recompilar. O calibrador começa da calibração
atual do `config/`. Outras fontes de imagem (não sobem o `usb_cam`):

```bash
ros2 run object_finder calibrador --camera 0 --largura 640 --altura 480
ros2 run object_finder calibrador --ros-topico /AUREA/camera_optical_frame/image_color   # simulação
ros2 run object_finder calibrador --imagens ~/frames
```

`--saida ~/calibracoes` guarda também um histórico datado (`calib_<data>/` + `ultima/`);
`--sem-config` grava só nele. **H** mostra todas as teclas
(**G**/**B** pintar verde/branco, **A** ajusta o branco da borda, **F** congela, **V** troca a vista,
**U** desfaz...). Para conferir uma calibração sem janela:
`ros2 run object_finder calibrador --avaliar --calib visao-cbr26/src/edrom_vision/object_finder/config --imagens ~/frames --relatorio conferencia/`.

**Calibrador HTML** (sem câmera no computador, offline): capture frames onde a câmera funciona

```bash
ros2 run object_finder capture_frames --camera 0 -n 20 -t 1.0 --saida frames      # OpenCV
ros2 run object_finder capture_frames_ros --topico /camera/image_raw -n 20 -t 1.0 --saida frames
```

abra `object_finder/object_finder/calibration/calibrador.html` no navegador, siga as mesmas teclas e
importe o JSON baixado (sobrescreve a calibração em `config/`, como o calibrador OpenCV):

```bash
ros2 run object_finder importar_calibracao ~/Downloads/calib_<data>.json
```

O HTML é gerado por `object_finder/tools/html/build_html.py` (a partir de `calibrador_core.js` e
`calibrador_template.html`); `tools/html/test_core_node.py <pasta>` confere o núcleo JS contra o OpenCV
(precisa do `node`).

Para usar outra pasta (ex.: um histórico): `calib_dir:=~/calibracoes/ultima` (launch) ou `--calib` (sem ROS).

## Avaliação (`object_finder/tools/`)

| Script | Uso |
|---|---|
| `avaliar_sintetico.py -n 40 --seed 7 --saida out/` | métricas no campo sintético (`--variantes` com perturbações) |
| `avaliar_gt.py --kit <kit_visao> --saida out/` | métricas contra o ground truth do kit |
| `validar_calibracao.py --kit <kit_visao> --seg <seg> --saida out/` | valida a calibração (Webots, fotos reais, perturbações) |
| `medir_fps.py --kit <kit_visao>` | tempo por frame |

## Testes

```bash
cd visao-cbr26/src/edrom_vision/object_finder
python3 -m pytest test        # inclui o nó ROS com rclpy simulado e os linters do ament
```
