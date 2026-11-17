"""
Métricas contra a verdade de terreno (``gt_marcacoes.json`` v2 e sintético).

Regras (``docs/metricas.md``):

* **cruzamentos**: casamento um-para-um guloso pela menor distância, raio
  15 px. Reporta "posição" (qualquer tipo) e "posição + tipo";
* **X de marca** (marca do centro / do pênalti, marcadas como X pela
  usuária) saem da conta principal e são reportadas à parte: X a menos de
  12 px de uma linha curta (< 30 px) ou que não está sobre nenhuma linha longa;
* **linhas**: cobertura só das longas (≥ 30 px); uma linha da verdade é
  coberta se ≥ 50 % do comprimento fica a ≤ 10 px de alguma linha detectada
  com ângulo ≤ 10°; uma linha detectada é correta se ≥ 50 % dela fica a
  ≤ 10 px de alguma linha da verdade (qualquer tamanho) ou de um círculo;
* **círculos**: os pontos de todos os arcos da imagem viram uma elipse
  (``cv2.fitEllipse``); compara centro e eixos.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np


def load_gt(path: str) -> Dict[str, Dict[str, Any]]:
    """Lê ``gt_marcacoes.json`` (versão 2)."""
    d = json.loads(Path(path).read_text(encoding='utf-8'))
    return d['imagens'] if 'imagens' in d else d


def _seg_len(ln: Dict[str, float]) -> float:
    return math.hypot(ln['x2'] - ln['x1'], ln['y2'] - ln['y1'])


def point_seg_dist(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
    """Distância ponto-segmento."""
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - x1 - t * dx, py - y1 - t * dy)


def is_mark(c: Dict[str, Any], img_gt: Dict[str, Any], near_short: float = 12.0,
            on_long: float = 12.0) -> bool:
    """Heurística "X de marca" (centro/pênalti)."""
    if c['tipo'] != 'X':
        return False
    for ln in img_gt.get('linhas', []):
        if _seg_len(ln) < 30:
            pts = [(ln['x1'], ln['y1']), (ln['x2'], ln['y2']),
                   ((ln['x1'] + ln['x2']) / 2, (ln['y1'] + ln['y2']) / 2)]
            if min(math.hypot(c['x'] - x, c['y'] - y) for x, y in pts) < near_short:
                return True
    longs = [ln for ln in img_gt.get('linhas', []) if _seg_len(ln) >= 30]
    return not any(point_seg_dist(c['x'], c['y'], ln['x1'], ln['y1'], ln['x2'], ln['y2']) < on_long
                   for ln in longs)


@dataclass
class MatchResult:
    """Casamento de cruzamentos."""

    tp: int = 0
    tp_tipo: int = 0
    fp: int = 0
    fn: int = 0
    pares: List[Tuple[int, int, float]] = field(default_factory=list)
    por_tipo: Dict[str, Dict[str, int]] = field(default_factory=dict)

    @property
    def precisao(self) -> float:
        """TP / (TP + FP)."""
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) else 0.0

    @property
    def recall(self) -> float:
        """TP / (TP + FN)."""
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) else 0.0

    def add(self, o: 'MatchResult') -> None:
        """Acumula."""
        self.tp += o.tp
        self.tp_tipo += o.tp_tipo
        self.fp += o.fp
        self.fn += o.fn
        for t, d in o.por_tipo.items():
            acc = self.por_tipo.setdefault(t, {'gt': 0, 'det': 0, 'tp': 0, 'tp_tipo': 0})
            for k, v in d.items():
                acc[k] += v


def match_crossings(dets: Sequence[Any], gts: Sequence[Dict[str, Any]], radius: float = 15.0) -> MatchResult:
    """Casamento guloso um-para-um por distância (raio em px)."""
    pairs = sorted((math.hypot(d.x - g['x'], d.y - g['y']), i, j)
                   for i, d in enumerate(dets) for j, g in enumerate(gts))
    used_d, used_g = set(), set()
    r = MatchResult()
    for dist, i, j in pairs:
        if dist > radius or i in used_d or j in used_g:
            continue
        used_d.add(i)
        used_g.add(j)
        r.pares.append((i, j, dist))
    r.tp = len(r.pares)
    r.tp_tipo = sum(1 for i, j, _ in r.pares if dets[i].tipo == gts[j]['tipo'])
    r.fp = len(dets) - r.tp
    r.fn = len(gts) - r.tp
    for t in ('L', 'T', 'X'):
        r.por_tipo[t] = {'gt': sum(g['tipo'] == t for g in gts), 'det': sum(d.tipo == t for d in dets),
                         'tp': sum(1 for i, j, _ in r.pares if gts[j]['tipo'] == t),
                         'tp_tipo': sum(1 for i, j, _ in r.pares if gts[j]['tipo'] == t and dets[i].tipo == t)}
    return r


def _sample_seg(x1: float, y1: float, x2: float, y2: float, step: float = 2.0) -> np.ndarray:
    L = math.hypot(x2 - x1, y2 - y1)
    n = max(2, int(L / step) + 1)
    t = np.linspace(0, 1, n)
    return np.stack([x1 + t * (x2 - x1), y1 + t * (y2 - y1)], 1)


def _angle(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.atan2(y2 - y1, x2 - x1) % math.pi


def _adiff(a: float, b: float) -> float:
    d = abs(a - b) % math.pi
    return min(d, math.pi - d)


@dataclass
class LineMetrics:
    """Métricas de linhas."""

    gt_longas: int = 0
    gt_longas_cobertas: int = 0
    gt_curtas: int = 0
    gt_curtas_cobertas: int = 0
    det: int = 0
    det_corretas: int = 0

    @property
    def recall(self) -> float:
        """Cobertura das linhas longas."""
        return self.gt_longas_cobertas / self.gt_longas if self.gt_longas else 0.0

    @property
    def precisao(self) -> float:
        """Linhas detectadas corretas / detectadas."""
        return self.det_corretas / self.det if self.det else 0.0

    def add(self, o: 'LineMetrics') -> None:
        """Acumula."""
        for k in ('gt_longas', 'gt_longas_cobertas', 'gt_curtas', 'gt_curtas_cobertas', 'det', 'det_corretas'):
            setattr(self, k, getattr(self, k) + getattr(o, k))


def circle_points(img_gt: Dict[str, Any]) -> np.ndarray:
    """Todos os pontos dos arcos da verdade de terreno."""
    pts = []
    for c in img_gt.get('circulos', []):
        for p in c['pontos']:
            pts.append((p['x'], p['y']) if isinstance(p, dict) else tuple(p))
    return np.array(pts, float).reshape(-1, 2)


def line_metrics(det_lines: Sequence[Any], img_gt: Dict[str, Any], tol_px: float = 10.0,
                 tol_deg: float = 10.0, min_cover: float = 0.5) -> LineMetrics:
    """Cobertura (linhas longas) e precisão das linhas detectadas."""
    m = LineMetrics()
    tol_a = math.radians(tol_deg)
    gls = img_gt.get('linhas', [])
    cpts = circle_points(img_gt)
    for g in gls:
        longa = _seg_len(g) >= 30
        ga = _angle(g['x1'], g['y1'], g['x2'], g['y2'])
        samples = _sample_seg(g['x1'], g['y1'], g['x2'], g['y2'])
        ok = np.zeros(len(samples), bool)
        for d in det_lines:
            if _adiff(ga, _angle(d.x1, d.y1, d.x2, d.y2)) > tol_a:
                continue
            ok |= np.array([point_seg_dist(px, py, d.x1, d.y1, d.x2, d.y2)
                           <= tol_px for px, py in samples])
        cov = bool(ok.mean() >= min_cover)
        if longa:
            m.gt_longas += 1
            m.gt_longas_cobertas += cov
        else:
            m.gt_curtas += 1
            m.gt_curtas_cobertas += cov
    for d in det_lines:
        m.det += 1
        da = _angle(d.x1, d.y1, d.x2, d.y2)
        samples = _sample_seg(d.x1, d.y1, d.x2, d.y2)
        ok = np.zeros(len(samples), bool)
        for g in gls:
            if _adiff(da, _angle(g['x1'], g['y1'], g['x2'], g['y2'])) > tol_a:
                continue
            ok |= np.array([point_seg_dist(px, py, g['x1'], g['y1'], g['x2'], g['y2']) <= tol_px
                            for px, py in samples])
        if len(cpts):
            dd = np.hypot(samples[:, None, 0] - cpts[None, :, 0],
                          samples[:, None, 1] - cpts[None, :, 1]).min(1)
            ok |= dd <= max(tol_px, 2 * tol_px)  # arcos marcados com poucos pontos
        m.det_corretas += bool(ok.mean() >= min_cover)
    return m


def gt_ellipse(img_gt: Dict[str, Any]) -> Optional[Tuple[float, float, float, float, float]]:
    """Elipse da verdade de terreno (todos os arcos juntos)."""
    pts = circle_points(img_gt)
    if len(pts) < 5:
        return None
    (cx, cy), (a, b), ang = cv2.fitEllipse(pts.astype(np.float32).reshape(-1, 1, 2))
    if a < b:
        a, b, ang = b, a, ang + 90
    return float(cx), float(cy), float(a), float(b), float(ang % 180)


def ellipse_metrics(dets: Sequence[Any], img_gt: Dict[str, Any]) -> Dict[str, Any]:
    """Centro e eixos da melhor elipse detectada contra a da verdade."""
    ge = gt_ellipse(img_gt)
    if ge is None:
        return {'gt': False, 'det': len(dets)}
    if not dets:
        return {'gt': True, 'det': 0, 'acerto': False}
    best = min(dets, key=lambda e: math.hypot(e.cx - ge[0], e.cy - ge[1]))
    dc = math.hypot(best.cx - ge[0], best.cy - ge[1])
    ra = best.eixo_maior / ge[2]
    rb = best.eixo_menor / ge[3] if ge[3] > 0 else 0.0
    ok = dc <= 0.15 * ge[2] and 0.8 <= ra <= 1.25
    return {'gt': True, 'det': len(dets), 'dist_centro_px': round(dc, 1), 'razao_eixo_maior': round(ra, 3),
            'razao_eixo_menor': round(rb, 3), 'acerto': bool(ok)}
