"""
Espaço de cor dinâmico do campo (dynamic_color.py).

Espaço de cor DINÂMICO do campo, como na Seção 3.1 ("Color Detector") do artigo
Fiedler et al., *An Open Source Vision Pipeline Approach for RoboCup Humanoid Soccer*
(Hamburg Bit-Bots, 2019):

  "pixels in the image mainly surrounded by pixels whose color is already in the color
  space are added. However, only colors without any occurrences above the field boundary
  are chosen to ensure a stable adaptation to changes in shade and lighting."

A cada atualização:
  1. para cada pixel, a fração dos vizinhos (janela `kernel_size` x `kernel_size`) que
     já é campo;
  2. candidatos: pixels abaixo da fronteira, fora do espaço de cor, com fração >= `threshold`;
  3. as cores que aparecem ACIMA da fronteira são descartadas (nunca viram campo);
  4. as cores novas entram num histórico das últimas `history` atualizações: uma cor que
     deixa de aparecer sai sozinha depois disso.

As cores aprendidas ficam numa tabela HSV exata (H 0-179, S e V 0-255), no mesmo formato da
`lut_verde` do código original (green_pixels.csv), e se SOMAM a ela: a calibração não muda.
Só numpy e OpenCV (sem ROS).
"""

from collections import deque
from typing import Deque, Optional

import cv2
import numpy as np

HSV_SHAPE = (180, 256, 256)
N_COLORS = HSV_SHAPE[0] * HSV_SHAPE[1] * HSV_SHAPE[2]


def hsv_index(image_hsv: np.ndarray) -> np.ndarray:
    """Índice de cada pixel na tabela HSV (h * 65536 + s * 256 + v)."""
    hsv = image_hsv.astype(np.int32)
    return (hsv[..., 0] << 16) | (hsv[..., 1] << 8) | hsv[..., 2]


class DynamicColorSpace:
    """Cores do campo aprendidas durante o jogo (soma-se ao espaço de cor calibrado)."""

    def __init__(self, threshold: float = 0.6, kernel_size: int = 3, history: int = 10):
        self.threshold = float(threshold)
        self.kernel_size = int(kernel_size)
        self.history: Deque[np.ndarray] = deque(maxlen=max(1, int(history)))
        self.lut = np.zeros(N_COLORS, dtype=np.uint8)      # 255 = cor aprendida
        self._scratch = np.zeros(N_COLORS, dtype=bool)
        self._n_colors = 0

    def configure(self, threshold: float, kernel_size: int, history: int) -> None:
        """Troca os parâmetros sem perder o que já foi aprendido."""
        self.threshold = float(threshold)
        self.kernel_size = int(kernel_size)
        if self.history.maxlen != max(1, int(history)):
            self.history = deque(self.history, maxlen=max(1, int(history)))
            self._rebuild()

    @property
    def n_colors(self) -> int:
        """Quantas cores (tríades HSV) foram aprendidas."""
        return self._n_colors

    def reset(self) -> None:
        self.history.clear()
        self._rebuild()

    def mask(self, image_hsv: np.ndarray) -> np.ndarray:
        """Máscara uint8 (0/255) dos pixels com cor aprendida."""
        return self.lut[hsv_index(image_hsv)]

    def update(self, image_hsv: np.ndarray, calibrated_mask: np.ndarray, below_boundary: np.ndarray) -> int:
        """
        Aprende com um quadro e devolve quantas cores novas entraram.

        calibrated_mask: máscara do espaço de cor CALIBRADO (as cores aprendidas são somadas aqui), 0/255 ou bool.
        below_boundary: região abaixo da fronteira do campo, 0/255 ou bool.
        """
        index = hsv_index(image_hsv)
        in_space = (np.asarray(calibrated_mask) > 0) | (self.lut[index] > 0)
        below = np.asarray(below_boundary) > 0
        k = max(1, self.kernel_size)
        ratio = cv2.blur(in_space.astype(np.float32), (k, k), borderType=cv2.BORDER_REPLICATE)
        candidates = below & ~in_space & (ratio >= self.threshold)

        above = index[~below]                  # com repetições: marcar/desmarcar não precisa de unique
        new = np.unique(index[candidates])
        self._scratch[above] = True
        new = new[~self._scratch[new]]
        # cores vistas acima da fronteira saem também do que já foi aprendido
        self.history = deque((h[~self._scratch[h]] for h in self.history), maxlen=self.history.maxlen)
        self._scratch[above] = False

        self.history.append(new)
        self._rebuild()
        return int(new.size)

    def _rebuild(self) -> None:
        self.lut[:] = 0
        for colors in self.history:
            self.lut[colors] = 255
        self._n_colors = int(np.unique(np.concatenate(list(self.history))).size) if self.history else 0


def below_boundary_mask(shape, boundary_points) -> np.ndarray:
    """Região abaixo de uma fronteira dada por pontos (x, y) ordenados por x (uint8 0/255)."""
    h, w = shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    pts = [(int(x), int(y)) for x, y in boundary_points]
    if len(pts) < 2:
        return mask
    polygon = [(0, pts[0][1])] + pts + [(w - 1, pts[-1][1]), (w - 1, h - 1), (0, h - 1)]
    cv2.fillPoly(mask, [np.asarray(polygon, dtype=np.int32)], 255)
    return mask


def maybe_create(enabled: bool, threshold: float, kernel_size: int, history: int,
                 current: Optional[DynamicColorSpace] = None) -> Optional[DynamicColorSpace]:
    """Cria, reconfigura ou desliga o espaço dinâmico conforme os parâmetros."""
    if not enabled:
        return None
    if current is None:
        return DynamicColorSpace(threshold, kernel_size, history)
    current.configure(threshold, kernel_size, history)
    return current
