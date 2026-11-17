# robocup_line_vision

Visão por **estrutura de linhas** + **YOLO** para a EDROM (RoboCup Humanoid
KidSize). Implementa as Seções III e IV do artigo *"Line Structure-based
Localization for Soccer Robots"* (Schulz, Liu, Stückler, Behnke, Humanoids
2009), usando a fronteira do campo e o esqueleto da etapa 1 (III-A/III-B, em
`vendor/`, sem alterar a lógica), e junta com o detector YOLO da equipe
(`best.pt`).

* Núcleo em Python puro (sem ROS), testado.
* Calibração de cor para fazer na hora, com a câmera real: OpenCV (HighGUI) ou
  HTML offline.
* Modo sem ROS: `python3 -m robocup_line_vision --camera 2`.
* Nó ROS 2 Humble (`ament_python`) que publica nos mesmos tópicos do nó
  `finder` (`markings_in_image` com `heading_rays`, `field_boundary_in_image`,
  bola/traves/robôs) e, opcionalmente, `edrom_msgs/LandmarkArray`.

Leia primeiro: **`RELATORIO.md`** (o que foi feito, os números e o que não foi
testado). Para o teste na câmera: **`docs/calibracao.md`** e
`../roteiros/04_calibrar_e_rodar_camera_real.md`.

## Uso rápido

```bash
pip3 install numpy scipy pandas pyyaml opencv-python   # + ultralytics (ou onnxruntime) para o YOLO

# 1. calibrar (R, clique no verde, clique na linha, S)
python3 -m robocup_line_vision.calibration.calibrator_cv --camera 2 --saida ~/calibracoes
# 2. rodar sem ROS
python3 -m robocup_line_vision --camera 2 --calib ~/calibracoes/ultima
# 3. ROS 2 (depois do colcon build, roteiro 02)
ros2 launch robocup_line_vision real.launch.py camera_idx:=2 calib_dir:=$HOME/calibracoes/ultima
ros2 launch robocup_line_vision sim.launch.py img_output:=True
```

## Estrutura

```
robocup_line_vision/            pacote ROS (ament_python) — package.xml, setup.py, setup.cfg
  robocup_line_vision/          núcleo Python
    vendor/                     código original (III-A, III-B) + VENDOR.md
    stage1_adapter.py           adaptador da etapa 1 (sem efeito colateral)
    graph_nodes.py              III-C nós e conexões
    crossings.py                IV-A cruzamentos L/T/X (+ extensão por retas)
    lines.py                    IV-B linhas (split-and-merge) e elipse do círculo
    fusion.py, detector.py      fusão com o YOLO (.pt/.onnx)
    camera_model.py             distorção e projeção ao chão
    pipeline.py, params.py      orquestração e parâmetros (config/params.yaml)
    overlay.py, __main__.py     desenho e modo sem ROS
    synthetic.py, evaluation.py campo sintético e métricas
    calibration/                calibrador OpenCV/HTML, captura de frames
    ros/                        nó ROS 2 e conversão de mensagens
  config/params.yaml            todos os limiares
  launch/                       sim.launch.py, real.launch.py
  calib/padrao_webots/          calibração original do Webots
  modelo/                       best.pt (modelo da equipe) e best.onnx (exportado do mesmo)
  docs/                         arquitetura, decisões, calibração, métricas (+ imagens)
  test/                         pytest (88 testes) + linters do ament
  tools/                        validação, avaliação, FPS, núcleo JS do calibrador HTML
```

