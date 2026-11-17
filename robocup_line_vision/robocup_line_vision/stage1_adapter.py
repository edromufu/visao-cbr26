"""
Adaptador da etapa 1 (Seções III-A e III-B do artigo).

O código original (``vendor/main.py`` e ``vendor/def_white_threshold.py``)
é usado sem alterar a lógica. Este módulo resolve três problemas dele:

* o limiar do branco é lido na importação, por caminho relativo;
* o objeto ``branco`` é global do módulo (uma calibração por processo);
* não há como mascarar o branco (caixas do YOLO) antes do esqueleto.

Veja ``vendor/VENDOR.md``.
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass, field
import importlib.util
import io
import itertools
import os
from pathlib import Path
import threading
from types import ModuleType, SimpleNamespace
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

VENDOR_DIR = Path(__file__).resolve().parent / 'vendor'
DEFAULT_GREEN_CSV = VENDOR_DIR / 'green_pixels.csv'
DEFAULT_WHITE_CSV = VENDOR_DIR / 'white_pixels.csv'

_LOCK = threading.RLock()
_COUNTER = itertools.count()

Box = Tuple[float, float, float, float]  # (x_centro, y_centro, largura, altura)


def _exec_isolated(path: Path, name: str) -> ModuleType:
    """Executa ``path`` como módulo novo, isolado (fora de ``sys.modules``)."""
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:  # pragma: no cover
        raise ImportError(f'não consegui carregar {path}')
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(module)
    return module


def white_thresholds_from_csv(csv_path: os.PathLike) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calcula (lower, up) do branco executando o código original no CSV.

    A fórmula (média ± 2·desvio por canal, recorte e conversão para int) é a
    de ``vendor/def_white_threshold.py``. O CSV é passado pela variável de
    ambiente ``RLV_WHITE_CSV`` só durante a execução; o ambiente é restaurado.
    """
    csv_path = Path(csv_path).resolve()
    if not csv_path.is_file():
        raise FileNotFoundError(f'CSV do branco não encontrado: {csv_path}')
    with _LOCK:
        old = os.environ.get('RLV_WHITE_CSV')
        os.environ['RLV_WHITE_CSV'] = str(csv_path)
        try:
            mod = _exec_isolated(
                VENDOR_DIR / 'def_white_threshold.py',
                f'robocup_line_vision.vendor._white_{next(_COUNTER)}')
        finally:
            if old is None:
                os.environ.pop('RLV_WHITE_CSV', None)
            else:
                os.environ['RLV_WHITE_CSV'] = old
    return np.asarray(mod.lower, dtype=int), np.asarray(mod.up, dtype=int)


def _load_vendor_main() -> ModuleType:
    """Carrega uma cópia nova e isolada de ``vendor/main.py``."""
    with _LOCK:
        # A importação relativa ``from . import def_white_threshold`` usa o
        # módulo compartilhado do pacote; ele lê o CSV padrão do vendor.
        old = os.environ.pop('RLV_WHITE_CSV', None)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                importlib.import_module('robocup_line_vision.vendor.def_white_threshold')
            return _exec_isolated(
                VENDOR_DIR / 'main.py',
                f'robocup_line_vision.vendor._main_{next(_COUNTER)}')
        finally:
            if old is not None:
                os.environ['RLV_WHITE_CSV'] = old


@dataclass
class Stage1Result:
    """Saída das etapas III-A/III-B (nomes originais entre parênteses)."""

    image_shape: Tuple[int, int]
    grid_shape: Tuple[int, int]
    scale: Tuple[float, float]           # (sx, sy) grade -> imagem
    white_mask: np.ndarray               # (white_mask) uint8 0/255, resolução cheia
    green_mask: np.ndarray               # (green_mask) uint8 0/255
    white_resized: np.ndarray            # (white_mask_resized) float32 0..255, grade
    green_resized: np.ndarray            # (green_mask_resized) float32 0..255, grade
    uniq_img: np.ndarray                 # (uniq_img) imagem cinza do campo
    borda_binaria: np.ndarray            # (borda_binaria)
    contour_points: np.ndarray           # (contour_points) grade (x, y)
    field_mask: np.ndarray               # (mascara_convexa) grade 0/255
    field_mask_full: np.ndarray          # (mascara_campo_original) imagem 0/255
    field_detected: bool                 # (campo_detectado)
    field_line_mask: np.ndarray          # (field_line_mask) grade
    relief: np.ndarray                   # (mascara_relevo) grade uint8
    skeleton: np.ndarray                 # (skeleton) grade bool
    segmentacao_linhas: np.ndarray       # (segmentacao_linhas) imagem 0/255
    baseline: Dict[str, Any] = field(default_factory=dict)  # polilinhas da etapa 1
    masked_boxes: List[Box] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)       # dicionários originais

    def grid_to_image(self, gx: float, gy: float) -> Tuple[float, float]:
        """Centro da célula (gx, gy) da grade em coordenadas da imagem."""
        sx, sy = self.scale
        return (float((gx + 0.5) * sx), float((gy + 0.5) * sy))

    def image_to_grid(self, x: float, y: float) -> Tuple[float, float]:
        """Inverso de :meth:`grid_to_image` (coordenada contínua)."""
        sx, sy = self.scale
        return (float(x / sx - 0.5), float(y / sy - 0.5))

    def boundary_image_points(self) -> np.ndarray:
        """Fronteira do campo em pixels da imagem (sem os 2 pontos de fecho)."""
        if not self.field_detected or len(self.contour_points) < 3:
            return np.empty((0, 2), dtype=np.float32)
        sx, sy = self.scale
        pts = self.contour_points[:-2].astype(np.float32).copy()
        pts[:, 0] = (pts[:, 0] + 0.5) * sx
        pts[:, 1] = pts[:, 1] * sy
        return pts


def _box_to_cells(box: Box, scale: Tuple[float, float], grid_shape: Tuple[int, int],
                  margin_cells: int) -> Tuple[int, int, int, int]:
    """Retângulo de células da grade que tocam a caixa (com margem)."""
    sx, sy = scale
    gh, gw = grid_shape
    xc, yc, w, h = box
    x0 = int(np.floor((xc - w / 2.0) / sx)) - margin_cells
    x1 = int(np.floor((xc + w / 2.0) / sx)) + margin_cells
    y0 = int(np.floor((yc - h / 2.0) / sy)) - margin_cells
    y1 = int(np.floor((yc + h / 2.0) / sy)) + margin_cells
    return (max(0, x0), max(0, y0), min(gw - 1, x1), min(gh - 1, y1))


class Stage1Segmenter:
    """
    Roda III-A e III-B com o código original e uma calibração própria.

    Parâmetros
    ----------
    green_csv:
        CSV ``H,S,V`` (LUT exata do verde).
    white_csv:
        CSV ``H,S,V,class`` (amostras do branco); o limiar sai da fórmula
        original. Ignorado se ``white_range`` for dado.
    white_range:
        ``(lower, up)`` já calculados (por exemplo, do ``calib_*.json``).
    tpix, trow, twin:
        Limiares da binarização (III-A.2), padrão original.
    baseline_polylines:
        Se verdadeiro, roda também ``_extrair_segmentos_conectados`` da etapa 1
        (linha de base de comparação; custa tempo).
    """

    def __init__(self, green_csv: os.PathLike = DEFAULT_GREEN_CSV,
                 white_csv: Optional[os.PathLike] = DEFAULT_WHITE_CSV,
                 white_range: Optional[Tuple[Sequence[int], Sequence[int]]] = None,
                 tpix: int = 20, trow: int = 10000, twin: int = 3000,
                 baseline_polylines: bool = False) -> None:
        self.green_csv = Path(green_csv).resolve()
        if not self.green_csv.is_file():
            raise FileNotFoundError(f'CSV do verde não encontrado: {self.green_csv}')
        if white_range is not None:
            lower = np.asarray(white_range[0], dtype=int)
            up = np.asarray(white_range[1], dtype=int)
            self.white_csv = None
        else:
            if white_csv is None:
                raise ValueError('informe white_csv ou white_range')
            self.white_csv = Path(white_csv).resolve()
            lower, up = white_thresholds_from_csv(self.white_csv)
        self.white_lower = lower
        self.white_up = up
        self._mod = _load_vendor_main()
        self._mod.branco = SimpleNamespace(lower=lower, up=up)
        with contextlib.redirect_stdout(io.StringIO()):
            self._seg = self._mod.Pixel_Segment(str(self.green_csv), tpix=tpix,
                                                trow=trow, twin=twin)
        self.baseline_polylines = baseline_polylines

    @property
    def vendor_segmenter(self) -> Any:
        """Instância ``Pixel_Segment`` original (para testes de equivalência)."""
        return self._seg

    def set_green_box(self, lower: Sequence[int], upper: Sequence[int]) -> None:
        """
        Troca a LUT do verde por uma caixa HSV (pré-visualização ao vivo).

        Equivale a carregar o ``green_pixels.csv`` denso daquela caixa (todas
        as tríades), sem gravar e reler o arquivo a cada ajuste.
        """
        lut = np.zeros((180, 256, 256), dtype=np.uint8)
        (h0, s0, v0), (h1, s1, v1) = lower, upper
        lut[int(h0):int(h1) + 1, int(s0):int(s1) + 1, int(v0):int(v1) + 1] = 255
        self._seg.lut_verde = lut

    def set_white_range(self, lower: Sequence[int], upper: Sequence[int]) -> None:
        """Troca o limiar do branco (``branco.lower``/``branco.up``)."""
        self.white_lower = np.asarray(lower, dtype=int)
        self.white_up = np.asarray(upper, dtype=int)
        self._mod.branco = SimpleNamespace(lower=self.white_lower, up=self.white_up)

    def process(self, frame_bgr: np.ndarray, mask_boxes: Sequence[Box] = (),
                mask_margin_cells: int = 0) -> Stage1Result:
        """
        Processa um frame BGR; ``mask_boxes`` zera o branco nessas caixas.

        As caixas são ``(x_centro, y_centro, largura, altura)`` em pixels. O
        mascaramento acontece depois da fronteira do campo (III-A) e antes do
        esqueleto (III-B), em resolução cheia e na grade.
        """
        seg = self._seg
        seg._preparar_frame(frame_bgr)
        masks = seg._masks_and_resize()
        binar = seg._binarization(masks['white_mask_resized'], masks['green_mask_resized'])
        white_mask = masks['white_mask']
        white_resized = masks['white_mask_resized']
        gh, gw = binar['borda_binaria'].shape
        h, w = frame_bgr.shape[:2]
        scale = (w / gw, h / gh)
        boxes = [tuple(float(v) for v in b) for b in mask_boxes]
        if boxes:
            white_mask = white_mask.copy()
            white_resized = white_resized.copy()
            for b in boxes:
                xc, yc, bw, bh = b
                x0 = max(0, int(np.floor(xc - bw / 2)))
                x1 = min(w, int(np.ceil(xc + bw / 2)))
                y0 = max(0, int(np.floor(yc - bh / 2)))
                y1 = min(h, int(np.ceil(yc + bh / 2)))
                white_mask[y0:y1, x0:x1] = 0
                cx0, cy0, cx1, cy1 = _box_to_cells(b, scale, (gh, gw), mask_margin_cells)
                white_resized[cy0:cy1 + 1, cx0:cx1 + 1] = 0
        skel = seg._skeletonization_and_connect(white_mask, white_resized,
                                                binar['mascara_convexa'])
        baseline: Dict[str, Any] = {}
        if self.baseline_polylines:
            baseline = seg._extrair_segmentos_conectados(skel['skeleton_img'])
        return Stage1Result(
            image_shape=(h, w), grid_shape=(gh, gw), scale=scale,
            white_mask=white_mask, green_mask=masks['green_mask'],
            white_resized=white_resized, green_resized=masks['green_mask_resized'],
            uniq_img=binar['uniq_img'], borda_binaria=binar['borda_binaria'],
            contour_points=binar['contour_points'], field_mask=binar['mascara_convexa'],
            field_mask_full=skel['mascara_campo_original'],
            field_detected=bool(binar['campo_detectado']),
            field_line_mask=skel['field_line_mask'], relief=skel['mascara_relevo'],
            skeleton=skel['skeleton'].astype(bool),
            segmentacao_linhas=skel['segmentacao_linhas'], baseline=baseline,
            masked_boxes=list(boxes),
            raw={'masks': masks, 'binarizacao': binar, 'esqueleto': skel})


def ranking_count(relief: np.ndarray) -> np.ndarray:
    """
    c(x, y) do operador de ranking (III-B), mesma fórmula da etapa 1.

    Número de vizinhos-8 com nível de cinza maior ou igual ao central. A
    etapa 1 não devolve esse mapa; a III-C precisa dele para separar picos
    (c = 0) de cumes (c = 1, 2).
    """
    padded = np.pad(relief, ((1, 1), (1, 1)), mode='constant', constant_values=0)
    vizinhos = np.stack([
        padded[:-2, 1:-1], padded[2:, 1:-1], padded[1:-1, 2:], padded[1:-1, :-2],
        padded[:-2, 2:], padded[2:, 2:], padded[:-2, :-2], padded[2:, :-2]])
    return np.sum(vizinhos >= relief[np.newaxis, :, :], axis=0, dtype=np.uint8)
