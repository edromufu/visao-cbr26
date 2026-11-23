# visao-cbr26 — branch yoeo_ipm (YOEO + IPM)

> Os comandos abaixo partem da pasta `visao-cbr26/` (a que contém `src/` e `requirements.txt`).

Visão da EDROM para a CBR 2026 (ROS 2 Humble): câmera pelo `usb_cam`, detecção + segmentação com o YOEO-26n
em OpenVINO e um IPM próprio que leva as detecções e as linhas para o chão. O IPM calcula a pose da câmera
sozinho, sem precisar de TF: por medidas fixas do robô ou pela cadeia cinemática (URDF + `/joint_states`).

## Pacotes (`src/`)

| Pacote | O que faz |
|---|---|
| `edrom_vision/object_finder` | Nó `vision` (YOEO-26n, `modelo/yoeo26n.xml`) e nó `yoeo_ipm` (pixels → metros em `base_footprint`) |
| `edrom_vision/soccer_interfaces` | Mensagens (`soccer_vision_2d_msgs`, `soccer_vision_3d_msgs`, etc.) |

## Instalar e compilar

```bash
pip install -r requirements.txt
sudo apt install ros-humble-usb-cam
colcon build --symlink-install
source install/setup.bash
```

## Rodar

O passo a passo completo de teste está em `src/edrom_vision/object_finder/GUIA_DE_TESTE.pdf`.

### Modo fixed (padrão, sem URDF)
A pose é: chão → eixo do tilt a `tilt_axis_height` → corpo inclinado `body_pitch` → gira `pan` → gira `tilt`
→ `camera_offset` até a lente. Meça no robô, **na pose de caminhada**:
- `tilt_axis_height`: altura do eixo do servo de tilt da cabeça até o chão, em m
- `camera_offset`: do eixo do tilt até a lente, `[x frente, y esquerda, z cima]` em m, com a cabeça reta
- `body_pitch`: inclinação do corpo para frente, em rad (também corrige erro no zero do tilt)
- `pan`/`tilt` (rad; tilt positivo olha para baixo) se a cabeça ficar parada, ou os nomes das juntas em
  `pan_joint`/`tilt_joint` se vierem de `/joint_states`

```bash
ros2 launch object_finder vision.launch.py use_joint_states:=False tilt:=0.52 \
    tilt_axis_height:=0.49 "camera_offset:=[0.05, 0.0, 0.02]"
```
Confira no cabeçalho da vista de cima: `cam h` deve bater com a altura medida da lente.

### Modo kinematics (URDF do robô)
```bash
ros2 launch object_finder vision.launch.py pose_source:=kinematics urdf_path:=/caminho/robo.urdf \
    torso_link:=base_link camera_link:=head_tilt_link \
    left_foot_link:=l_ank_roll_link right_foot_link:=r_ank_roll_link \
    "sole_offset_left:=[0.0, 0.0, -0.03]" "sole_offset_right:=[0.0, 0.0, -0.03]" \
    "camera_offset:=[0.05, 0.0, 0.02]" rviz:=True
```
- `camera_link`: link em que a câmera está presa (normalmente o do tilt); `camera_offset` vai dele até a lente.
- `left/right_foot_link`: último link de cada perna; `sole_offset_*` vai dele até o centro da sola.
- Os nomes de junta em `/joint_states` precisam ser os do URDF, com os mesmos sinais.
- Se algum link não existir, o nó para e lista os links disponíveis no URDF.

### Outros argumentos
Câmera: `video_device`, `camera_name` (padrão `milare`, escolhe `config/<camera_name>_camera-info.yaml`),
`sim_mode` (Webots: lê `/camera/image`, sem usb_cam). YOEO: `device` (CPU/GPU), `threads`, `model_path`,
`img_output`, `debug_image`, `conf_ball`, `conf_goalpost`, `conf_robot`, `conf_intersection`. IPM: `fov`, `show`.

A configuração da câmera (dispositivo, resolução, formato) fica em
`src/edrom_vision/object_finder/config/usb_cam.yaml`.

**A imagem é girada 180° antes do YOEO** (`rotate_180: true` no `usb_cam.yaml`), porque no robô a câmera fica de
cabeça para baixo. A janela e o `vision_debug` mostram a imagem em pé; as detecções e a máscara saem nas
coordenadas da imagem original da câmera, que é o referencial do `camera_info` usado pelo IPM. Testando com a
câmera em pé ou no Webots, use `rotate_180:=False`.

## Entradas e saídas
| Tópico | Tipo | |
|---|---|---|
| `/camera/image_raw`, `/camera/camera_info` | do usb_cam | entrada |
| `/joint_states` | `sensor_msgs/JointState` | entrada: pan/tilt (fixed) ou todas as juntas (kinematics) |
| `balls_in_image`, `goal_posts_in_image`, `robots_in_image`, `markings_in_image` | `soccer_vision_2d_msgs` | saída do YOEO, em pixels |
| `/vision/segmentation` | `sensor_msgs/Image` mono8 | máscara do YOEO: 0 fundo, 1 campo, 2 linhas |
| `balls_relative`, `goal_posts_relative`, `robots_relative`, `markings_relative` | `soccer_vision_3d_msgs` | saída do IPM em `base_footprint` |
| `ipm/line_points` | `sensor_msgs/PointCloud2` | linhas da segmentação no chão |
| `ipm/markers`, `ipm/birdseye` | RViz / imagem | depuração |
| TF | | `base_footprint → camera_optical_frame` (e `→ torso_link` no kinematics) |

## Detalhes
- **Intrínseca e distorção** vêm do `camera_info`. A imagem vai crua para o YOEO e o IPM tira a distorção só
  dos pixels projetados. Sem calibração (K zerada) o IPM usa um pinhole pelo `fov` (padrão 1,6 rad) e avisa no log.
- **Trave e robô** usam a base da caixa; são descartados se a base passa de 80% da altura da imagem (pode estar
  cortada), a mesma regra do `soccer_ipm`. A **bola** usa o centro, projetado no plano z = 7 cm.
- **Modo fixed:** supõe que os eixos de pan e tilt se cruzam. Uma distância horizontal de 1–2 cm entre eles
  vira erro da mesma ordem nos pontos; se for maior, some-a no `camera_offset`.
- **Modo kinematics:** o pé de apoio é a sola mais baixa; supõe essa sola plana no chão. A IMU não é usada.
- **Testes:** `python3 -m pytest src/edrom_vision/object_finder/test` (sem ROS; usam `test/robo_teste.urdf`).
- `object_finder/yoeo_infer.py` é uma cópia de `edrom_yoeo/infer.py` do repositório de treino: mantenha os dois iguais.
