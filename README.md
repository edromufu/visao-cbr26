# visao-cbr26 — branch ivan

Visão da EDROM para a CBR 2026 (ROS 2 Humble): câmera pelo `usb_cam`, detecção com YOLO
(`object_finder`) e projeção das detecções no chão com o IPM (`soccer_ipm`).

## Pacotes (`visao-cbr26/src/`)

| Pacote | O que faz |
|---|---|
| `edrom_vision/object_finder` | Nó `vision`: roda o YOLO (`modelo/best.pt`) e publica as detecções em pixels |
| `edrom_vision/soccer_ipm` | Leva as detecções de pixels para metros, no referencial do robô |
| `edrom_vision/ipm` | Biblioteca e serviços de IPM usados pelo `soccer_ipm` |
| `edrom_vision/soccer_interfaces` | Mensagens (`soccer_vision_2d_msgs`, `soccer_vision_3d_msgs`, etc.) |
| `edrom_utils/camera_calibrator` | Calibração intrínseca da câmera (ver o README do pacote) |
| `edrom_utils/ipm_calibrator` | `aruco_record`: grava os ArUcos detectados por frame |

## Instalar e compilar

```bash
pip install -r requirements.txt
sudo apt install ros-humble-usb-cam
cd visao-cbr26
colcon build --symlink-install
source install/setup.bash
```

## Rodar

```bash
ros2 launch object_finder vision.launch.py
```

Com outra câmera (ex.: câmera USB em `/dev/video2`) ou outra calibração:

```bash
ros2 launch object_finder vision.launch.py video_device:=/dev/video2 camera_name:=milare
```

A configuração da câmera (dispositivo, resolução, formato) fica em
`src/edrom_vision/object_finder/config/usb_cam.yaml`. Para descobrir o dispositivo:
`v4l2-ctl --list-devices`. Use o primeiro `/dev/videoN` da câmera, porque o segundo é só de metadados.

## Calibração

```bash
ros2 run camera_calibrator camera_calibrator --size 8x6 --square 0.025   # intrínseca
ros2 launch ipm_calibrator aruco_record.launch.py                         # ArUcos para o IPM
```
