"""
Fusão do grafo de linhas com o detector YOLO.

Regras (``docs/decisoes.md``):

* caixas de ``ball``, ``robot`` e ``goalpost`` **mascaram** o branco antes do
  esqueleto (III-B/III-C) — evita linhas falsas nos pés das traves e robôs;
* detecções **fora do campo** segmentado são rejeitadas (``outside_field``):
  objetos de pé no campo (bola, robô, trave) são testados pela base da caixa;
  marcas e cruzamentos, pelo centro;
* um cruzamento do grafo **confirmado** por uma caixa ``L/T/X-Intersection``
  do mesmo tipo e na mesma região sobe de confiança (``fonte='grafo+yolo'``);
* um cruzamento só do YOLO, sem estrutura de linha, entra **rebaixado**
  (``fonte='yolo'``, sem ``heading_rays``: o YOLO não dá direções);
* as classes são mapeadas **pelo nome**, nunca pelo número.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
import math
from typing import Any, Dict, List, Sequence, Tuple

import cv2
import numpy as np

from .features import CrossingFeature, Detection

INTERSECTION_CLASSES = {'L-Intersection': 'L', 'T-Intersection': 'T', 'X-Intersection': 'X'}
STANDING_CLASSES = ('ball', 'robot', 'goalpost')


@dataclass
class FusionParams:
    """Parâmetros da fusão."""

    mask_classes: Tuple[str, ...] = ('ball', 'robot', 'goalpost')
    mask_margin_px: float = 4.0
    reject_outside_field: bool = True
    field_tolerance_cells: int = 1      # dilata a máscara do campo
    confirm_radius_px: float = 24.0     # + metade da maior dimensão da caixa
    confirm_boost: float = 0.3          # confiança += boost * conf_yolo
    yolo_only_factor: float = 0.5       # confiança = conf_yolo * fator
    yolo_only_min_dist_px: float = 30.0  # não duplica cruzamento já existente
    keep_yolo_only: bool = True
    upgrade_t_to_x_min_conf: float = 0.6  # T do grafo + X do YOLO -> X


@dataclass
class FusionResult:
    """Resultado da fusão."""

    crossings: List[CrossingFeature]
    detections: List[Detection]
    info: Dict[str, Any] = field(default_factory=dict)


def _field_full(s1: Any, tol_cells: int) -> np.ndarray:
    fm = np.asarray(s1.field_mask, np.uint8)
    if tol_cells > 0:
        k = np.ones((2 * tol_cells + 1, 2 * tol_cells + 1), np.uint8)
        fm = cv2.dilate(fm, k)
    h, w = s1.image_shape
    return cv2.resize(fm, (w, h), interpolation=cv2.INTER_NEAREST) > 0


def _inside(mask: np.ndarray, x: float, y: float) -> bool:
    h, w = mask.shape
    xi, yi = int(np.clip(round(x), 0, w - 1)), int(np.clip(round(y), 0, h - 1))
    return bool(mask[yi, xi])


def mask_boxes(dets: Sequence[Detection], p: FusionParams) -> List[Tuple[float, float, float, float]]:
    """Caixas (aceitas) que mascaram o branco antes do esqueleto."""
    m = p.mask_margin_px
    return [(d.x, d.y, d.w + 2 * m, d.h + 2 * m) for d in dets
            if d.classe in p.mask_classes and not d.rejeitada]


def check_field(dets: Sequence[Detection], s1: Any, p: FusionParams) -> List[Detection]:
    """Marca como rejeitadas as detecções fora do campo segmentado."""
    out = []
    if not p.reject_outside_field:
        return [replace(d) for d in dets]
    if not getattr(s1, 'field_detected', False):
        return [replace(d, rejeitada=True, motivo='outside_field') for d in dets]
    fm = _field_full(s1, p.field_tolerance_cells)
    for d in dets:
        if d.classe in STANDING_CLASSES:
            px, py = d.x, d.y + d.h / 2.0 - 1  # base da caixa (pé)
        else:
            px, py = d.x, d.y
        ok = _inside(fm, px, py)
        out.append(replace(d, rejeitada=not ok, motivo='' if ok else 'outside_field'))
    return out


def fuse(crossings: Sequence[CrossingFeature], dets: Sequence[Detection], s1: Any,
         p: FusionParams) -> FusionResult:
    """Combina cruzamentos do grafo com as caixas do YOLO."""
    dets = check_field(dets, s1, p)
    out = [replace(c, verificacao=dict(c.verificacao)) for c in crossings]
    yolo_x = [d for d in dets if d.classe in INTERSECTION_CLASSES and not d.rejeitada]
    confirmed, used = 0, set()
    for i, d in enumerate(sorted(yolo_x, key=lambda d: -d.conf)):
        tipo = INTERSECTION_CLASSES[d.classe]
        rad = p.confirm_radius_px + 0.5 * max(d.w, d.h)
        best, bd = None, 1e9
        for k, c in enumerate(out):
            if c.fonte == 'yolo' or k in used:
                continue
            dist = math.hypot(c.x - d.x, c.y - d.y)
            if dist <= rad and c.tipo == tipo and dist < bd:
                best, bd = k, dist
        if best is None and tipo == 'X' and d.conf >= p.upgrade_t_to_x_min_conf:
            # T do grafo onde o YOLO vê X: o 4º braço (linha fraca) sumiu do
            # esqueleto. Vira X com o raio oposto à haste.
            for k, c in enumerate(out):
                if k in used or c.fonte == 'yolo' or c.tipo != 'T' or len(c.heading_rays) != 3:
                    continue
                if math.hypot(c.x - d.x, c.y - d.y) <= rad:
                    r = sorted(c.heading_rays)
                    # a haste é o raio que não faz parte do par colinear (~pi entre eles)
                    stem = None
                    for i in range(3):
                        others = [r[j] for j in range(3) if j != i]
                        diff = abs((others[0] - others[1] + math.pi) % (2 * math.pi) - math.pi)
                        if diff > math.radians(150):
                            stem = r[i]
                    if stem is None:
                        continue
                    c.heading_rays = sorted(r + [(stem + math.pi) % (2 * math.pi)])
                    c.tipo = 'X'
                    c.verificacao['tipo_corrigido_pelo_yolo'] = 'T->X'
                    best, bd = k, math.hypot(c.x - d.x, c.y - d.y)
                    break
        if best is not None:
            c = out[best]
            c.confianca = round(min(1.0, c.confianca + p.confirm_boost * d.conf), 3)
            c.fonte = 'grafo+yolo'
            c.verificacao['yolo'] = {'conf': round(d.conf, 3), 'dist_px': round(bd, 1)}
            used.add(best)
            confirmed += 1
            continue
        if not p.keep_yolo_only:
            continue
        near = any(math.hypot(c.x - d.x, c.y - d.y) < p.yolo_only_min_dist_px for c in out)
        if near:
            continue
        out.append(CrossingFeature(tipo=tipo, x=float(d.x), y=float(d.y), heading_rays=[],
                                   confianca=round(d.conf * p.yolo_only_factor, 3), fonte='yolo',
                                   verificacao={'yolo': {'conf': round(d.conf, 3)},
                                                'sem_estrutura_de_linha': True}))
    return FusionResult(out, dets, {'confirmados': confirmed, 'yolo_cruzamentos': len(yolo_x)})
