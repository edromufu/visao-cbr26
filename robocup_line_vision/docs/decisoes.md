# Decisões e suposições

Numeradas para referência no relatório. "Medido" = há número em
`docs/metricas.md` ou nos JSON de `docs/`.

## Escopo e regras

* **D1. Pacote novo e independente.** `robocup_line_vision/` fica em
  `kit_visao/`, sem `.git` e sem vínculo com `edrom_main`, `Webots_YOLOv8` ou
  `~/segmentation`. Nada foi commitado em repositório de ninguém. O que
  muda na EDROM está descrito em `roteiros/06_onde_encaixar_na_edrom.md`, para
  aplicar à mão.
* **D2. III-A/III-B vêm do código original, sem alterar a lógica.** Cópia em
  `vendor/`, com 3 linhas alteradas (importação relativa e caminho do CSV,
  `vendor/VENDOR.md`). O adaptador reproduz o original **bit a bit** nos 6
  frames do kit (máscaras, campo, esqueleto e polilinhas; medido).
* **D3. Filtro de partículas fora.** O pacote só publica o que o
  `localization_pkg` consome (`edrom_msgs/LandmarkArray`, opcional).

## Calibração (P0)

* **D4. Verde = caixa HSV, CSV denso.** A LUT original é exata (só as
  tríades listadas contam). A ferramenta grava **todas** as tríades da caixa
  (por exemplo, 200 a 330 mil linhas, de 2 a 4 MB). Proposta: percentis 1–99 com
  margem (H ±4, S −25, V ±30), S até 255, descarte de pixels quase pretos e de
  outliers por mediana ± 3,5·MAD (cantos escuros da lente e robôs pegos sem
  querer; medido na foto `bitbots`: sem isso a caixa virava H 0–114, S 0–255,
  ou seja, tudo).
* **D5. Branco: CSV que reproduz exatamente a faixa pela fórmula original.**
  A etapa 1 calcula o limiar com média ± 2·desvio por canal. Para o ajuste fino
  (deslizadores) valer também no código original, o `white_pixels.csv` gravado traz
  amostras *equivalentes* sintetizadas (dois níveis inteiros por canal), e não
  as amostras cruas. As amostras reais vão para o `calib_*.json`. Teste:
  `white_thresholds_from_csv(white_pixels.csv)` devolve exatamente a faixa
  escolhida (7 faixas testadas, incluindo os extremos).
* **D6. Proposta do branco filtrada.** Pinceladas sobre linhas finas pegam
  carpete e borda: excluímos pixels dentro da caixa do verde e separamos claro
  de escuro por Otsu no V. Faixa: percentis 5–95, H livre (0–179; branco não tem
  matiz), S desde 0, V até 255.
* **D7. Tecla A (sugestão de V mínimo).** No Webots as placas de publicidade
  têm V = 212, o mesmo das linhas distantes; com V mínimo 191 elas viram
  "campo" e o esqueleto sobe para as placas (medido: precisão do esqueleto contra
  a verdade cai de 0,98 para 0,53). A métrica "branco na fronteira" detecta isso e
  a tecla A propõe `mediana(V do branco encostado na fronteira) + 1`. No Webots
  ela chega sozinha a 213, o valor original. A recalibração rápida
  aplica A automaticamente quando a métrica acusa. Não é calibração
  automática: a usuária vê e decide.
* **D8. Versionamento.** `calibracoes/calib_AAAAMMDD_HHMMSS/` nunca é
  sobrescrita (sufixo `_2`, `_3` no mesmo segundo); `ultima/` é **cópia** (não
  link, por causa do Windows/WSL).
* **D9. HTML como alternativa.** HighGUI funcionou num Xvfb com Qt (cliques e
  teclas reais via XTest), mas no WSL a câmera USB depende do `usbipd`. O
  `calibrador.html` (arquivo único, offline) usa um núcleo JS portado da etapa
  1 e conferido contra o Python: HSV igual ao OpenCV nas 16.777.216 cores, campo
  com no máximo 13 de 14.018 células diferentes e esqueleto com no máximo 4
  células diferentes (bordas do `fillPoly`); propostas iguais.

## Algoritmo (P1)

* **D10. Extensão: cruzamentos pelas retas e pela elipse.** Medido no
  sintético e no Webots: o operador de ranking apaga a linha **fina** perto de
  uma linha **grossa** (o relevo da grossa domina por 3 a 9 células), então a
  junção some do grafo e o cruzamento não aparece, embora as duas retas da IV-B
  saiam boas. A extensão gera candidatos pela interseção das retas (e reta ×
  elipse, para o X da linha do meio com o círculo) e os submete à **mesma
  verificação do artigo**. Efeito medido no sintético (30 frames, semente 7):
  precisão 0,41 → 0,46 e recall 0,16 → 0,29. Pode ser desligada
  (`saida.cruzamentos_de_retas: false`).
* **D11. Conexões candidatas ponta→aresta.** Caso medido num T sintético
  limpo: a linha que atravessa a junção é religada por cima dela e a haste
  termina *sobre uma aresta*, não sobre um nó. Sem isso, o T não se forma.
* **D12. Ordem total dos nós.** `np.lexsort((x, y, c, −cinza, cume))` em vez
  de `argsort(−cinza)`: o desempate do `argsort` mudava o resultado entre numpy
  1.26 e 2.x (problema registrado na retomada de 09/11). Os testes passam em
  numpy 1.21.5 (Humble) e 2.5.
* **D13. Pico isolado não é dividido.** Um pico de grau 0 costuma ser o
  centro de uma junção (o ranking quebra o esqueleto em volta). Dividi-lo
  destruía a junção (medido no caso círculo × linha do meio).
* **D14. Mínimos quadrados totais (PCA)** na IV-B em vez de regressão
  y(x), para funcionar com linhas verticais. O ponto de divisão é o nó mais
  distante da reta ajustada; quando ele cai na ponta (L de braços desiguais), uso
  a corda, porque o ajuste "descascava" a ponta nó a nó (medido no teste do L).
* **D15. Merge por centróide.** "Parâmetros parecidos" = ângulo ≤ 4° e o
  centróide de cada segmento a ≤ 1 célula da reta do outro, com a união ainda
  reta (rms ≤ `split_dist`). Comparar extremos falhava em T (o nó da junção
  inclina a reta).
* **D16. Limiar de branco relativo** na verificação da IV-A: 0,35 × mediana
  do branco ao longo dos próprios braços (linhas distantes têm densidade
  baixa na grade).
* **D17. T e X precisam de pares colineares.** Retas continuam retas em
  perspectiva, então o "tampo" do T e as duas linhas do X têm ~180° na imagem.
  L e T sobre a elipse do círculo são descartados (arcos mal conectados).
* **D18. T + X do YOLO → X.** Se o grafo vê um T onde o YOLO vê um X (conf.
  ≥ 0,6), vira X e o 4º raio é o oposto da haste (a linha fraca sumiu do
  esqueleto, D10). "Tipo compatível" para confirmar é só o mesmo tipo.
* **D19. Marcas (centro/pênalti).** O artigo não detecta marcas. A avaliação
  separa "X de cruzamento" de "X de marca" pela heurística do brief; detecções
  que caem numa marca não contam como falso positivo de cruzamento.

## Limitações conhecidas (do código original, não alteradas)

* **D20. Linhas grossas viram platô.** O borrão 5×5 da III-B não garante um
  único máximo por seção quando a linha tem mais de ~3 células de largura
  (perto da câmera do AUREA, FOV 45°). O ranking põe o esqueleto nas bordas do
  platô (visto nos overlays sintéticos de 1,5 m). Sugestão para a etapa 1:
  kernel proporcional à largura esperada da linha. A câmera real da EDROM
  (fx ≈ 311 px em 640×480, FOV ≈ 92°) sofre menos: 5 cm a 1 m ≈ 2 células.
* **D21. Placas brancas e linhas com a mesma cor.** Com o branco saturado
  (perturbação "claro ×1,35" e "frio"), placas e linhas viram a mesma cor e a
  calibração por cor não separa (medido: 6 dos 32 casos perturbados).

## Câmera e ROS (P2)

* **D22. AUREA no Webots** (derivado do `.wbt`, confirmar com `camera_info`):
  1080×720, FOV horizontal 0,785 rad, altura 0,70 m, sem inclinação.
  `config/params.yaml` → `camera.modelo: fov`. Se o nó receber `camera_info`,
  usa K e D dele.
* **D23. Robô real:** `camera_matrix.npy` (fx 311,7, cx 349, cy 215,5) e
  `dist_coeffs.npy` da EDROM, supostos de 640×480. A `homography_matrix.npy` do
  kit é a **identidade** (não calibrada) e é ignorada com aviso.
* **D24. Sem cv_bridge.** O nó converte `sensor_msgs/Image` com numpy
  (bgr8/bgra8/rgb8/rgba8/mono8). No Humble o `cv_bridge` quebra com numpy 2,
  que o `ultralytics` costuma puxar.
* **D25. IDs dos landmarks pelo nome.** Padrão `L:4, T:5, X:6`, que bate com o
  `vision_to_filter_id_map` do `localization_pkg` (4→L, 5→T). O comentário do
  `Landmark.msg` ("4 = L, 5 = T") não é o número de classe do modelo
  (`3 = L, 4 = T, 5 = X`). Por isso nada usa número de classe, só nome.
  Configurável em `landmark_ids`.
* **D26. Linhas até 120 colunas.** O `test_flake8.py` do pacote passa
  `--linelength 120` e exclui `vendor/`. O `test_pep257.py` ignora D401 (verbo
  no imperativo em inglês não se aplica a docstrings em português). Com essas
  duas exceções, flake8 (plugins do ament: import-order google, quotes,
  builtins, comprehensions) e pep257 dão **zero** avisos.
* **D27. ONNX.** `modelo/best.onnx` foi exportado do mesmo `best.pt`
  (opset 18, arquivo único). Nas fotos reais quadradas as caixas são iguais às
  do `.pt`. Em imagens não quadradas, diferem um pouco, porque o `.pt` usa
  letterbox retangular e o ONNX usa 320×320 fixo.
