# visao-cbr26 — branch vital (YOEO)

> Os comandos abaixo partem da pasta `visao-cbr26/` (a que contém `src/` e `requirements.txt`).

Visão da EDROM para a CBR 2026 (ROS 2 Humble): câmera pelo `usb_cam` e detecção + segmentação com o
YOEO-26n em OpenVINO (`object_finder`), sem Ultralytics nem PyTorch.

## Pacotes (`src/`)

| Pacote | O que faz |
|---|---|
| `edrom_vision/object_finder` | Nó `vision`: roda o YOEO-26n (`modelo/yoeo26n.xml`) e publica detecções em pixels e a máscara de campo/linhas |
| `edrom_vision/soccer_interfaces` | Mensagens (`soccer_vision_2d_msgs`, `soccer_vision_3d_msgs`, etc.) |

## Instalar e compilar

```bash
pip install -r requirements.txt
sudo apt install ros-humble-usb-cam
colcon build --symlink-install
source install/setup.bash
```

## Rodar

```bash
ros2 launch object_finder vision.launch.py                         # robô real, CPU
ros2 launch object_finder vision.launch.py device:=GPU             # iGPU
ros2 launch object_finder vision.launch.py img_output:=True        # janela com caixas e máscara
ros2 launch object_finder vision.launch.py sim_mode:=True          # Webots: lê /camera/image, sem usb_cam
```

Com outra câmera (ex.: `/dev/video2`) ou outra calibração (padrão: `milare`):

```bash
ros2 launch object_finder vision.launch.py video_device:=/dev/video2 camera_name:=verri
```

Outros argumentos: `model_path`, `threads` (CPU; 0 = automático), `debug_image` (publica `vision_debug`),
`undistort` (padrão `True`) e `conf_ball`, `conf_goalpost`, `conf_robot`, `conf_intersection` (padrão 0,45).

A configuração da câmera (dispositivo, resolução, formato) fica em
`src/edrom_vision/object_finder/config/usb_cam.yaml`, e a calibração em `config/<camera_name>_camera-info.yaml`.
Para descobrir o dispositivo: `v4l2-ctl --list-devices` (use o primeiro `/dev/videoN` da câmera).

## O que publica

| Tópico | Tipo | Conteúdo |
|---|---|---|
| `balls_in_image`, `goal_posts_in_image`, `robots_in_image` | `soccer_vision_2d_msgs` | caixas em pixels, com a confiança |
| `markings_in_image` | `soccer_vision_2d_msgs/MarkingArray` | cruzamentos L/T/X (`num_rays` 2/3/4); só o centro tem sentido |
| `/vision/segmentation` | `sensor_msgs/Image` `mono8` | máscara a 1/4 da entrada da rede, só a área do frame: 0 fundo, 1 campo, 2 linhas |
| `vision_debug` | `sensor_msgs/Image` `bgr8` | caixas + máscara, só com `debug_image:=True` |

Todas com o header da imagem da câmera. Com `undistort:=True` e calibração no `camera_info`, a imagem é corrigida
da distorção antes da rede e os pixels publicados já são sem distorção.

O nó registra a latência p50/p95 a cada 300 frames. `object_finder/yoeo_infer.py` é uma cópia de
`edrom_yoeo/infer.py` do repositório de treino: mantenha os dois iguais.
