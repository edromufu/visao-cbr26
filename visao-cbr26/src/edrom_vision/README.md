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

## Funcionalidades a mais que a `ivan`

Caminhos dentro de `src/edrom_vision/object_finder/`.

| Funcionalidade | Onde |
|---|---|
| Segmentação por cor (sem ROS): fronteira do campo, obstáculos (vermelho, azul, branco) e pontos das linhas | `object_finder/pipeline/` |
| Validação do YOLO: bola, trave e robô só valem com a base no campo; interseções precisam de linha branca | `object_finder/detection_validator.py` |
| Obstáculos: o que a segmentação vê e o YOLO não explicou | `object_finder/pipeline/main_pipeline.py` |
| Imagem de debug: campo, fronteira, obstáculos e detecções (verde = válida, vermelho = rejeitada) | `object_finder/vision_debug.py` |
| Parâmetros mudáveis com a visão rodando (`ros2 param set /vision ...`) | `config/vision_params.yaml` |
| Escolha dos pesos (`model_file:=`); o nó recusa modelo com outras classes | `object_finder/running_inference.py` |
| Calibração de cor (`calibrar`) | `object_finder/pipeline/calibrate.py` |
| Simulação no Webots (`simulacao:=true`) e TF da câmera (`publish_tf:=true`) | `launch/vision.launch.py` |
| Segmentação sem ROS (`segmentar`), comparar e treinar modelos | `object_finder/pipeline/`, `object_finder/tools/` |
| `robot.sh`: `setup`, `build`, `calibrate` e `run` | raiz do repositório |

Tópicos publicados: `balls_in_image`, `goal_posts_in_image`, `robots_in_image`, `markings_in_image`,
`field_boundary_in_image`, `obstacles_in_image` e `processed_image_topic` (imagem de debug).

O `config/verri_camera-info.yaml` é provisório: gere o real com o `camera_calibrator` da branch `ivan`.

## Testes

```bash
cd src/edrom_vision/object_finder && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest test
```
