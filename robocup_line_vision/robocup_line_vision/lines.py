"""
IV-B — Extração de linhas do campo (split-and-merge) e do círculo central.

Fiel ao artigo (Seção IV-B):

* parte do grafo fino da III-C (Fig. 2c);
* uma linha é um conjunto conexo de nós de **grau 2** mais os nós de outro
  grau ligados diretamente ao conjunto;
* as coordenadas dos nós são **corrigidas da distorção** antes do ajuste;
* **split**: ajuste por mínimos quadrados; o nó mais distante da reta divide
  o componente se a distância for grande; recursivo; componentes com menos de
  3 nós são descartados;
* **merge**: componentes com parâmetros de reta parecidos são unidos;
* extremos finais = **projeção dos extremos do componente na reta ajustada**;
* com modelo de câmera, as linhas vão ao chão: (distância, ângulo).

Mínimos quadrados *totais* (PCA) em vez de regressão y(x), para funcionar com
linhas verticais (documentado em ``docs/decisoes.md``).

Extra (o artigo não trata): o círculo central vira uma cadeia de nós de grau 2
que o split corta em pedaços curtos; cadeias curvas que juntas cabem numa
elipse viram ``EllipseFeature`` (``ellipses`` de ``MarkingArray``) e saem da
lista de linhas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, List, Optional, Sequence, Set, Tuple

import cv2
import numpy as np

from .camera_model import CameraModel
from .features import EllipseFeature, LineFeature
from .graph_nodes import NodeGraph


@dataclass
class LineParams:
    """Parâmetros da IV-B (distâncias em células da grade; multiplicadas pela escala)."""

    split_dist: float = 0.9            # distância nó-reta que provoca divisão
    min_nodes: int = 3                 # artigo: descartar componentes com < 3 nós
    merge_angle_deg: float = 4.0       # retas "parecidas": ângulo
    merge_dist: float = 1.0            # ... e extremos a menos disto da outra reta
    min_length: float = 3.0            # linha final mínima (células)
    ellipse_min_nodes: int = 6
    curve_rms: float = 0.6             # rms da reta acima disto = cadeia curva
    ellipse_rms: float = 0.6           # rms máximo do ajuste de elipse
    ellipse_min_span_deg: float = 120.0
    ellipse_max_axis_ratio: float = 60.0


@dataclass
class Segment:
    """Segmento ajustado por mínimos quadrados totais."""

    pts: np.ndarray
    c: np.ndarray = field(default_factory=lambda: np.zeros(2))
    d: np.ndarray = field(default_factory=lambda: np.array([1.0, 0.0]))
    n: int = 0
    rms: float = 0.0

    @staticmethod
    def fit(pts: np.ndarray) -> 'Segment':
        """Ajuste PCA (reta que minimiza a soma das distâncias perpendiculares²)."""
        pts = np.asarray(pts, float)
        c = pts.mean(axis=0)
        if len(pts) >= 2:
            _, _, vt = np.linalg.svd(pts - c, full_matrices=False)
            d = vt[0]
        else:
            d = np.array([1.0, 0.0])
        if d[0] < 0 or (abs(d[0]) < 1e-12 and d[1] < 0):
            d = -d
        s = Segment(pts, c, d, len(pts))
        s.rms = float(np.sqrt(np.mean(s.distances() ** 2))) if len(pts) else 0.0
        return s

    @property
    def normal(self) -> np.ndarray:
        """Normal unitária."""
        return np.array([-self.d[1], self.d[0]])

    def distances(self, pts: Optional[np.ndarray] = None) -> np.ndarray:
        """Distâncias perpendiculares (com sinal) dos pontos à reta."""
        p = self.pts if pts is None else np.asarray(pts, float)
        return (p - self.c) @ self.normal

    def endpoints(self, ordered: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """Extremos projetados na reta: do 1º/último ponto (ordenado) ou dos extremos."""
        t = (self.pts - self.c) @ self.d
        if ordered:
            t0, t1 = t[0], t[-1]
        else:
            t0, t1 = t.min(), t.max()
        return self.c + t0 * self.d, self.c + t1 * self.d

    def angle(self) -> float:
        """Ângulo da direção em [0, π)."""
        return float(math.atan2(self.d[1], self.d[0]) % math.pi)


def degree2_components(g: NodeGraph) -> List[List[int]]:
    """Componentes de nós de grau 2 + nós de outro grau ligados a eles, ordenados."""
    deg2 = {n for n in g.nodes() if g.degree(n) == 2}
    seen: Set[int] = set()
    out: List[List[int]] = []
    for s in sorted(deg2):
        if s in seen:
            continue
        comp, stack = set(), [s]
        while stack:
            u = stack.pop()
            if u in comp:
                continue
            comp.add(u)
            stack.extend(v for v in g.adj[u] if v in deg2 and v not in comp)
        seen |= comp
        # ordenar: começa numa ponta da cadeia (nó com vizinho fora do conjunto ou ciclo)
        ends = [n for n in sorted(comp) if any(v not in comp for v in g.adj[n])]
        start = ends[0] if ends else min(comp)
        order, prev, cur = [start], None, start
        while True:
            nxt = [v for v in sorted(g.adj[cur]) if v in comp and v != prev and v not in order]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
            order.append(cur)
        head = _best_continuation(
            g, order, [v for v in sorted(g.adj[order[0]]) if v not in comp], True)
        tail_c = [v for v in sorted(g.adj[order[-1]]) if v not in comp and v != head]
        tail = _best_continuation(g, order, tail_c, False)
        if head is not None:
            order = [head] + order
        if tail is not None:
            order = order + [tail]
        if not ends and len(order) > 2:
            order.append(order[0])  # ciclo fechado (círculo sem junção)
        out.append(order)
    return out


def _best_continuation(g: NodeGraph, order: List[int], cands: List[int], at_head: bool) -> Optional[int]:
    """Entre os vizinhos de fora, o que melhor continua a direção da cadeia."""
    if not cands:
        return None
    if len(cands) == 1 or len(order) < 2:
        return cands[0]
    a, b = (order[1], order[0]) if at_head else (order[-2], order[-1])
    d = np.subtract(g.pos[b], g.pos[a])
    d = d / (np.hypot(*d) + 1e-9)

    def score(v: int) -> float:
        e = np.subtract(g.pos[v], g.pos[b])
        return -float(e @ d / (np.hypot(*e) + 1e-9))
    return min(cands, key=lambda v: (score(v), v))


def split_and_merge(pts: np.ndarray, p: LineParams, scale: float) -> List[Segment]:
    """Split recursivo de uma cadeia ordenada e merge dos pedaços vizinhos."""
    pts = np.asarray(pts, float)
    segs = _split(pts, p, scale)
    return merge_segments(segs, p, scale)


def _split(pts: np.ndarray, p: LineParams, scale: float) -> List[Segment]:
    if len(pts) < p.min_nodes:
        return []
    s = Segment.fit(pts)
    if len(pts) <= 2:
        return [s]
    dist = np.abs(s.distances())
    k = 1 + int(np.argmax(dist[1:-1]))
    if k <= 1 or k >= len(pts) - 2:
        # o mais distante da reta ajustada caiu na ponta (ex.: um L com braços
        # desiguais): usar a corda evita "descascar" a ponta nó a nó
        chord = pts[-1] - pts[0]
        nrm = np.hypot(*chord)
        if nrm > 1e-9:
            dc = np.abs((pts - pts[0]) @ np.array([-chord[1], chord[0]]) / nrm)
            kc = 1 + int(np.argmax(dc[1:-1]))
            if dc[kc] > p.split_dist * scale:
                k = kc
    if dist[k] > p.split_dist * scale:
        return _split(pts[:k + 1], p, scale) + _split(pts[k:], p, scale)
    return [s]


def merge_segments(segs: List[Segment], p: LineParams, scale: float) -> List[Segment]:
    """
    Une segmentos com parâmetros de reta parecidos (ângulo e deslocamento).

    "Parecidos": ângulo <= ``merge_angle_deg`` e o centróide de cada um a no
    máximo ``merge_dist`` da reta do outro; a união ainda precisa ser uma reta
    (rms <= ``split_dist``), o que evita juntar paralelas próximas.
    """
    segs = list(segs)
    max_ang = math.radians(p.merge_angle_deg)
    refused: Set[Tuple[int, int]] = set()
    ids = list(range(len(segs)))
    next_id = len(segs)
    while True:
        best = None
        for i in range(len(segs)):
            for j in range(i + 1, len(segs)):
                if (min(ids[i], ids[j]), max(ids[i], ids[j])) in refused:
                    continue
                a, b = segs[i], segs[j]
                da = abs(a.angle() - b.angle())
                da = min(da, math.pi - da)
                if da > max_ang:
                    continue
                off = max(abs(float(a.distances(b.c[None])[0])),
                          abs(float(b.distances(a.c[None])[0])))
                if off > p.merge_dist * scale:
                    continue
                cost = da + off / (scale * 100.0)
                if best is None or cost < best[0]:
                    best = (cost, i, j)
        if best is None:
            return segs
        _, i, j = best
        merged = Segment.fit(np.vstack([segs[i].pts, segs[j].pts]))
        if merged.rms > p.split_dist * scale:
            refused.add((min(ids[i], ids[j]), max(ids[i], ids[j])))
            continue
        keep = [k for k in range(len(segs)) if k not in (i, j)]
        segs = [segs[k] for k in keep] + [merged]
        ids = [ids[k] for k in keep] + [next_id]
        next_id += 1


# -------------------------------------------------------------------- elipse
def _ellipse_rms(pts: np.ndarray, e: Tuple) -> Tuple[float, float]:
    """RMS da distância dos pontos à elipse e cobertura angular (graus)."""
    (cx, cy), (MA, ma), ang = e
    if MA <= 1e-6 or ma <= 1e-6:
        return 1e9, 0.0
    poly = cv2.ellipse2Poly((int(round(cx * 16)), int(round(cy * 16))),
                            (max(1, int(round(MA * 8))), max(1, int(round(ma * 8)))),
                            int(round(ang)), 0, 360, 2, ) if False else None
    t = np.linspace(0, 2 * math.pi, 720, endpoint=False)
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    ex = cx + (MA / 2) * np.cos(t) * ca - (ma / 2) * np.sin(t) * sa
    ey = cy + (MA / 2) * np.cos(t) * sa + (ma / 2) * np.sin(t) * ca
    d = np.hypot(pts[:, None, 0] - ex[None], pts[:, None, 1] - ey[None])
    rms = float(np.sqrt(np.mean(d.min(axis=1) ** 2)))
    idx = d.argmin(axis=1)
    angs = np.sort(np.unique(t[idx]))
    if len(angs) < 2:
        return rms, 0.0
    gaps = np.diff(np.concatenate([angs, angs[:1] + 2 * math.pi]))
    del poly
    return rms, float(math.degrees(2 * math.pi - gaps.max()))


def _fit_ellipse(pts: np.ndarray) -> Optional[Tuple]:
    if len(pts) < 5:
        return None
    try:
        e = cv2.fitEllipse(pts.astype(np.float32).reshape(-1, 1, 2))
    except cv2.error:
        return None
    if not all(np.isfinite([e[0][0], e[0][1], e[1][0], e[1][1], e[2]])):
        return None
    return e


def _norm_ellipse(e: Tuple) -> Tuple[float, float, float, float, float]:
    (cx, cy), (a, b), ang = e
    if a < b:
        a, b, ang = b, a, ang + 90.0
    return float(cx), float(cy), float(a), float(b), float(ang % 180.0)


def find_ellipses(chains: List[np.ndarray], p: LineParams, scale: float,
                  shape: Optional[Tuple[int, int]] = None) -> Tuple[List[EllipseFeature], Set[int]]:
    """Arcos curvos que juntos cabem numa elipse. Devolve elipses e índices usados."""
    arcs = []
    for i, pts in enumerate(chains):
        if len(pts) < p.ellipse_min_nodes:
            continue
        if Segment.fit(pts).rms <= p.curve_rms * scale:
            continue
        e = _fit_ellipse(pts)
        if e is None:
            continue
        rms, _ = _ellipse_rms(pts, e)
        if rms <= p.ellipse_rms * scale:
            arcs.append(i)
    used: Set[int] = set()
    out: List[EllipseFeature] = []
    for i in sorted(arcs, key=lambda k: -len(chains[k])):
        if i in used:
            continue
        group = [i]
        for j in sorted(arcs, key=lambda k: -len(chains[k])):
            if j in used or j in group:
                continue
            e = _fit_ellipse(np.vstack([chains[k] for k in group + [j]]))
            if e is None:
                continue
            rms, _ = _ellipse_rms(np.vstack([chains[k] for k in group + [j]]), e)
            if rms <= p.ellipse_rms * scale:
                group.append(j)
        pts = np.vstack([chains[k] for k in group])
        e = _fit_ellipse(pts)
        if e is None:
            continue
        rms, span = _ellipse_rms(pts, e)
        cx, cy, a, b, ang = _norm_ellipse(e)
        if span < p.ellipse_min_span_deg or b <= 0 or a / b > p.ellipse_max_axis_ratio:
            continue
        if shape is not None and not (-a < cx < shape[1] + a and -a < cy < shape[0] + a):
            continue
        # cadeias quase retas (pedaços curtos do círculo) que caem sobre a elipse
        for k, ch in enumerate(chains):
            if k in used or k in group or len(ch) < 3:
                continue
            if _ellipse_rms(ch, e)[0] <= p.ellipse_rms * scale:
                group.append(k)
        used.update(group)
        conf = min(1.0, len(pts) / 30.0) * max(0.0, 1.0 - rms / (p.ellipse_rms * scale + 1e-9) * 0.5)
        out.append(EllipseFeature(cx, cy, a, b, ang, round(conf, 3), len(pts), round(rms, 2)))
    return out, used


def point_on_ellipses(ellipses: Sequence[EllipseFeature], tol_px: float):
    """Função ``(x, y) -> bool`` que diz se o ponto está sobre alguma elipse (± tol)."""
    def f(pt: Tuple[float, float]) -> bool:
        x, y = pt
        for e in ellipses:
            ca, sa = math.cos(math.radians(e.angulo_graus)), math.sin(math.radians(e.angulo_graus))
            dx, dy = x - e.cx, y - e.cy
            u = dx * ca + dy * sa
            v = -dx * sa + dy * ca
            a, b = e.eixo_maior / 2.0, e.eixo_menor / 2.0
            r = math.hypot(u / a, v / b)
            # distância aproximada à curva ao longo do raio
            if r > 0 and abs(math.hypot(u, v) * (1 - 1 / r)) <= tol_px:
                return True
        return False
    return f


# --------------------------------------------------------------------- IV-B
def extract_lines(g: NodeGraph, s1: Any, params: Optional[LineParams] = None,
                  camera: Optional[CameraModel] = None) -> Tuple[List[LineFeature], List[EllipseFeature]]:
    """IV-B completa: linhas (e elipses) a partir do grafo fino."""
    p = params or LineParams()
    scale = float(np.mean(s1.scale))
    comps = degree2_components(g)
    chains = []
    for comp in comps:
        img_pts = np.array([s1.grid_to_image(*g.pos[n]) for n in comp], float)
        if camera is not None:
            img_pts = camera.undistort_points(img_pts)
        chains.append(img_pts)
    ellipses, used = find_ellipses(chains, p, scale, s1.image_shape)
    segs: List[Segment] = []
    for i, pts in enumerate(chains):
        if i in used:
            continue
        segs.extend(_split(pts, p, scale))
    segs = merge_segments(segs, p, scale)
    lines: List[LineFeature] = []
    for s in segs:
        if s.n < p.min_nodes:
            continue
        a, b = s.endpoints(ordered=False)
        if np.hypot(*(b - a)) < p.min_length * scale:
            continue
        conf = min(1.0, s.n / 10.0) * max(0.0, 1.0 - s.rms / (p.split_dist * scale))
        a_img, b_img = (camera.distort_points(
            np.array([a, b])) if camera is not None else np.array([a, b]))
        ln = LineFeature(float(a_img[0]), float(a_img[1]), float(b_img[0]), float(b_img[1]),
                         round(float(conf), 3), int(s.n), round(float(s.rms), 2))
        if camera is not None and camera.can_project:
            pol = camera.line_polar(a, b, undistorted=True)
            if pol is not None:
                ln.distancia_m, ln.angulo_rad, ln.comprimento_m = (round(pol[0], 3), round(pol[1], 4),
                                                                   round(pol[2], 3))
        lines.append(ln)
    if camera is not None:
        for e in ellipses:
            c = camera.distort_points(np.array([[e.cx, e.cy]]))[0]
            e.cx, e.cy = float(c[0]), float(c[1])
    lines.sort(key=lambda ln: -ln.length)
    return lines, ellipses
