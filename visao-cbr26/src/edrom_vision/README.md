# visao-cbr26 — branch giovanna

Visão por **estrutura de linhas** (Schulz et al., *Line Structure-based Localization for Soccer Robots*, 2009)
junto com o YOLO, no pacote `object_finder`. Câmera pelo `usb_cam`.

> Os comandos partem da pasta `visao-cbr26/` (a que contém `src/` e `requirements.txt`).

## Rodar

```bash
pip install -r requirements.txt
rm -rf build install log                 # sempre que trocar de branch
colcon build --symlink-install && source install/setup.bash

ros2 launch object_finder vision.launch.py video_device:=/dev/video2   # câmera USB (padrão: /dev/video0)
ros2 launch object_finder vision.launch.py simulacao:=true rotate_180:=false   # Webots
```

**A imagem é girada 180° antes da visão** (`rotate_180: true` em `object_finder/config/usb_cam.yaml`), porque no
robô a câmera fica de cabeça para baixo. O pipeline, a janela e o `processed_image_topic` usam a imagem em pé (o
`camera_info` também é girado para a projeção própria); os tópicos `*_in_image` (inclusive fronteira, segmentos,
elipses e `heading_rays`) saem nas coordenadas da imagem original da câmera, que é o referencial do `camera_info`
usado pelo IPM. Com a câmera em pé ou no Webots, use `rotate_180:=false`.

Para descobrir a câmera: `v4l2-ctl --list-devices` (use o primeiro `/dev/videoN` dela).
Todos os argumentos: `ros2 launch object_finder vision.launch.py --show-args`.

## Calibração de cor

O verde do campo e o branco das linhas ficam em `object_finder/config/`. O padrão vem do Webots,
então **calibre no campo real antes do jogo**. Feche o `vision.launch` antes, porque a câmera só abre
em um programa por vez.

```bash
ros2 run object_finder calibrador --video-device /dev/video2
```

Na janela: **R**, clique no verde, clique numa linha branca, confira e aperte **S**. **H** mostra as
outras teclas.

Ao salvar, o calibrador **reescreve** `green_pixels.csv`, `white_pixels.csv` e `calib.json` em
`config/`, tanto no `src/` quanto no `install/`. Não precisa recompilar, mas **reinicie o launch**:
o nó só lê a calibração ao iniciar. A calibração anterior é substituída. Para voltar ao padrão:
`git checkout -- src/edrom_vision/object_finder/config/`.

Sem câmera no computador: grave fotos com
`ros2 run object_finder capture_frames --camera 2 -n 20 --saida frames`. Depois calibre com
`calibrador --imagens frames/`, ou abra `object_finder/calibration/calibrador.html` no navegador e
importe o JSON com `ros2 run object_finder importar_calibracao calib_<data>.json`.

**Verde dinâmico** (como no artigo dos Bit-Bots, Seção 3.1): com a visão rodando, o nó aprende sozinho os
tons de verde que estão cercados de campo e abaixo da fronteira, e assim acompanha sombra e mudanças de luz.
Cores que aparecem acima da fronteira nunca entram, e uma cor que some é esquecida depois de 10 atualizações.
O aprendido se soma à calibração e **não altera os arquivos** do `config/`. Vem ligado. Para desligar ou
ajustar, use `verde_dinamico:` em `config/params.yaml`. A imagem de debug mostra quantas cores foram aprendidas.

## Sem ROS

```bash
ros2 run object_finder line_vision --camera 2
ros2 run object_finder line_vision --image foto.png --sem-janela --saida out/
```

## Funcionalidades a mais que a `ivan`

Caminhos dentro de `src/edrom_vision/object_finder/object_finder/`.

| Funcionalidade | Onde |
|---|---|
| Fronteira do campo e esqueleto das linhas (código original do artigo) | `vendor/`, `stage1_adapter.py` |
| Nós e conexões sobre o esqueleto | `graph_nodes.py` |
| Cruzamentos L/T/X com a direção dos braços | `crossings.py` |
| Linhas retas e elipse do círculo central | `lines.py` |
| Fusão com o YOLO: rejeita fora do campo, confirma cruzamentos | `fusion.py` |
| YOLO `.pt`, `.onnx` ou sem YOLO (`use_yolo:=false`) | `detector.py` |
| Projeção ao chão própria (`publish_projection:=True`) | `camera_model.py` |
| Todos os limiares num YAML | `params.py`, `../config/params.yaml` |
| Imagem de debug (fronteira, esqueleto, linhas, cruzamentos, YOLO, FPS) | `overlay.py` |
| Modo sem ROS (`line_vision`) | `__main__.py`, `pipeline.py` |
| Calibração de cor (OpenCV, HTML, captura de fotos, importação) | `calibration/` |
| Verde dinâmico: aprende o verde com a visão rodando (artigo Bit-Bots) | `dynamic_color.py` |
| Simulação no Webots (`simulacao:=true`) | `../launch/vision.launch.py` |
| Campo sintético e métricas | `synthetic.py`, `evaluation.py`, `../tools/` |

Tópicos publicados: `balls_in_image`, `goal_posts_in_image`, `robots_in_image`, `markings_in_image`,
`field_boundary_in_image` e `processed_image_topic` (imagem de debug).

## Testes

```bash
cd src/edrom_vision/object_finder && python3 -m pytest test
```
