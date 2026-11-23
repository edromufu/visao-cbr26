# visao-cbr26 — branch diego

> Os comandos abaixo partem da raiz do repositório (a pasta que contém `requirements.txt`).

Mesma estrutura, mensagens (`soccer_interfaces`), câmera (`usb_cam`), tópicos e launch da branch `ivan`
(base: detecção com YOLO), com a **validação das detecções pela segmentação do campo (HSV)**.

## Teste rápido

```bash
pip install -r requirements.txt
cd visao-cbr26 && colcon build --symlink-install && source install/setup.bash
ros2 launch object_finder vision.launch.py video_device:=/dev/video2   # câmera USB (padrão: /dev/video0)
ros2 launch object_finder vision.launch.py simulacao:=true              # ou no Webots
```

Para descobrir o dispositivo da câmera: `v4l2-ctl --list-devices`. Use o primeiro `/dev/videoN` da câmera, porque o segundo é só de metadados.

## Funcionalidades a mais que a `ivan`

Tudo fica em `visao-cbr26/src/edrom_vision/object_finder/`.

- **Segmentação por cor** (`object_finder/pipeline/`, não depende de ROS): fronteira do campo (varredura de cima
  para baixo ou, com a câmera inclinada para cima, de baixo para cima), obstáculos classificados por cor
  (vermelho, azul, branco) e pontos das linhas. A imagem pode ser reduzida antes (`pipeline.process_width`).
- **Validação das detecções do YOLO**: bola, trave e robô só valem se a base da caixa estiver no campo;
  interseções L/T/X precisam do centro no campo e de linha branca na caixa; o travessão é ignorado. Motivos de
  rejeição: `no_field`, `outside_field`, `no_marking`, `ignored_class`. Pode ser desligada (`validation.enabled`).
- **Obstáculos**: o que a segmentação vê e o YOLO não explicou como bola, trave ou robô.
- **Imagem de debug**: campo em azul claro, fronteira, obstáculos e detecções (verde = válida, vermelho =
  rejeitada com o motivo). Vai para a janela (`show_window`) e para o tópico `processed_image_topic`.
- **Parâmetros em tempo de execução**: tudo em `config/vision_params.yaml` pode ser mudado com
  `ros2 param set /vision ...` (valores inválidos são recusados).
- **Escolha dos pesos**: `model_file:=` (nome em `modelo/` ou caminho absoluto); o nó recusa um modelo com outro
  esquema de classes (`strict_class_check`).
- **Calibração do verde**: a faixa do campo sai de `config/green_pixels.csv` (percentis 1 e 99 + margem), ou é
  fixada no YAML (`hsv.field_min`, `hsv.field_max`, etc.).
- **Simulação no Webots**: `simulacao:=true` usa a câmera do robô AUREA em vez do `usb_cam`.
- **TF da câmera** pelo launch (`publish_tf:=true cam_z:=... cam_pitch:=...`).
- **Ferramentas**: `segmentar` (segmentação sem ROS), `comparar_modelos` (YOLOv8n × YOLO26n: velocidade e
  acurácia) e `treinar_yolo26n`.
- **`robot.sh`**: `setup` (dependências), `build` e `run`.
- **Testes** (pytest) em `object_finder/test/`.

## Tópicos publicados pelo nó `vision`

| Tópico | Mensagem |
|---|---|
| `balls_in_image`, `goal_posts_in_image`, `robots_in_image`, `markings_in_image` | `soccer_vision_2d_msgs` (como na `ivan`) |
| `field_boundary_in_image` | `soccer_vision_2d_msgs/FieldBoundary` |
| `obstacles_in_image` | `soccer_vision_2d_msgs/ObstacleArray` |
| `processed_image_topic` | `sensor_msgs/Image` (debug) |

Os `*_in_image` seguem o formato que o `soccer_ipm` consome. O IPM (pixels → metros) ainda não está nesta
branch; será integrado depois.

## Rodar

```bash
cd visao-cbr26
colcon build && source install/setup.bash
ros2 launch object_finder vision.launch.py                     # robô real (usb_cam)
ros2 launch object_finder vision.launch.py simulacao:=true     # Webots
ros2 launch object_finder vision.launch.py show_window:=false model_file:=/caminho/yolo26n_best.pt
```

Ou, na raiz do repositório: `./robot.sh setup` (uma vez) e `./robot.sh run [argumentos do launch]`.

## Segmentação sem ROS

```bash
segmentar foto.png                          # grava foto_segmentada.png (ou: python3 -m object_finder.pipeline)
segmentar partida.mp4 -o saida.mp4
segmentar 0 --show                          # câmera 0 ao vivo (q para sair)
segmentar foto.png --hsv-csv meu_hsv.csv    # CSV: classe,h_min,h_max,s_min,s_max,v_min,v_max
```

## Testes

```bash
cd visao-cbr26 && colcon build && source install/setup.bash
cd src/edrom_vision/object_finder
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest test
```

## Calibração da câmera

`config/verri_camera-info.yaml` é provisório (valores de exemplo do `usb_cam`). Gere o real com o
`camera_calibrator` da branch `ivan` e substitua.
