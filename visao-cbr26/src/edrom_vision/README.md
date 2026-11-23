# visao-cbr26 — branch ivan

> Os comandos abaixo partem da pasta `visao-cbr26/` (a que contém `src/` e `requirements.txt`).

Visão da EDROM para a CBR 2026 (ROS 2 Humble): câmera pelo `usb_cam`, detecção com YOLO
(`object_finder`) e projeção das detecções no chão com o IPM (`soccer_ipm`).

## Pacotes (`src/`)

| Pacote | O que faz |
|---|---|
| `edrom_vision/object_finder` | Nó `vision`: roda o YOLO (`modelo/best.pt`) e publica as detecções em pixels |
| `edrom_vision/soccer_ipm` | Leva as detecções de pixels para metros, no referencial do robô |
| `edrom_vision/ipm` | Biblioteca e serviços de IPM usados pelo `soccer_ipm` |
| `edrom_vision/soccer_interfaces` | Mensagens (`soccer_vision_2d_msgs`, `soccer_vision_3d_msgs`, etc.) |
| `edrom_utils/camera_calibrator` | Calibração intrínseca da câmera e medição de desempenho (ver o README do pacote) |
| `edrom_utils/ipm_calibrator` | `aruco_record`: grava os ArUcos detectados por frame |

## Instalar e compilar

```bash
pip install -r requirements.txt
sudo apt install ros-humble-usb-cam
colcon build --symlink-install
source install/setup.bash
```

## Rodar

```bash
ros2 launch object_finder vision.launch.py
```

Com outra câmera (ex.: câmera USB em `/dev/video2`) ou outra calibração (padrão: `milare`):

```bash
ros2 launch object_finder vision.launch.py video_device:=/dev/video2 camera_name:=verri
```

**A imagem é girada 180° antes do YOLO** (`image_rotation`, padrão `180`), porque no robô a câmera
fica de cabeça para baixo. Testando com a câmera na mão, ou em pé, use `image_rotation:=0`.

A configuração da câmera (dispositivo, resolução, formato) fica em
`src/edrom_vision/object_finder/config/usb_cam.yaml`. Para descobrir o dispositivo:
`v4l2-ctl --list-devices`. Use o primeiro `/dev/videoN` da câmera, porque o segundo é só de metadados.

## Calibração

```bash
ros2 run camera_calibrator camera_calibrator --size 8x6 --square 0.025   # intrínseca (--rotation 0: câmera em pé)
ros2 launch ipm_calibrator aruco_record.launch.py                         # ArUcos para o IPM
```

## Desempenho

Com o `vision.launch` rodando, em outro terminal:

```bash
ros2 run camera_calibrator desempenho      # fps da câmera, YOLO e IPM, latência e CPU a cada 5 s
```

**Ctrl+C** mostra o resumo da sessão inteira.
