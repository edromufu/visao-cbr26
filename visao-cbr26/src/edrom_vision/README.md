# visao-cbr26 — branch diego

Detecção com YOLO (bola, trave, robô, interseções) **validada pela segmentação do campo** (cores HSV), no
pacote `object_finder`. Também publica a fronteira do campo e os obstáculos. Câmera pelo `usb_cam`.

> Os comandos partem da pasta `visao-cbr26/` (a que contém `src/` e `requirements.txt`).

## Rodar

```bash
pip install -r requirements.txt
rm -rf build install log                 # sempre que trocar de branch
colcon build --symlink-install && source install/setup.bash

ros2 launch object_finder vision.launch.py video_device:=/dev/video2   # câmera USB (padrão: /dev/video0)
ros2 launch object_finder vision.launch.py simulacao:=true              # Webots
```

Para descobrir a câmera: `v4l2-ctl --list-devices` (use o primeiro `/dev/videoN` dela).
Outros argumentos: `show_window:=false`, `model_file:=/caminho/pesos.pt`, `params_file:=...`.

## Calibração de cor

Sem calibrar, o verde do campo vem do Webots. **Calibre no campo real antes do jogo.** Feche o
`vision.launch` antes, porque a câmera só abre em um programa por vez.

```bash
ros2 run object_finder calibrar hsv --source /dev/video2
```

Na janela: **1** campo, **2** branco, **3** vermelho, **4** azul. Arraste um retângulo sobre a cor,
**p** mostra o resultado, **s** salva e **q** sai.

O resultado vai para `calibracao/hsv_params.yaml` e **não altera** o `config/`. Para usar:

```bash
ros2 launch object_finder vision.launch.py params_file:=calibracao/hsv_params.yaml
```

O `../robot.sh run` já usa esse arquivo automaticamente se ele existir (`NOCALIB=1` desliga). Com a
visão rodando, também dá para ajustar na hora: `ros2 param set /vision hsv.field_min "[35, 60, 40]"`.

Sem tela no robô: `calibrar snapshot --source /dev/video2` grava uma foto com grade. Depois
`calibrar hsv --source /dev/video2 --sample field=x,y,largura,altura`, com as frações da imagem.

## Sem ROS

```bash
ros2 run object_finder segmentar foto.png          # grava foto_segmentada.png
ros2 run object_finder segmentar 2 --show          # câmera ao vivo
```

## Onde fica cada coisa (`object_finder/`)

| O quê | Onde |
|---|---|
| Nó ROS (`finder`) | `object_finder/connecting_and_showing.py` |
| Segmentação (sem ROS) e calibrador | `object_finder/pipeline/` |
| Validação das detecções | `object_finder/detection_validator.py` |
| Parâmetros | `config/vision_params.yaml` |
| Comparar e treinar modelos | `object_finder/tools/` |

Tópicos publicados: `balls_in_image`, `goal_posts_in_image`, `robots_in_image`, `markings_in_image`,
`field_boundary_in_image`, `obstacles_in_image` e `processed_image_topic` (imagem de debug).

O `config/verri_camera-info.yaml` é provisório: gere o real com o `camera_calibrator` da branch `ivan`.

## Testes

```bash
cd src/edrom_vision/object_finder && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest test
```
