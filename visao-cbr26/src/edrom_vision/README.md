# visao-cbr26 — branch yoeo_ros2

> Os comandos abaixo partem da pasta `visao-cbr26/` (a que contém `src/` e `requirements.txt`).

Visão da EDROM para a CBR 2026 (ROS 2 Humble) com o pipeline híbrido do `yoeopth`:

- **Detecção**: YOLO26n da Ultralytics (`modelo/yolov26n-edrom.pt`): bola, trave, robô e intersecções L/T/X.
- **Segmentação clássica** (`field_seg.py`, OpenCV, ~5 ms em CPU): campo, borda do campo e linhas do campo,
  sem rede neural. A cor do campo é calibrada sozinha a cada poucos frames (pico do histograma de matiz na
  parte de baixo da imagem), sem tabela de cor para ajustar à mão.

A câmera vem do `usb_cam` e as saídas usam só as mensagens do `soccer_interfaces`.

## Pacotes (`src/edrom_vision/`)

| Pacote | O que faz |
|---|---|
| `yoeo_vision` | Nó `vision`: YOLO26n + segmentação clássica; publica tudo em `soccer_vision_2d_msgs` |
| `soccer_interfaces` | Mensagens (`soccer_vision_2d_msgs`, `soccer_vision_3d_msgs`, etc.) |

## Instalar e compilar

```bash
pip install -r requirements.txt          # YOLO26 precisa da ultralytics 8.4+
sudo apt install ros-humble-usb-cam ros-humble-vision-msgs ros-humble-cv-bridge
colcon build --symlink-install
source install/setup.bash
```

## Rodar

```bash
ros2 launch yoeo_vision vision.launch.py
```

Sobe o `usb_cam` (namespace `camera`) e o nó `vision`. Argumentos úteis:

| Argumento | Padrão | Para quê |
|---|---|---|
| `video_device` | do `usb_cam.yaml` | ex.: `video_device:=/dev/video0` |
| `camera_name` | do `usb_cam.yaml` | escolhe `config/<nome>_camera-info.yaml` (calibração intrínseca) |
| `rotate_180` | do `usb_cam.yaml` | câmera de cabeça para baixo (ver abaixo) |
| `model_path` | `modelo/yolov26n-edrom.pt` | outro `.pt` ou uma pasta `*_openvino_model` |
| `classic_seg` | `true` | `false` desliga campo/borda/linhas (só detecção) |
| `wb_file` | vazio | balanço de branco fixo (ver abaixo) |
| `show_window` | `false` | janela do OpenCV com o overlay (precisa de monitor) |

Os demais parâmetros do nó (`imgsz`, `conf`, `iou`, `device`, `seg_width`, Hough das linhas...) ficam em
`src/edrom_vision/yoeo_vision/config/yoeo_vision.yaml`. A configuração da câmera (dispositivo, resolução,
formato) fica em `config/usb_cam.yaml`. Para descobrir o dispositivo: `v4l2-ctl --list-devices`. Use o
primeiro `/dev/videoN` da câmera, porque o segundo é só de metadados.

**A imagem é girada 180° antes da visão** (`rotate_180: true` em `config/usb_cam.yaml`), porque no robô a
câmera fica de cabeça para baixo. O YOLO e a segmentação veem a imagem em pé, mas **todas as saídas estão nas
coordenadas da imagem original da câmera** (referencial do `camera_info`). Testando com a câmera na mão, use
`rotate_180:=False`.

## Tópicos publicados

Todas as coordenadas são em pixels, com o `header` da imagem da câmera.

| Tópico | Tipo | Conteúdo |
|---|---|---|
| `balls_in_image` | `soccer_vision_2d_msgs/BallArray` | bolas (`center` + `bb`) |
| `goal_posts_in_image` | `soccer_vision_2d_msgs/GoalpostArray` | traves (`bb`) |
| `robots_in_image` | `soccer_vision_2d_msgs/RobotArray` | robôs (`bb`) |
| `markings_in_image` | `soccer_vision_2d_msgs/MarkingArray` | `intersections` (L/T/X do YOLO, `num_rays` 2/3/4) e `segments` (linhas do campo, HoughLinesP sobre a máscara da segmentação) |
| `field_boundary_in_image` | `soccer_vision_2d_msgs/FieldBoundary` | polígono convexo da borda do campo (`confidence` 0 quando não acha campo) |
| `vision/debug_image` | `sensor_msgs/Image` | overlay: campo (verde), linhas (azul), borda (magenta), segmentos (vermelho) e caixas; só é desenhado se alguém assinar |

Para ver o overlay de outro PC na mesma rede (com o mesmo `ROS_DOMAIN_ID`):

```bash
ros2 run rqt_image_view rqt_image_view /vision/debug_image
```

## Desempenho

O nó loga a cada 150 frames o tempo médio de detecção, segmentação e total (`print_every` no
`yoeo_vision.yaml`). Em CPU, exportar o modelo para OpenVINO deixa a detecção bem mais rápida:

```bash
yolo export model=src/edrom_vision/yoeo_vision/modelo/yolov26n-edrom.pt format=openvino imgsz=416
ros2 launch yoeo_vision vision.launch.py \
    model_path:=$PWD/src/edrom_vision/yoeo_vision/modelo/yolov26n-edrom_openvino_model
```

## Balanço de branco (opcional)

Para câmeras com cor ruim (imagem roxa/esverdeada mesmo com o white balance da câmera ajustado). Com o launch
rodando, segure uma folha branca/cinza cobrindo o **centro** da imagem e, em outro terminal:

```bash
ros2 run yoeo_vision wb_calib --ros-args -p out:=$HOME/wb_gains.json
ros2 launch yoeo_vision vision.launch.py wb_file:=$HOME/wb_gains.json
```

O `wb_calib` também salva `wb_gains_check.jpg` (antes | depois).

## Testar a segmentação em fotos

```bash
ros2 run yoeo_vision field_seg foto1.png foto2.png    # salva foto1_seg.png com o mosaico de depuração
```
