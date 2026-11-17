# vendor/ — código original da etapa 1 (III-A e III-B)

Origem: o zip do repositório original da etapa 1 que está no `kit_visao`,
copiado em 2026-11-11. Este código não foi escrito neste pacote. A lógica
**não foi alterada**. Só mudaram importações e caminhos, como no
`Webots_YOLOv8`.

| Arquivo aqui | Arquivo original | md5 do original |
|---|---|---|
| `main.py` | `main.py` | `ed3acee083d4d5f880be5d7b2fcf528e` |
| `def_white_threshold.py` | `def_white_threshold.py` | `2ce6bc77c699bf3db750da17dbef2397` |
| `green_pixels.csv` | `green_pixels.csv` | (cópia byte a byte) |
| `white_pixels.csv` | `white_pixels.csv` | (cópia byte a byte) |

## Linhas alteradas (lista completa)

`main.py`

```diff
@@ linha 4 @@
-import def_white_threshold as branco
+from . import def_white_threshold as branco
```

`def_white_threshold.py`

```diff
@@ depois da linha 3 (import io) @@
+import os
@@ linha 7 (agora 8) @@
-csv_data = "white_pixels.csv"
+csv_data = os.environ.get("RLV_WHITE_CSV", os.path.join(os.path.dirname(os.path.abspath(__file__)), "white_pixels.csv"))
```

Nenhuma outra linha mudou (confira com `diff` contra o zip original).

## Como o pacote usa este código sem efeito colateral

O `def_white_threshold.py` original lê o CSV **na importação**, por caminho
relativo ao diretório atual, e imprime estatísticas. O adaptador
`robocup_line_vision/stage1_adapter.py` resolve isso assim:

1. **Limiar do branco por calibração**: executa uma cópia nova (módulo
   isolado, nome único) do `def_white_threshold.py` com a variável de ambiente
   `RLV_WHITE_CSV` apontando para o CSV desejado, sob um `threading.Lock`, com
   a saída padrão desviada, e restaura o ambiente no `finally`. A fórmula usada
   é a original (média ± 2·desvio por canal), executada pelo próprio código
   original.
2. **Uma instância por calibração**: cada `Stage1Segmenter` carrega uma cópia
   nova do `main.py` (módulo isolado) e substitui nela o objeto `branco` por um
   `SimpleNamespace(lower, up)`. Assim duas calibrações diferentes podem
   coexistir no mesmo processo (por exemplo, o calibrador e o nó).
3. **Máscara do YOLO antes do esqueleto**: o adaptador chama os métodos
   originais na mesma ordem de `processar()` (`_preparar_frame`,
   `_masks_and_resize`, `_binarization`, `_skeletonization_and_connect` e,
   opcionalmente, `_extrair_segmentos_conectados`) e, entre a binarização e o
   esqueleto, zera o branco dentro das caixas de bola/robô/trave. Sem caixas o
   resultado é idêntico ao de `processar()` (teste
   `test/test_stage1_adapter.py::test_equivalente_ao_processar`).

`main.py` mantém o bloco `if __name__ == '__main__'` original (não é executado
na importação).
