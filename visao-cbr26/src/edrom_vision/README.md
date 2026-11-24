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
| `soccer_interfaces` | Só as mensagens usadas: `soccer_vision_2d_msgs` e `soccer_vision_attribute_msgs` |

## Instalar e compilar

```bash
pip install -r requirements.txt          # YOLO26 precisa da ultralytics 8.4+
sudo apt install ros-humble-usb-cam ros-humble-vision-msgs ros-humble-cv-bridge
source /opt/ros/humble/setup.bash        # obrigatório em todo terminal novo (senão: "ament_cmake" não encontrado)
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
| `model_path` | `modelo/yolov26n-edrom.pt` | outro `.pt` ou uma pasta `*_openvino_model` |
| `classic_seg` | `true` | `false` desliga campo/borda/linhas (só detecção) |

Os demais parâmetros do nó (`imgsz`, `conf`, `iou`, `device`, `seg_width`, Hough das linhas...) ficam em
`src/edrom_vision/yoeo_vision/config/yoeo_vision.yaml`. A configuração da câmera (dispositivo, resolução,
formato) fica em `config/usb_cam.yaml`. Para descobrir o dispositivo: `v4l2-ctl --list-devices`. Use o
primeiro `/dev/videoN` da câmera, porque o segundo é só de metadados.

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
