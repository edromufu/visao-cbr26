# Calibração de cor na hora do teste (passo a passo)

Objetivo: em **menos de 2 minutos**, ensinar à etapa 1 qual é o verde do
carpete e qual é o branco das linhas **com a câmera real**. Sem isso a etapa 1
não acha o campo (medido: nas 2 fotos reais do kit, a calibração do Webots dá
"campo NÃO detectado").

Há dois caminhos. Use o 1; se a janela do OpenCV ou a câmera não abrirem no
WSL, use o 2.

---

## Caminho 1 — calibrador OpenCV (câmera ao vivo ou imagens)

Na pasta `kit_visao/robocup_line_vision` (ou com o pacote instalado):

```bash
# câmera ao vivo (troque 2 pelo índice certo; a EDROM usa 2 no object_finder)
python3 -m robocup_line_vision.calibration.calibrator_cv --camera 2 --largura 640 --altura 480 --saida ~/calibracoes

# ou imagens já capturadas
python3 -m robocup_line_vision.calibration.calibrator_cv --imagens ~/frames_dia13 --saida ~/calibracoes
```

Abrem duas janelas: **calibrador** (imagem + painel embaixo) e **ajustes**
(12 deslizadores). Tecla **H** mostra a ajuda na tela.

### Recalibração rápida (o caminho de 2 minutos)

1. Aponte a câmera para o campo com carpete e pelo menos uma linha branca.
2. Tecle **R**.
3. **Clique no carpete verde** (de preferência numa parte típica, nem a mais
   escura nem a mais clara).
4. **Clique no meio de uma linha branca** (perto da câmera, onde a linha é
   larga).
5. Olhe o painel:
   * `campo SIM` em verde e `OK` na linha de avisos → ótimo;
   * **amarelo** = fronteira do campo; **vermelho** = esqueleto (deve correr
     sobre as linhas); **magenta** = pixels classificados como branco.
6. Tecle **S** para salvar. A pasta aparece no painel
   (`calibracoes/calib_AAAAMMDD_HHMMSS/`) e `calibracoes/ultima/` é atualizada.

Se a câmera estiver ao vivo, **F** congela o frame ("usar o frame atual") e
volta ao vivo.

### Quando o painel avisar algo

| Aviso | O que fazer |
|---|---|
| `campo NAO detectado` | tecle **G** e pinte mais carpete (sombras e partes claras), arrastando com o botão esquerdo |
| `pouco verde no campo` | idem: mais amostras de verde, ou baixe `VD S min`/`VD V min` |
| `branco demais no campo` | suba `BR V min` ou baixe `BR S max` nos deslizadores |
| `branco encostado na fronteira (placas/parede...)` | tecle **A**: sobe o V mínimo do branco para tirar placas/parede da borda do campo; confira se as linhas distantes continuam vermelhas |
| `quase sem esqueleto` | tecle **B** e pinte sobre as linhas (o pincel tem raio pequeno: `[` e `]` mudam) |

Outras teclas: **G**/**B** modo verde/branco, **T** pincel ↔ retângulo,
**U** ou botão direito desfaz, **C** limpa as amostras, **V** troca a
visualização (geral, máscara verde, máscara branca, esqueleto, imagem),
**N**/**P** próxima/anterior imagem. **ESC** ou **Q** sai (pede confirmação
se não salvou).

### O que fica salvo

```
calibracoes/
  calib_20261113_091512/
    green_pixels.csv         # H,S,V — TODAS as tríades da caixa do verde (LUT densa)
    white_pixels.csv         # H,S,V,class=branco — reproduz a faixa pela fórmula original
    calib_20261113_091512.json   # faixas, amostras, métricas, data, imagens
    frames/                  # os frames usados nas amostras
  ultima/                    # cópia da mais recente (calib.json + CSVs)
```

Nada é sobrescrito. Os CSVs estão no formato que a etapa 1 já lê:
dá para copiá-los para o `recursos/` do `Webots_YOLOv8` (à mão), se
quiser.

---

## Caminho 2 — câmera fora do WSL + calibrador HTML

1. **Capturar frames** onde a câmera funciona (Windows com Python + OpenCV, ou
   o NUC):

   ```bash
   python3 -m robocup_line_vision.calibration.capture_frames --camera 0 -n 20 -t 1.0 --largura 640 --altura 480 --saida frames_dia13
   ```

   (com ROS: `ros2 run robocup_line_vision capture_frames_ros --topico <topico> -n 20 -t 1.0 --saida frames_dia13`)

2. Abrir `robocup_line_vision/calibration/calibrador.html` no navegador
   (duplo clique; funciona offline, nada é enviado).
3. **Abrir imagens** → mesmas teclas: **R**, clique no verde, clique na linha,
   confira, **S** ("Gerar arquivos").
4. O navegador baixa `calib_AAAAMMDD_HHMMSS.json`, `green_pixels.csv` e
   `white_pixels.csv`. Ou coloque os três numa pasta `calibracoes/calib_.../`,
   ou rode:

   ```bash
   python3 -m robocup_line_vision.calibration.importar_json ~/Downloads/calib_20261113_091512.json --saida ~/calibracoes
   ```

   que recria a pasta versionada e atualiza `ultima/`.

---

## Usar a calibração

```bash
# sem ROS
python3 -m robocup_line_vision --camera 2 --calib ~/calibracoes/ultima
# ROS (robô real)
ros2 launch robocup_line_vision real.launch.py camera_idx:=2 calib_dir:=$HOME/calibracoes/ultima
```

Para conferir uma calibração salva sem abrir janela:

```bash
python3 -m robocup_line_vision.calibration.calibrator_cv --avaliar --calib ~/calibracoes/ultima --imagens frames_dia13 --relatorio conferencia/
```

## Se a iluminação mudar durante o teste

Tecle **R** de novo (2 cliques) e **S**. A calibração anterior continua
salva; volte a ela passando a pasta antiga em `--calib`/`calib_dir`.

## Tempo

O fluxo mínimo é **R + 2 cliques + S**. Medido com cliques automáticos (XTest)
num Xvfb: segundos. **Não foi cronometrado com uma pessoa usando** (não havia
como aqui); a meta de < 2 min depende de achar o índice da câmera e de o WSL
enxergá-la.
