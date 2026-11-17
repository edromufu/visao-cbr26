# Calibração da câmera

## Como rodar

1. Em `src/edrom_vision/object_finder/config/usb_cam.yaml`, coloque o nome da câmera em `camera_name` (`verri` ou `milare`).
2. Feche o `vision.launch`, se estiver rodando (a câmera não pode estar em uso).
3. Rode:

```bash
ros2 run camera_calibrator camera_calibrator --size 8x6 --square 0.025
```

O script inicia o `usb_cam` e abre o calibrador. Na janela:

1. Mova o tabuleiro pela imagem (cantos, perto, longe e inclinado) até as barras **X**, **Y**, **Size** e **Skew** ficarem verdes.
2. Clique em **CALIBRATE** e espere (a janela congela durante o cálculo).
3. Clique em **SAVE**.
4. Aperte **q** na janela para sair.

O resultado é salvo em `src/edrom_vision/object_finder/config/<camera_name>_camera-info.yaml`.

Depois de calibrar, rode `colcon build --packages-select object_finder` para instalar o arquivo novo. O `vision.launch` também lê o `usb_cam.yaml` (nome, dispositivo, resolução, formato), então usa a mesma câmera da calibração. Para trocar sem editar o arquivo:

```bash
ros2 launch object_finder vision.launch.py camera_name:=milare
```

## Parâmetros

| Parâmetro | O que é |
|---|---|
| `--size 8x6` | Número de **cantos internos** do tabuleiro (colunas x linhas). Um tabuleiro de 9×7 quadrados tem 8×6 cantos internos. |
| `--square 0.025` | Lado de um quadrado do tabuleiro, em **metros** (0.025 = 25 mm). Meça depois de imprimir. |

As configurações da câmera (nome, dispositivo, resolução, formato) ficam em `src/edrom_vision/object_finder/config/usb_cam.yaml`.

## Observação

A calibração só vale para a resolução e o foco usados. Como o `vision.launch` e o calibrador usam o mesmo `usb_cam.yaml`, a resolução é sempre a mesma; se mudar a resolução, calibre de novo.