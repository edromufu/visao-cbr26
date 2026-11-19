# Guia de Testes na Sede — Pipeline de Visão 2D + ROS

Este guia descreve o passo a passo para executar e validar o fluxo de **Segmentação + Detecção + Publicação ROS 2D** no robô real, sem depender dos nós de projeção geométrica (`ipm` / `soccer_ipm`) ou da árvore de transformações (`/tf`).

---

## 1. Identificar o ID da câmera USB

Conecte a câmera no computador do robô e liste os dispositivos de vídeo disponíveis no sistema:

```bash
ls -l /dev/video*
```

> **Dica:** Se aparecerem múltiplos dispositivos para a mesma câmera (ex.: `/dev/video0` e `/dev/video1`), utilize sempre o **primeiro índice** (menor número), pois o segundo normalmente corresponde apenas a metadados e não fornece stream de imagem.

---

## 2. Configurar `real.launch.py` e parâmetros

Verifique o arquivo de inicialização real para garantir que o ID da câmera está correto e que o nó do IPM não está sendo iniciado junto:

```bash
cat ~/ws_visao/src/robocup_line_vision/launch/real.launch.py
```

1. Ajuste o parâmetro do ID da câmera no `real.launch.py` ou em `robocup_line_vision/config/params.yaml`.
2. Caso exista alguma chamada para `soccer_ipm` ou `ipm_image_node` dentro do `real.launch.py`, comente-a para isolar apenas a visão 2D.

---

## 3. Compilar e carregar o workspace

Compile apenas os pacotes necessários para este fluxo (ignorando `ipm` e `soccer_ipm`):

```bash
cd ~/ws_visao
colcon build --symlink-install --packages-select edrom_msgs soccer_interfaces robocup_line_vision
source install/setup.bash
```

---

## 4. Executar o pipeline de visão

Inicie o launch file configurado para o hardware real:

```bash
ros2 launch robocup_line_vision real.launch.py
```

*(Opcional)* Caso queira rodar o nó diretamente sem o launch file, carregando os parâmetros manualmente:
```bash
ros2 run robocup_line_vision line_vision_node --ros-args --params-file ~/ws_visao/src/robocup_line_vision/config/params.yaml
```

---

## 5. Calibrar as cores para a iluminação da sede (se necessário)

Os limiares padrão do repositório (`calib/padrao_webots/`) foram ajustados para o simulador. Se a iluminação da sede comprometer a segmentação do gramado (verde) ou das linhas (branco):

1. Em um segundo terminal (`source ~/ws_visao/install/setup.bash`), capture frames reais publicados pela câmera:
   ```bash
   ros2 run robocup_line_vision capture_frames_ros
   ```
2. Abra o calibrador visual para ajustar as faixas de cor:
   ```bash
   python3 ~/ws_visao/src/robocup_line_vision/robocup_line_vision/calibration/calibrator_cv.py
   ```
3. Salve os novos valores em `config/params.yaml` e reinicie o `real.launch.py`.

---

## 6. Validar tópicos ROS, taxa de FPS e imagem de debug

Com o nó rodando, abra outro terminal (`source ~/ws_visao/install/setup.bash`) e execute as verificações abaixo:

```bash
# 1. Conferir os tópicos publicados pela visão
ros2 topic list

# 2. Verificar a frequência real (FPS) no hardware do robô
ros2 topic hz /vision_data

# 3. Inspecionar as detecções (bola, gol, linhas e cruzamentos) em pixels
ros2 topic echo /vision_data

# 4. Abrir a visualização com overlay (segmentação + bounding boxes + linhas)
ros2 run rqt_image_view rqt_image_view
```

> **Nota:** Caso o tópico principal configurado no `params.yaml` tenha outro nome (ex.: `/detections` ou `/markings`), substitua `/vision_data` pelo nome exibido no `ros2 topic list`.