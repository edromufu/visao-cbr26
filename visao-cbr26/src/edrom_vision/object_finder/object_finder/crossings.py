"""
IV-A — Detecção de cruzamentos (L, T, X) a partir do grafo de nós.

Sequência do artigo (Seção IV-A):

1. suavizar as linhas (nós de grau 2 andam para a média dos vizinhos,
   sempre recolocados **sobre o esqueleto**);
2. eliminar linhas curtas que terminam em junções (pontas de ruído);
3. remover nós em locais de baixa curvatura (sobra a estrutura de nós-chave,
   Fig. 2d);
4. fundir junções próximas e conectadas num só cruzamento (o nó novo vai
   para o pixel de esqueleto mais próximo);
5. tipo pelo grau: 2 com ângulo característico = L, 3 = T, 4 = X;
6. verificação nas imagens subamostradas: máquina de estados
   verde→branco→verde num círculo centrado no cruzamento, e caminho branco
   do cruzamento até os vizinhos em cada direção.

Checagens geométricas extras (documentadas em ``docs/decisoes.md``): o T
precisa de um par de braços colineares e o X de dois (retas continuam retas
em perspectiva); o L precisa de curvatura concentrada no vértice (um arco do
círculo central, ao contrário, tem curvatura espalhada).
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .features import CrossingFeature
from .graph_nodes import _unit, angle_between, bilinear, NodeGraph

Pos = Tuple[float, float]


@dataclass
class CrossingParams:
    """Parâmetros da IV-A (unidades: células da grade, graus)."""

    spur_max_len: float = 3.5          # linha curta terminando em junção
    low_curv_deg: float = 25.0         # nós com desvio menor que isto somem
    merge_dist: float = 4.0            # junções conectadas mais próximas que isto
    collinear_deg: float = 150.0       # par de braços "em linha reta"
    l_min_angle: float = 30.0          # ângulo interno do L (perspectiva)
    l_max_angle: float = 150.0
    l_concentration: float = 0.6       # giro curto / giro longo (vértice x arco)
    arm_short: float = 2.5
    arm_long: float = 6.0
    min_arm_len: float = 2.5           # braço mínimo (células)
    ray_len: float = 4.0               # distância para medir a direção do raio
    circle_radii: Tuple[float, ...] = (2.0, 3.0, 4.0)
    white_frac: float = 0.35           # limiar do branco relativo ao centro
    white_min: float = 20.0
    green_min: float = 100.0
    path_len: float = 6.0
    path_min_frac: float = 0.75
    require_both: bool = True          # artigo: as duas verificações
    curve_run: int = 3                 # cantos seguidos no mesmo sentido = curva
    complete_x: bool = True            # T com 4 faixas no círculo + branco oposto = X
    smooth: bool = True


class _KeyGraph:
    """Grafo de nós-chave com a polilinha fina de cada aresta."""

    def __init__(self, g: NodeGraph) -> None:
        self.g = g.copy()
        self.fine = dict(self.g.pos)  # posições finas (congeladas após suavizar)
        self.path: Dict[Tuple[int, int], List[int]] = {}
        for a, b in self.g.edges():
            self.path[(a, b)] = [a, b]

    def get_path(self, a: int, b: int) -> List[int]:
        if (a, b) in self.path:
            return self.path[(a, b)]
        return list(reversed(self.path[(b, a)]))

    def set_path(self, a: int, b: int, p: List[int]) -> None:
        self.path.pop((a, b), None)
        self.path.pop((b, a), None)
        self.path[(a, b)] = p

    def drop_path(self, a: int, b: int) -> None:
        self.path.pop((a, b), None)
        self.path.pop((b, a), None)

    def pts(self, ids: Sequence[int]) -> np.ndarray:
        return np.array([self.fine[i] for i in ids], float)

    def arm_polyline(self, n: int, m: int, max_len: float = 1e9) -> np.ndarray:
        """Polilinha fina saindo de n em direção a m (continua por nós de grau 2)."""
        out = [self.g.pos[n]]
        prev, cur, total = n, m, 0.0
        while True:
            seg = self.get_path(prev, cur)
            for i in seg[1:]:
                p = self.fine[i] if i != cur else self.g.pos[cur]
                total += math.hypot(p[0] - out[-1][0], p[1] - out[-1][1])
                out.append(p)
                if total >= max_len:
                    return np.array(out)
            if self.g.degree(cur) != 2:
                return np.array(out)
            nxt = [k for k in self.g.neighbors(cur) if k != prev]
            if not nxt or nxt[0] == n:
                return np.array(out)
            prev, cur = cur, nxt[0]


def _point_at(poly: np.ndarray, dist: float) -> Tuple[Pos, float]:
    """Ponto a ``dist`` ao longo da polilinha (ou o último) e o comprimento real."""
    acc = 0.0
    for i in range(1, len(poly)):
        seg = float(np.hypot(*(poly[i] - poly[i - 1])))
        if acc + seg >= dist and seg > 0:
            t = (dist - acc) / seg
            p = poly[i - 1] + t * (poly[i] - poly[i - 1])
            return (float(p[0]), float(p[1])), dist
        acc += seg
    return (float(poly[-1][0]), float(poly[-1][1])), acc


def _snap(skeleton: np.ndarray, q: Pos, radius: int = 1) -> Optional[Tuple[int, int]]:
    """Pixel de esqueleto mais próximo de q (Chebyshev <= radius)."""
    h, w = skeleton.shape
    cx, cy = int(round(q[0])), int(round(q[1]))
    best, bd = None, 1e9
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            x, y = cx + dx, cy + dy
            if 0 <= x < w and 0 <= y < h and skeleton[y, x]:
                d = math.hypot(x - q[0], y - q[1])
                if d < bd:
                    best, bd = (x, y), d
    return best


def _smooth(k: _KeyGraph, skeleton: np.ndarray) -> None:
    g = k.g
    newpos = {}
    for n in g.nodes():
        if g.degree(n) != 2:
            continue
        a, b = g.neighbors(n)
        p, pa, pb = g.pos[n], g.pos[a], g.pos[b]
        q = ((pa[0] + 2 * p[0] + pb[0]) / 4.0, (pa[1] + 2 * p[1] + pb[1]) / 4.0)
        s = _snap(skeleton, q, 1)
        if s is not None:
            newpos[n] = (float(s[0]), float(s[1]))
    for n, p in newpos.items():
        g.pos[n] = p
        k.fine[n] = p


def _walk_to_junction(g: NodeGraph, e: int) -> Tuple[List[int], int, float]:
    chain, prev, cur = [e], e, g.neighbors(e)[0]
    length = g.dist(e, cur)
    while g.degree(cur) == 2:
        nxt = [x for x in g.neighbors(cur) if x != prev]
        if not nxt or nxt[0] == e:
            break
        chain.append(cur)
        prev, cur = cur, nxt[0]
        length += g.dist(prev, cur)
    return chain, cur, length


def _remove_spurs(k: _KeyGraph, max_len: float) -> bool:
    g, changed = k.g, False
    again = True
    while again:
        again = False
        for e in g.nodes():
            if e not in g.adj or g.degree(e) != 1:
                continue
            chain, end, length = _walk_to_junction(g, e)
            if g.degree(end) >= 3 and length < max_len:
                for n in chain:
                    for m in list(g.adj[n]):
                        k.drop_path(n, m)
                    g.remove_node(n)
                again = changed = True
    return changed


def _turn(g: NodeGraph, n: int) -> float:
    a, b = g.neighbors(n)
    p = g.pos[n]
    ang = angle_between((g.pos[a][0] - p[0], g.pos[a][1] - p[1]),
                        (g.pos[b][0] - p[0], g.pos[b][1] - p[1]))
    return 180.0 - ang


def _simplify(k: _KeyGraph, low_curv: float) -> bool:
    g, changed = k.g, False
    while True:
        best, bt = None, low_curv
        for n in g.nodes():
            if g.degree(n) == 2:
                a, b = g.neighbors(n)
                if b in g.adj[a]:
                    continue  # não criar aresta duplicada (triângulo)
                t = _turn(g, n)
                if t < bt:
                    best, bt = n, t
        if best is None:
            return changed
        a, b = g.neighbors(best)
        p = k.get_path(a, best) + k.get_path(best, b)[1:]
        k.drop_path(a, best)
        k.drop_path(best, b)
        g.remove_node(best)
        g.add_edge(a, b)
        k.set_path(a, b, p)
        changed = True


def _merge(k: _KeyGraph, skeleton: np.ndarray, merge_dist: float, relief: np.ndarray) -> bool:
    g, changed = k.g, False
    while True:
        cands = []
        for a, b in g.edges():
            da, db = g.degree(a), g.degree(b)
            if da < 2 or db < 2 or (da == 2 and db == 2 and not _same_turn(g, a, b)):
                continue
            if da == 2 and db == 2:
                pass
            elif max(da, db) < 3:
                continue
            d = g.dist(a, b)
            if d < merge_dist:
                cands.append((d, a, b))
        if not cands:
            return changed
        _, a, b = min(cands)
        q = _merge_point(g, a, b)
        s = _snap(skeleton, q, 2) or (int(round(q[0])), int(round(q[1])))
        nbrs = [(m, k.get_path(a, m)) for m in g.neighbors(a) if m != b] + \
               [(m, k.get_path(b, m)) for m in g.neighbors(b) if m != a]
        new = g.add_node(float(s[0]), float(s[1]), float(relief[s[1], s[0]]), 'fundido')
        k.fine[new] = (float(s[0]), float(s[1]))
        for m in list(g.adj[a]):
            k.drop_path(a, m)
        for m in list(g.adj[b]):
            k.drop_path(b, m)
        g.remove_node(a)
        g.remove_node(b)
        for m, p in nbrs:
            if m in g.adj and m != new and m not in g.adj[new]:
                g.add_edge(new, m)
                k.set_path(new, m, [new] + p[1:])
        changed = True


def _same_turn(g: NodeGraph, a: int, b: int) -> bool:
    """Dois cantos vizinhos girando para o mesmo lado (canto arredondado)."""
    def cross(n: int) -> float:
        x, y = g.neighbors(n)
        p = g.pos[n]
        u = (p[0] - g.pos[x][0], p[1] - g.pos[x][1])
        v = (g.pos[y][0] - p[0], g.pos[y][1] - p[1])
        if x == b or x == a:
            u, v = (g.pos[y][0] - p[0], g.pos[y][1] - p[1]
                    ), (p[0] - g.pos[x][0], p[1] - g.pos[x][1])
            u, v = (-u[0], -u[1]), (-v[0], -v[1])
        return u[0] * v[1] - u[1] * v[0]
    # orientação consistente: percorre a -> b
    oa = [m for m in g.neighbors(a) if m != b][0]
    ob = [m for m in g.neighbors(b) if m != a][0]
    p0, p1, p2, p3 = g.pos[oa], g.pos[a], g.pos[b], g.pos[ob]
    c1 = (p1[0] - p0[0]) * (p2[1] - p1[1]) - (p1[1] - p0[1]) * (p2[0] - p1[0])
    c2 = (p2[0] - p1[0]) * (p3[1] - p2[1]) - (p2[1] - p1[1]) * (p3[0] - p2[0])
    del cross
    return c1 * c2 > 0


def _merge_point(g: NodeGraph, a: int, b: int) -> Pos:
    """Ponto de fusão: interseção das arestas externas (cantos) ou ponto médio."""
    pa, pb = g.pos[a], g.pos[b]
    mid = ((pa[0] + pb[0]) / 2.0, (pa[1] + pb[1]) / 2.0)
    if g.degree(a) == 2 and g.degree(b) == 2:
        oa = [m for m in g.neighbors(a) if m != b][0]
        ob = [m for m in g.neighbors(b) if m != a][0]
        p = _intersect(g.pos[oa], pa, g.pos[ob], pb)
        if p is not None and math.hypot(p[0] - mid[0], p[1] - mid[1]) <= g.dist(a, b):
            return p
        return mid
    # junções: o nó mais claro (pico do relevo) marca o centro do cruzamento
    return pa if g.gray[a] >= g.gray[b] else pb


def _intersect(p1: Pos, p2: Pos, q1: Pos, q2: Pos) -> Optional[Pos]:
    d1 = (p2[0] - p1[0], p2[1] - p1[1])
    d2 = (q2[0] - q1[0], q2[1] - q1[1])
    den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) < 1e-9:
        return None
    t = ((q1[0] - p1[0]) * d2[1] - (q1[1] - p1[1]) * d2[0]) / den
    return (p1[0] + t * d1[0], p1[1] + t * d1[1])


def keynode_graph(g: NodeGraph, s1: Any, p: CrossingParams) -> _KeyGraph:
    """Passos 1-4: estrutura de nós-chave (Fig. 2d)."""
    k = _KeyGraph(g)
    if p.smooth:
        _smooth(k, s1.skeleton)
    for _ in range(4):
        c1 = _remove_spurs(k, p.spur_max_len)
        c2 = _simplify(k, p.low_curv_deg)
        c3 = _merge(k, s1.skeleton, p.merge_dist, s1.relief)
        if not (c1 or c2 or c3):
            break
    return k


# ------------------------------------------------------------ verificação
def circle_transitions(white: np.ndarray, green: np.ndarray, center: Pos, r: float,
                       thr_w: float, thr_g: float) -> int:
    """Máquina de estados verde→branco→verde num círculo: nº de faixas brancas."""
    n = max(16, int(math.ceil(2 * math.pi * r * 3)))
    th = np.arange(n) * 2 * math.pi / n
    xs = center[0] + r * np.cos(th)
    ys = center[1] + r * np.sin(th)
    w = bilinear(white, xs, ys)
    gr = bilinear(green, xs, ys)
    labels = np.where(w >= thr_w, 'W', np.where(gr >= thr_g, 'G', 'U'))
    seq = [c for c in labels if c != 'U']
    if not seq or 'G' not in seq or 'W' not in seq:
        return 0
    # gira para começar num G e conta as entradas G->W (estado verde->branco->verde)
    i0 = seq.index('G')
    seq = seq[i0:] + seq[:i0]
    count, state = 0, 'G'
    for c in seq + ['G']:
        if state == 'G' and c == 'W':
            state = 'W'
        elif state == 'W' and c == 'G':
            count += 1
            state = 'G'
    return count


def white_path_ok(white: np.ndarray, poly: np.ndarray, length: float, thr: float,
                  min_frac: float) -> Tuple[bool, float]:
    """Caminho branco do cruzamento ao longo do braço (até ``length``)."""
    samples = []
    d = 0.5
    while d <= length:
        q, real = _point_at(poly, d)
        if real < d - 1e-6:
            break
        samples.append(q)
        d += 0.5
    if not samples:
        return False, 0.0
    xs = np.array([s[0] for s in samples])
    ys = np.array([s[1] for s in samples])
    frac = float((bilinear(white, xs, ys) >= thr).mean())
    return frac >= min_frac, frac


def _ray_angle(s1: Any, c: Pos, q: Pos) -> float:
    ci = s1.grid_to_image(*c)
    qi = s1.grid_to_image(*q)
    return float(math.atan2(qi[1] - ci[1], qi[0] - ci[0]) % (2 * math.pi))


def _classify(dirs: List[Tuple[float, float]], deg: int, p: CrossingParams) -> Optional[str]:
    pairs = [(i, j) for i in range(deg) for j in range(i + 1, deg)
             if angle_between(dirs[i], dirs[j]) >= p.collinear_deg]
    if deg == 2:
        ang = angle_between(dirs[0], dirs[1])
        return 'L' if p.l_min_angle <= ang <= p.l_max_angle else None
    if deg == 3:
        return 'T' if pairs else None
    if deg == 4:
        for a in pairs:
            for b in pairs:
                if len({*a, *b}) == 4:
                    return 'X'
    return None


def _turn_sign(g: NodeGraph, n: int, prev: int) -> float:
    nxt = [m for m in g.neighbors(n) if m != prev][0]
    p0, p1, p2 = g.pos[prev], g.pos[n], g.pos[nxt]
    return (p1[0] - p0[0]) * (p2[1] - p1[1]) - (p1[1] - p0[1]) * (p2[0] - p1[0])


def _curve_runs(g: NodeGraph, min_run: int) -> set:
    """
    Nós de grau 2 em sequências de >= ``min_run`` cantos girando para o mesmo lado.

    É a assinatura de uma curva (círculo central poligonizado), não de um L:
    num retângulo (área do gol) os cantos vêm no máximo aos pares entre junções.
    """
    out: set = set()
    seen: set = set()
    for start in g.nodes():
        if g.degree(start) != 2 or start in seen:
            continue
        # anda até a ponta da cadeia de nós de grau 2
        chain = [start]
        for direction in (0, 1):
            prev, cur = start, g.neighbors(start)[direction]
            part = []
            while g.degree(cur) == 2 and cur not in chain and cur not in part:
                part.append(cur)
                nxt = [m for m in g.neighbors(cur) if m != prev]
                prev, cur = cur, nxt[0]
            chain = (list(reversed(part)) + chain) if direction == 0 else (chain + part)
        seen.update(chain)
        if len(chain) < min_run:
            continue
        # sinais do giro ao longo da cadeia (mesma orientação de percurso)
        signs = []
        for i, n in enumerate(chain):
            prev = chain[i - 1] if i > 0 else [m for m in g.neighbors(n) if m not in chain[1:2]][0]
            signs.append(np.sign(_turn_sign(g, n, prev)))
        run = [chain[0]]
        for i in range(1, len(chain)):
            if signs[i] == signs[i - 1] and signs[i] != 0:
                run.append(chain[i])
            else:
                if len(run) >= min_run:
                    out.update(run)
                run = [chain[i]]
        if len(run) >= min_run:
            out.update(run)
    return out


def detect_crossings(g: NodeGraph, s1: Any, params: Optional[CrossingParams] = None,
                     keygraph: Optional[_KeyGraph] = None,
                     on_ellipse: Optional[Any] = None,
                     rejected: Optional[List[Dict[str, Any]]] = None) -> List[CrossingFeature]:
    """
    IV-A completa. ``s1`` é o ``Stage1Result`` (imagens subamostradas).

    ``on_ellipse(x, y) -> bool`` (opcional) descarta candidatos a L sobre o
    círculo central já ajustado na IV-B.
    """
    p = params or CrossingParams()
    k = keygraph or keynode_graph(g, s1, p)
    kg = k.g
    white = np.asarray(s1.white_resized, np.float32)
    green = np.asarray(s1.green_resized, np.float32)
    out: List[CrossingFeature] = []
    curve_nodes = _curve_runs(kg, p.curve_run)
    for n in kg.nodes():
        deg = kg.degree(n)
        if deg < 2 or deg > 4:
            continue
        c = kg.pos[n]
        arms_long = [k.arm_polyline(n, m, p.arm_long) for m in kg.neighbors(n)]
        arm_lens = [float(np.sum(np.hypot(*np.diff(a, axis=0).T)))
                    if len(a) > 1 else 0.0 for a in arms_long]

        def rej(motivo: str, **kw: Any) -> None:
            if rejected is not None:
                rejected.append({'grade': c, 'grau': deg, 'motivo': motivo, **kw})
        if min(arm_lens) < p.min_arm_len:
            rej('braco_curto', bracos=arm_lens)
            continue
        dirs = []
        for a in arms_long:
            q, _ = _point_at(a, p.ray_len)
            dirs.append(_unit(q[0] - c[0], q[1] - c[1]))
        tipo = _classify(dirs, deg, p)
        if tipo is None:
            rej('geometria', angulos=[round(angle_between(dirs[i], dirs[j]))
                for i in range(deg) for j in range(i + 1, deg)])
            continue
        info: Dict[str, Any] = {'grau': deg, 'bracos': [round(x, 2) for x in arm_lens]}
        if tipo == 'L' and n in curve_nodes:
            rej('curva')
            continue
        if tipo in ('L', 'T') and on_ellipse is not None and on_ellipse(s1.grid_to_image(*c)):
            # sobre o círculo central só há X (com a linha do meio), que vem da
            # extensão reta x elipse; L/T do grafo ali são arcos mal conectados
            rej('sobre_elipse')
            continue
        if tipo == 'L':
            qs = [_point_at(a, p.arm_short)[0] for a in arms_long]
            ql = [_point_at(a, p.arm_long)[0] for a in arms_long]
            t_s = 180.0 - angle_between((qs[0][0] - c[0], qs[0][1] - c[1]),
                                        (qs[1][0] - c[0], qs[1][1] - c[1]))
            t_l = 180.0 - angle_between((ql[0][0] - c[0], ql[0][1] - c[1]),
                                        (ql[1][0] - c[0], ql[1][1] - c[1]))
            conc = t_s / t_l if t_l > 1e-6 else 0.0
            info['concentracao'] = round(conc, 2)
            if min(arm_lens) >= p.arm_long - 0.5 and conc < p.l_concentration:
                rej('L_nao_concentrado', conc=conc)
                continue
        # nível de branco das próprias linhas (mediana ao longo dos braços):
        # o limiar é relativo a ele, para funcionar com linhas finas/distantes
        levels = []
        for a, L in zip(arms_long, arm_lens):
            qs = [_point_at(a, d)[0] for d in np.arange(
                1.0, max(1.5, min(p.path_len, L)) + 1e-6, 0.5)]
            levels.append(float(np.median(bilinear(white, np.array(
                [q[0] for q in qs]), np.array([q[1] for q in qs])))))
        level = float(np.median(levels))
        thr_w = max(p.white_min, p.white_frac * level)
        # verificação 1: círculo verde->branco->verde
        counts = [circle_transitions(white, green, c, r, thr_w, p.green_min)
                  for r in p.circle_radii]
        circ_ok = deg in counts
        # verificação 2: caminho branco em cada direção
        paths = [white_path_ok(white, a, min(p.path_len, L), thr_w, p.path_min_frac)
                 for a, L in zip(arms_long, arm_lens)]
        path_ok = all(ok for ok, _ in paths)
        info.update({'circulo': bool(circ_ok), 'transicoes': counts, 'nivel_branco': round(level, 1),
                     'caminho_branco': bool(path_ok), 'frac_caminho': [round(f, 2) for _, f in paths]})
        extra_ray = None
        if tipo == 'T' and p.complete_x and 4 in counts and path_ok:
            # o 4º braço (oposto à haste) pode ter sumido do esqueleto (linha fraca
            # cruzando uma forte): confirma pelo branco na direção oposta
            pair = [(i, j) for i in range(3) for j in range(i + 1, 3)
                    if angle_between(dirs[i], dirs[j]) >= p.collinear_deg][0]
            stem = ({0, 1, 2} - set(pair)).pop()
            opp = (-dirs[stem][0], -dirs[stem][1])
            line = np.array([[c[0] + opp[0] * t, c[1] + opp[1] * t]
                            for t in np.arange(0, p.path_len + 0.5, 0.5)])
            ok4, f4 = white_path_ok(white, line, p.path_len, thr_w, p.path_min_frac)
            info['x_completado'] = bool(ok4)
            if ok4:
                tipo, circ_ok = 'X', True
                extra_ray = (c[0] + opp[0] * p.ray_len, c[1] + opp[1] * p.ray_len)
        if (p.require_both and not (circ_ok and path_ok)) or not (circ_ok or path_ok):
            rej('verificacao', tipo=tipo, **info)
            continue
        conf = 0.5 + 0.25 * circ_ok + 0.25 * path_ok
        conf *= min(1.0, 0.6 + 0.4 * min(arm_lens) / p.arm_long)
        rays = [_ray_angle(s1, c, _point_at(a, p.ray_len)[0]) for a in arms_long]
        if extra_ray is not None:
            rays.append(_ray_angle(s1, c, extra_ray))
        rays = sorted(rays)
        x, y = s1.grid_to_image(*c)
        out.append(CrossingFeature(tipo=tipo, x=float(x), y=float(y), heading_rays=rays,
                                   confianca=round(float(conf), 3), verificacao=info,
                                   grade=(float(c[0]), float(c[1]))))
    out.sort(key=lambda f: (f.y, f.x))
    return out


# ----------------------------------------------------------------------------
# Extensão (não está no artigo): candidatos a partir das retas da IV-B e da
# elipse do círculo central. Mesma verificação da IV-A (círculo verde->branco->
# verde e caminho branco). Motivo medido (docs/decisoes.md): o operador de
# ranking apaga a linha fina perto de uma linha grossa, então a junção some do
# grafo, mas as duas retas continuam bem ajustadas.
# ----------------------------------------------------------------------------
@dataclass
class LineCrossingParams:
    """Parâmetros da extensão (células da grade)."""

    min_angle_deg: float = 20.0     # retas quase paralelas não cruzam
    end_tol: float = 2.5            # "termina no cruzamento" se a ponta está a até isto
    gap_tol: float = 3.0            # a interseção pode ficar até isto além da ponta
    dedupe_dist: float = 2.5        # mesmo cruzamento do grafo
    ellipse_pass_tol: float = 2.0


def _verify_dirs(s1: Any, c: Pos, dirs: List[Tuple[float, float]], p: CrossingParams,
                 lens: Optional[List[float]] = None) -> Tuple[bool, bool, Dict[str, Any]]:
    """Verificação da IV-A com braços retos nas direções dadas (grade)."""
    white = np.asarray(s1.white_resized, np.float32)
    green = np.asarray(s1.green_resized, np.float32)
    lens = lens or [p.path_len] * len(dirs)
    polys = [np.array([[c[0] + d[0] * t, c[1] + d[1] * t] for t in np.arange(0, Lk + 0.5, 0.5)])
             for d, Lk in zip(dirs, lens)]
    levels = []
    for a in polys:
        qs = a[2:]
        levels.append(float(np.median(bilinear(white, qs[:, 0], qs[:, 1]))))
    level = float(np.median(levels))
    thr = max(p.white_min, p.white_frac * level)
    counts = [circle_transitions(white, green, c, r, thr, p.green_min) for r in p.circle_radii]
    paths = [white_path_ok(white, a, Lk, thr, p.path_min_frac) for a, Lk in zip(polys, lens)]
    circ_ok = len(dirs) in counts
    path_ok = all(ok for ok, _ in paths)
    return circ_ok, path_ok, {'circulo': bool(circ_ok), 'transicoes': counts, 'nivel_branco': round(level, 1),
                              'caminho_branco': bool(path_ok), 'frac_caminho': [round(f, 2) for _, f in paths]}


def _in_field(s1: Any, c: Pos) -> bool:
    fm = getattr(s1, 'field_mask', None)
    if fm is None:
        return True
    h, w = fm.shape
    x, y = int(round(c[0])), int(round(c[1]))
    return 0 <= x < w and 0 <= y < h and bool(fm[y, x])


def crossings_from_lines(lines: Sequence[Any], ellipses: Sequence[Any], s1: Any,
                         p: Optional[CrossingParams] = None,
                         lp: Optional[LineCrossingParams] = None) -> List[CrossingFeature]:
    """Cruzamentos pela interseção de retas (L/T/X) e de reta com a elipse (X)."""
    p = p or CrossingParams()
    lp = lp or LineCrossingParams()
    sx, sy = s1.scale
    segs = []
    for ln in lines:
        a = np.array(s1.image_to_grid(ln.x1, ln.y1))
        b = np.array(s1.image_to_grid(ln.x2, ln.y2))
        L = float(np.hypot(*(b - a)))
        if L < 1e-6:
            continue
        segs.append((a, b, (b - a) / L, L))
    out: List[CrossingFeature] = []
    min_ang = math.radians(lp.min_angle_deg)
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            a1, b1, d1, L1 = segs[i]
            a2, b2, d2, L2 = segs[j]
            cr = d1[0] * d2[1] - d1[1] * d2[0]
            if abs(cr) < math.sin(min_ang):
                continue
            w = a2 - a1
            t1 = (w[0] * d2[1] - w[1] * d2[0]) / cr
            t2 = (w[0] * d1[1] - w[1] * d1[0]) / cr
            if not (-lp.gap_tol <= t1 <= L1 + lp.gap_tol and -lp.gap_tol <= t2 <= L2 + lp.gap_tol):
                continue
            c = tuple(a1 + t1 * d1)
            if not _in_field(s1, c):
                continue
            dirs: List[Tuple[float, float]] = []
            ends = 0
            for (t, d, L) in ((t1, d1, L1), (t2, d2, L2)):
                at_start, at_end = t <= lp.end_tol, t >= L - lp.end_tol
                if at_start and at_end:
                    dirs = []
                    break
                if at_start:
                    dirs.append((float(d[0]), float(d[1])))
                    ends += 1
                elif at_end:
                    dirs.append((float(-d[0]), float(-d[1])))
                    ends += 1
                else:
                    dirs += [(float(d[0]), float(d[1])), (float(-d[0]), float(-d[1]))]
            if not dirs:
                continue
            tipo = {2: 'L', 3: 'T', 4: 'X'}[len(dirs)]
            if tipo == 'L':
                ang = angle_between(dirs[0], dirs[1])
                if not (p.l_min_angle <= ang <= p.l_max_angle):
                    continue
            circ_ok, path_ok, info = _verify_dirs(s1, c, dirs, p)
            if (p.require_both and not (circ_ok and path_ok)) or not (circ_ok or path_ok):
                continue
            conf = 0.5 + 0.25 * circ_ok + 0.25 * path_ok
            x, y = s1.grid_to_image(*c)
            rays = sorted(float(math.atan2(d[1] * sy, d[0] * sx) % (2 * math.pi)) for d in dirs)
            info.update({'retas': [i, j]})
            out.append(CrossingFeature(tipo, float(x), float(y), rays, round(conf, 3), fonte='retas',
                                       verificacao=info, grade=(float(c[0]), float(c[1]))))
    # reta x elipse (círculo central cortado pela linha do meio)
    for e in ellipses:
        ex, ey = s1.image_to_grid(e.cx, e.cy)
        A, B = e.eixo_maior / 2.0 / sx, e.eixo_menor / 2.0 / sy
        th = math.radians(e.angulo_graus)
        ct, st = math.cos(th), math.sin(th)
        for (a, b, d, L) in segs:
            # reta em coordenadas da elipse
            p0 = a - [ex, ey]
            u0 = np.array([p0[0] * ct + p0[1] * st, -p0[0] * st + p0[1] * ct])
            du = np.array([d[0] * ct + d[1] * st, -d[0] * st + d[1] * ct])
            qa = (du[0] / A) ** 2 + (du[1] / B) ** 2
            qb = 2 * (u0[0] * du[0] / A ** 2 + u0[1] * du[1] / B ** 2)
            qc = (u0[0] / A) ** 2 + (u0[1] / B) ** 2 - 1
            disc = qb * qb - 4 * qa * qc
            if disc <= 0:
                continue
            for t in ((-qb - math.sqrt(disc)) / (2 * qa), (-qb + math.sqrt(disc)) / (2 * qa)):
                if not (-lp.gap_tol <= t <= L + lp.gap_tol):
                    continue
                c = tuple(a + t * d)
                if not _in_field(s1, c):
                    continue
                # tangente da elipse no ponto
                u = u0 + t * du
                tang_e = np.array([-u[1] / B ** 2, u[0] / A ** 2])
                tang_e = tang_e / (np.hypot(*tang_e) + 1e-12)
                tg = (tang_e[0] * ct - tang_e[1] * st, tang_e[0] * st + tang_e[1] * ct)
                cross_ang = angle_between(tg, (d[0], d[1]))
                if cross_ang < lp.min_angle_deg or cross_ang > 180 - lp.min_angle_deg:
                    continue
                dirs = [(float(tg[0]), float(tg[1])), (float(-tg[0]), float(-tg[1]))]
                if t > lp.end_tol:
                    dirs.append((float(-d[0]), float(-d[1])))
                if t < L - lp.end_tol:
                    dirs.append((float(d[0]), float(d[1])))
                if len(dirs) < 3:
                    continue
                tipo = 'X' if len(dirs) == 4 else 'T'
                # braços da elipse são curvos: caminho branco curto ao longo da tangente
                lens = [min(p.path_len, 3.0)] * 2 + [p.path_len] * (len(dirs) - 2)
                circ_ok, path_ok, info = _verify_dirs(s1, c, dirs, p, lens)
                if tipo == 'T' and 4 in info['transicoes']:
                    # a reta continua do outro lado (linha fraca que sumiu): vira X
                    opp = [(-dd[0], -dd[1]) for dd in dirs[2:]]
                    ok4, path4, _ = _verify_dirs(s1, c, dirs + opp, p, lens + [p.path_len])
                    if ok4 and path4:
                        tipo, dirs, circ_ok = 'X', dirs + opp, True
                if (p.require_both and not (circ_ok and path_ok)) or not (circ_ok or path_ok):
                    continue
                x, y = s1.grid_to_image(*c)
                rays = sorted(float(math.atan2(dd[1] * sy, dd[0] * sx) %
                              (2 * math.pi)) for dd in dirs)
                info.update({'elipse': True})
                out.append(CrossingFeature(tipo, float(x), float(y), rays,
                                           round(0.5 + 0.25 * circ_ok + 0.25 * path_ok, 3), fonte='retas',
                                           verificacao=info, grade=(float(c[0]), float(c[1]))))
    # remove duplicatas entre si (mesmo ponto)
    final: List[CrossingFeature] = []
    for c in sorted(out, key=lambda k: (-k.confianca, -len(k.heading_rays))):
        if all(math.hypot(c.x - f.x, c.y - f.y) > lp.dedupe_dist * sx for f in final):
            final.append(c)
    final.sort(key=lambda f: (f.y, f.x))
    return final


def combine_crossings(graph_cr: Sequence[CrossingFeature], line_cr: Sequence[CrossingFeature], s1: Any,
                      lp: Optional[LineCrossingParams] = None) -> List[CrossingFeature]:
    """União: o do grafo tem prioridade; o das retas confirma ou completa."""
    lp = lp or LineCrossingParams()
    rad = lp.dedupe_dist * float(np.mean(s1.scale))
    out = list(graph_cr)
    for lc in line_cr:
        near = [g for g in out if math.hypot(g.x - lc.x, g.y - lc.y) <= rad]
        if not near:
            out.append(lc)
            continue
        g = min(near, key=lambda k: math.hypot(k.x - lc.x, k.y - lc.y))
        if g.tipo == lc.tipo and g.fonte == 'grafo':
            g.verificacao['confirmado_por_retas'] = True
    out.sort(key=lambda f: (f.y, f.x))
    return out
