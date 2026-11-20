# Calibração de cor (verde do campo e branco das linhas)

Calibrador trazido do pacote `robocup_line_vision` (branch `giovanna`). O código
é o mesmo; mudou só o nome do módulo e entrou o
comando `aplicar_calibracao_cores`, que leva o resultado para o nó de visão do
`object_finder`.

## Passo a passo

```bash
# 1. feche o vision.launch (o calibrador abre a câmera direto)
# 2. calibre com a câmera ao vivo (troque 0 pelo índice certo: ls -l /dev/video*)
ros2 run object_finder calibrar_cores --camera 0 --saida ~/calibracoes
#    R -> clique no carpete verde -> clique no meio de uma linha branca -> confira -> S
#    H mostra todas as teclas; ESC ou Q sai

# 3. leve as faixas para o nó de visão e instale
ros2 run object_finder aplicar_calibracao_cores            # usa ~/calibracoes/ultima
colcon build --packages-select object_finder

# 4. rode o vision.launch normalmente: ele carrega config/hsv_calibrado.yaml
ros2 launch object_finder vision.launch.py
```

Para ajustar sem reiniciar o nó (com o `vision.launch` rodando e frames já
salvos em `--imagens`):

```bash
ros2 run object_finder calibrar_cores --imagens ~/calibracoes/ultima/frames --saida ~/calibracoes
ros2 run object_finder aplicar_calibracao_cores --ao-vivo
```

## O que vai para o nó

| Calibrador | Parâmetro do nó `vision` |
|---|---|
| verde (`lower`, `upper`) | `hsv.field_min`, `hsv.field_max` |
| branco (`lower`, `upper`) | `hsv.white_min`, `hsv.white_max` (o nó usa o branco também como marcação) |

O arquivo `config/hsv_calibrado.yaml` é carregado depois do `vision_params.yaml`
e sobrescreve o `hsv` de lá. Apague-o (e rode `colcon build`) para voltar às
faixas padrão.

O `green_pixels.csv` que o calibrador também salva **não** é usado: o nó
deriva a faixa do verde desse CSV com uma margem extra (8, 40, 50), o que
alargaria a caixa calibrada.

## Observações

- **Prévia:** a fronteira do campo e o esqueleto mostrados no calibrador vêm
  da segmentação do `robocup_line_vision` (`stage1_adapter.py` + `vendor/`),
  não da segmentação do `object_finder`. A máscara verde/branca (tecla **V**)
  é a mesma conta (`inRange` na caixa HSV) que o nó faz.
- **Outros comandos:** `capturar_frames` e `capturar_frames_ros` salvam frames
  para calibrar depois; `importar_calibracao_json` importa o JSON do
  calibrador HTML (`calibrador.html`, abre no navegador, funciona offline).
- Guia original completo: `robocup_line_vision/docs/calibracao.md` na branch
  `giovanna`.
