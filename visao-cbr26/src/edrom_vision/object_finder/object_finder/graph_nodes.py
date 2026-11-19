"""
III-C — Posicionamento e conexão de nós sobre o esqueleto (grade 1/8).

Fiel ao artigo (Schulz et al., 2009, Seção III-C) e à referência [1]
(Behnke et al., dígitos manuscritos):

1. **Nós**: primeiro nos *picos* do esqueleto (``c(x,y) = 0``), depois nos
   *cumes* (``c = 1`` e ``c = 2``), sempre a pelo menos 2 pixels (Chebyshev)
   de qualquer nó já posto. A ordem é total e explícita (cinza decrescente,
   depois ``c``, ``y``, ``x``) para não depender do desempate do ``argsort``
   (problema medido antes entre versões do numpy).
2. **Conexões locais**: liga dois nós cujas regiões 3x3 se sobrepõem ou se
   tocam *no esqueleto* (há caminho-8 de esqueleto entre eles dentro da união
   das duas regiões). Triângulos (redundância de esqueleto grosso) perdem a
   aresta mais longa.
3. **Informação global**: nós de ponta são *esticados* até o último pixel do
   esqueleto; nós de grau 0 são *divididos* em dois para preencher lacunas;
   *conexões candidatas* são avaliadas por continuidade, fechamento (cinza ao
   longo do segmento parecido com o dos nós) e simplicidade (distância curta).
   Restrições: grau máximo 4 e nenhum cruzamento que não resulte em linhas
   contínuas (junções de grau 3/4 precisam de pares de arestas colineares) nem
   arestas que se cruzam geometricamente.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

from .stage1_adapter import ranking_count

Pos = Tuple[float, float]


@dataclass
class GraphParams:
    """Parâmetros da III-C (unidades: células da grade 1/8)."""

    min_node_distance: int = 2          # artigo: "at least two pixels apart"
    max_degree: int = 4                 # artigo: grau máximo 4
    stretch_radius: int = 2             # alcance para esticar pontas
    candidate_max_dist: float = 7.0     # distância máxima de conexão candidata
    candidate_min_score: float = 0.55   # pontuação mínima para aceitar
    w_continuity: float = 0.4
    w_closure: float = 0.4
    w_simplicity: float = 0.2
    min_closure: float = 0.25           # cinza ao longo / cinza dos nós (mínimo)
    max_turn_deg: float = 50.0          # desvio máximo de direção numa ponta
    collinear_deg: float = 145.0        # ângulo mínimo para considerar colineares
    min_hops_shortcut: int = 5          # não liga nós já próximos no grafo
    edge_first: bool = True             # ponta->aresta antes de ponta->nó


class NodeGraph:
    """Grafo não dirigido de nós com posição (x, y) na grade."""

    def __init__(self) -> None:
        self.pos: Dict[int, Pos] = {}
        self.adj: Dict[int, Set[int]] = {}
        self.gray: Dict[int, float] = {}
        self.kind: Dict[int, str] = {}
        self._next = 0

    # ------------------------------------------------------------ básico
    def add_node(self, x: float, y: float, gray: float = 0.0, kind: str = '') -> int:
        """Acrescenta um nó e devolve o id."""
        n = self._next
        self._next += 1
        self.pos[n] = (float(x), float(y))
        self.adj[n] = set()
        self.gray[n] = float(gray)
        self.kind[n] = kind
        return n

    def remove_node(self, n: int) -> None:
        """Remove o nó e suas arestas."""
        for m in list(self.adj[n]):
            self.adj[m].discard(n)
        del self.adj[n], self.pos[n], self.gray[n], self.kind[n]

    def add_edge(self, a: int, b: int) -> None:
        """Liga ``a`` e ``b``."""
        if a != b:
            self.adj[a].add(b)
            self.adj[b].add(a)

    def remove_edge(self, a: int, b: int) -> None:
        """Desliga ``a`` e ``b``."""
        self.adj[a].discard(b)
        self.adj[b].discard(a)

    def nodes(self) -> List[int]:
        """Ids em ordem crescente."""
        return sorted(self.adj)

    def edges(self) -> List[Tuple[int, int]]:
        """Arestas ``(a, b)`` com ``a < b``, ordenadas."""
        return sorted((a, b) for a in self.adj for b in self.adj[a] if a < b)

    def neighbors(self, n: int) -> List[int]:
        """Vizinhos em ordem crescente."""
        return sorted(self.adj[n])

    def degree(self, n: int) -> int:
        """Grau do nó."""
        return len(self.adj[n])

    def dist(self, a: int, b: int) -> float:
        """Distância euclidiana entre dois nós."""
        (xa, ya), (xb, yb) = self.pos[a], self.pos[b]
        return math.hypot(xb - xa, yb - ya)

    def copy(self) -> 'NodeGraph':
        """Cópia profunda."""
        g = NodeGraph()
        g.pos = dict(self.pos)
        g.adj = {k: set(v) for k, v in self.adj.items()}
        g.gray = dict(self.gray)
        g.kind = dict(self.kind)
        g._next = self._next
        return g

    def hops(self, a: int, b: int, limit: int) -> Optional[int]:
        """Número de arestas entre ``a`` e ``b`` (BFS limitado) ou ``None``."""
        if a == b:
            return 0
        frontier, seen = [a], {a}
        for d in range(1, limit + 1):
            nxt = []
            for u in frontier:
                for v in self.adj[u]:
                    if v == b:
                        return d
                    if v not in seen:
                        seen.add(v)
                        nxt.append(v)
            frontier = nxt
            if not frontier:
                return None
        return None


# ---------------------------------------------------------------- geometria
def _unit(dx: float, dy: float) -> Tuple[float, float]:
    n = math.hypot(dx, dy)
    return (dx / n, dy / n) if n > 1e-9 else (0.0, 0.0)


def angle_between(u: Tuple[float, float], v: Tuple[float, float]) -> float:
    """Ângulo (graus, 0..180) entre dois vetores."""
    a, b = _unit(*u), _unit(*v)
    c = max(-1.0, min(1.0, a[0] * b[0] + a[1] * b[1]))
    return math.degrees(math.acos(c))


def segments_cross(p1: Pos, p2: Pos, q1: Pos, q2: Pos) -> bool:
    """Cruzamento próprio de dois segmentos (sem contar extremos comuns)."""
    def orient(a: Pos, b: Pos, c: Pos) -> float:
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    if p1 in (q1, q2) or p2 in (q1, q2):
        return False
    d1, d2 = orient(q1, q2, p1), orient(q1, q2, p2)
    d3, d4 = orient(p1, p2, q1), orient(p1, p2, q2)
    return (d1 * d2 < 0) and (d3 * d4 < 0)


def sample_along(img: np.ndarray, p: Pos, q: Pos, step: float = 0.5) -> np.ndarray:
    """Valores (bilinear) ao longo do segmento p->q, sem os extremos."""
    L = math.hypot(q[0] - p[0], q[1] - p[1])
    n = max(1, int(L / step))
    ts = (np.arange(1, n) / n) if n > 1 else np.array([0.5])
    xs = p[0] + ts * (q[0] - p[0])
    ys = p[1] + ts * (q[1] - p[1])
    return bilinear(img, xs, ys)


def bilinear(img: np.ndarray, xs: np.ndarray, ys: np.ndarray) -> np.ndarray:
    """Interpolação bilinear com borda replicada."""
    h, w = img.shape
    xs = np.clip(np.asarray(xs, float), 0, w - 1)
    ys = np.clip(np.asarray(ys, float), 0, h - 1)
    x0 = np.floor(xs).astype(int)
    y0 = np.floor(ys).astype(int)
    x1 = np.minimum(x0 + 1, w - 1)
    y1 = np.minimum(y0 + 1, h - 1)
    fx, fy = xs - x0, ys - y0
    a = img[y0, x0] * (1 - fx) + img[y0, x1] * fx
    b = img[y1, x0] * (1 - fx) + img[y1, x1] * fx
    return a * (1 - fy) + b * fy


def junction_is_continuous(dirs: List[Tuple[float, float]], collinear_deg: float) -> bool:
    """Grau 3: algum par colinear. Grau 4: dois pares colineares disjuntos."""
    k = len(dirs)
    if k <= 2:
        return True
    pairs = [(i, j) for i in range(k) for j in range(i + 1, k)
             if angle_between(dirs[i], dirs[j]) >= collinear_deg]
    if k == 3:
        return bool(pairs)
    if k == 4:
        for a in pairs:
            for b in pairs:
                if len({*a, *b}) == 4:
                    return True
        return False
    return False


# ------------------------------------------------------------------ III-C
def place_nodes(relief: np.ndarray, skeleton: np.ndarray, c_xy: np.ndarray,
                min_dist: int = 2) -> NodeGraph:
    """Passo 1: nós nos picos (c=0) e depois nos cumes (c=1,2)."""
    g = NodeGraph()
    h, w = skeleton.shape
    occ = np.full((h, w), -1, dtype=np.int64)
    ys, xs = np.nonzero(skeleton)
    if len(xs) == 0:
        return g
    grays = relief[ys, xs].astype(np.int64)
    cs = c_xy[ys, xs].astype(np.int64)
    is_ridge = (cs > 0).astype(np.int64)
    # ordem total: picos antes; depois cinza decrescente, c, y, x
    order = np.lexsort((xs, ys, cs, -grays, is_ridge))
    r = min_dist - 1
    for i in order:
        x, y = int(xs[i]), int(ys[i])
        y0, y1 = max(0, y - r), min(h, y + r + 1)
        x0, x1 = max(0, x - r), min(w, x + r + 1)
        if (occ[y0:y1, x0:x1] >= 0).any():
            continue
        n = g.add_node(x, y, float(relief[y, x]), 'pico' if cs[i] == 0 else 'cume')
        occ[y, x] = n
    return g


def _skeleton_path_exists(skeleton: np.ndarray, a: Tuple[int, int], b: Tuple[int, int]) -> bool:
    """Caminho-8 de esqueleto entre a e b dentro da união das regiões 3x3."""
    h, w = skeleton.shape
    allowed = set()
    for (cx, cy) in (a, b):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                x, y = cx + dx, cy + dy
                if 0 <= x < w and 0 <= y < h and skeleton[y, x]:
                    allowed.add((x, y))
    if a not in allowed or b not in allowed:
        return False
    stack, seen = [a], {a}
    while stack:
        x, y = stack.pop()
        if (x, y) == b:
            return True
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                q = (x + dx, y + dy)
                if q in allowed and q not in seen:
                    seen.add(q)
                    stack.append(q)
    return False


def connect_local(g: NodeGraph, skeleton: np.ndarray) -> None:
    """Passo 2: conexões onde regiões 3x3 se sobrepõem/tocam no esqueleto."""
    ids = g.nodes()
    if not ids:
        return
    P = np.array([g.pos[n] for n in ids])
    for i, a in enumerate(ids):
        d = np.max(np.abs(P[i + 1:] - P[i]), axis=1)
        for j in np.nonzero(d <= 3)[0]:
            b = ids[i + 1 + int(j)]
            pa = (int(P[i][0]), int(P[i][1]))
            pb = (int(g.pos[b][0]), int(g.pos[b][1]))
            if _skeleton_path_exists(skeleton, pa, pb):
                g.add_edge(a, b)
    _remove_triangles(g)


def _remove_triangles(g: NodeGraph) -> None:
    """Remove a aresta mais longa de cada triângulo (esqueleto grosso)."""
    changed = True
    while changed:
        changed = False
        for a in g.nodes():
            nb = g.neighbors(a)
            for i in range(len(nb)):
                for j in range(i + 1, len(nb)):
                    b, c = nb[i], nb[j]
                    if c in g.adj[b]:
                        tri = [(g.dist(a, b), min(a, b), max(a, b)), (g.dist(a, c), min(a, c), max(a, c)),
                               (g.dist(b, c), min(b, c), max(b, c))]
                        _, u, v = max(tri)
                        g.remove_edge(u, v)
                        changed = True
                        break
                if changed:
                    break
            if changed:
                break


def _territory(g: NodeGraph, skeleton: np.ndarray, n: int, radius: int) -> List[Tuple[int, int]]:
    """Pixels de esqueleto ligados a n (até ``radius``) mais próximos dele que de outros nós."""
    h, w = skeleton.shape
    x0, y0 = int(round(g.pos[n][0])), int(round(g.pos[n][1]))
    others = [(m, g.pos[m]) for m in g.nodes() if m != n
              and abs(g.pos[m][0] - x0) <= 2 * radius + 1 and abs(g.pos[m][1] - y0) <= 2 * radius + 1]
    out, stack, seen = [], [(x0, y0)], {(x0, y0)}
    while stack:
        x, y = stack.pop()
        out.append((x, y))
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                q = (x + dx, y + dy)
                if q in seen or not (0 <= q[0] < w and 0 <= q[1] < h) or not skeleton[q[1], q[0]]:
                    continue
                if max(abs(q[0] - x0), abs(q[1] - y0)) > radius:
                    continue
                dn = math.hypot(q[0] - x0, q[1] - y0)
                if any(math.hypot(q[0] - p[0], q[1] - p[1]) < dn for _, p in others):
                    continue
                seen.add(q)
                stack.append(q)
    return out


def stretch_ends(g: NodeGraph, skeleton: np.ndarray, relief: np.ndarray, radius: int) -> None:
    """Passo 3a: move nós de ponta até o último pixel do esqueleto."""
    for n in g.nodes():
        if g.degree(n) != 1:
            continue
        m = g.neighbors(n)[0]
        d = _unit(g.pos[n][0] - g.pos[m][0], g.pos[n][1] - g.pos[m][1])
        best, best_p = 0.0, None
        x0, y0 = g.pos[n]
        for (x, y) in _territory(g, skeleton, n, radius):
            proj = (x - x0) * d[0] + (y - y0) * d[1]
            if proj > best + 0.5:
                best, best_p = proj, (x, y)
        if best_p is not None:
            g.pos[n] = (float(best_p[0]), float(best_p[1]))
            g.gray[n] = float(relief[best_p[1], best_p[0]])
            g.kind[n] = 'esticado'


def split_isolated(g: NodeGraph, skeleton: np.ndarray, relief: np.ndarray, radius: int) -> None:
    """Passo 3b: divide nós de grau 0 em dois (extremos do território)."""
    for n in g.nodes():
        if g.degree(n) != 0 or g.kind[n] == 'pico':
            # um pico isolado costuma ser o centro de uma junção (o ranking
            # quebra o esqueleto em volta): mantê-lo inteiro deixa as pontas
            # chegarem nele pelas conexões candidatas.
            continue
        terr = _territory(g, skeleton, n, radius)
        if len(terr) < 3:
            continue
        pts = np.array(terr, float)
        d = np.linalg.norm(pts[:, None] - pts[None], axis=2)
        i, j = np.unravel_index(int(np.argmax(d)), d.shape)
        if d[i, j] < 2:
            continue
        (xa, ya), (xb, yb) = terr[int(i)], terr[int(j)]
        g.remove_node(n)
        a = g.add_node(xa, ya, float(relief[ya, xa]), 'dividido')
        b = g.add_node(xb, yb, float(relief[yb, xb]), 'dividido')
        g.add_edge(a, b)


def _arm_dir(g: NodeGraph, n: int, toward: Optional[int] = None) -> Optional[Tuple[float, float]]:
    """Direção para fora de uma ponta, usando até 2 nós de braço (mais estável)."""
    nb = g.neighbors(n)
    if len(nb) != 1:
        return None
    m = nb[0]
    far = m
    nb2 = [k for k in g.neighbors(m) if k != n]
    if len(nb2) == 1:
        far = nb2[0]
    return _unit(g.pos[n][0] - g.pos[far][0], g.pos[n][1] - g.pos[far][1])


def _far_point(g: NodeGraph, n: int, m: int) -> Pos:
    """Ponto do braço n->m um nó adiante (se m for de grau 2), mais estável."""
    if g.degree(m) == 2:
        nxt = [k for k in g.neighbors(m) if k != n]
        if nxt:
            return g.pos[nxt[0]]
    return g.pos[m]


def _dirs_at(g: NodeGraph, n: int, extra: Optional[int] = None) -> List[Tuple[float, float]]:
    """Direções dos braços em n (com 2 nós de alcance) e, opcionalmente, da nova aresta."""
    p = g.pos[n]
    out = []
    for m in g.neighbors(n):
        q = _far_point(g, n, m)
        out.append(_unit(q[0] - p[0], q[1] - p[1]))
    if extra is not None:
        out.append(_unit(g.pos[extra][0] - p[0], g.pos[extra][1] - p[1]))
    return out


def candidate_connections(g: NodeGraph, relief: np.ndarray, p: GraphParams) -> int:
    """Passo 3c: conexões candidatas (continuidade, fechamento, simplicidade)."""
    ids = g.nodes()
    if len(ids) < 2:
        return 0
    P = np.array([g.pos[n] for n in ids])
    cands = []
    max_turn = p.max_turn_deg
    for i, u in enumerate(ids):
        if g.degree(u) > 1:
            continue
        du = _arm_dir(g, u)
        dd = np.hypot(*(P - P[i]).T)
        for j in np.nonzero((dd > 0) & (dd <= p.candidate_max_dist))[0]:
            v = ids[int(j)]
            if v in g.adj[u] or g.degree(v) >= p.max_degree:
                continue
            if g.degree(v) <= 1 and v < u and g.degree(u) == g.degree(v):
                continue  # par simétrico: avaliado uma vez
            e = _unit(g.pos[v][0] - g.pos[u][0], g.pos[v][1] - g.pos[u][1])
            if du is not None:
                turn_u = angle_between(du, e)
                if turn_u > max_turn:
                    continue
                cont_u = math.cos(math.radians(turn_u))
            else:
                cont_u = 0.5
            if g.degree(v) == 1:
                dv = _arm_dir(g, v)
                turn_v = angle_between(dv, (-e[0], -e[1])) if dv else 0.0
                if turn_v > max_turn:
                    continue
                cont_v = math.cos(math.radians(turn_v))
            else:
                cont_v = 0.5 if g.degree(v) == 0 else cont_u
            h = g.hops(u, v, p.min_hops_shortcut)
            if h is not None:
                continue  # atalho dentro da mesma linha
            along = sample_along(relief.astype(np.float32), g.pos[u], g.pos[v])
            g_nodes = 0.5 * (g.gray[u] + g.gray[v])
            closure = float(min(1.0, (along.mean() / g_nodes) if g_nodes > 0 else 0.0))
            if closure < p.min_closure:
                continue
            simp = 1.0 - float(dd[j]) / p.candidate_max_dist
            score = (p.w_continuity * 0.5 * (cont_u + cont_v) + p.w_closure * closure
                     + p.w_simplicity * simp)
            if score >= p.candidate_min_score:
                cands.append((-score, float(dd[j]), u, v))
    cands.sort()
    added = 0
    for _, _, u, v in cands:
        if v in g.adj[u] or g.degree(u) >= p.max_degree or g.degree(v) >= p.max_degree:
            continue
        if g.degree(u) > 1:
            continue
        if not junction_is_continuous(_dirs_at(g, v, u), p.collinear_deg):
            continue
        if not junction_is_continuous(_dirs_at(g, u, v), p.collinear_deg):
            continue
        pu, pv = g.pos[u], g.pos[v]
        if any(segments_cross(pu, pv, g.pos[a], g.pos[b]) for a, b in g.edges()
               if a not in (u, v) and b not in (u, v)):
            continue
        if g.hops(u, v, p.min_hops_shortcut) is not None:
            continue
        g.add_edge(u, v)
        added += 1
    return added


def _ray_hit(u: Pos, d: Tuple[float, float], a: Pos, b: Pos) -> Optional[Tuple[float, float, Pos]]:
    """Raio u + t·d contra o segmento ab: (t, s, ponto) com s em [0, 1], ou None."""
    ex, ey = b[0] - a[0], b[1] - a[1]
    den = d[0] * ey - d[1] * ex
    if abs(den) < 1e-9:
        return None
    wx, wy = a[0] - u[0], a[1] - u[1]
    t = (wx * ey - wy * ex) / den
    sp = (wx * d[1] - wy * d[0]) / den
    if not (0.0 <= sp <= 1.0):
        return None
    return t, sp, (a[0] + sp * ex, a[1] + sp * ey)


def edge_candidates(g: NodeGraph, relief: np.ndarray, p: GraphParams,
                    skeleton: Optional[np.ndarray] = None) -> int:
    """
    Passo 3c (cont.): ponta -> aresta. Forma T/X quando a haste termina na linha.

    O operador de ranking costuma quebrar o esqueleto na junção, e a linha que
    atravessa é religada por cima dela (conexão ponta-a-ponta). A haste então
    termina sobre uma *aresta*, não sobre um nó; a conexão candidata vai do nó
    de ponta até o ponto da aresta atingido pelo prolongamento da haste, que
    vira um nó novo (sobre o esqueleto, se houver pixel a até 1 célula).
    """
    rf = relief.astype(np.float32)
    cands = []
    for u in g.nodes():
        if g.degree(u) != 1:
            continue
        du = _arm_dir(g, u)
        if du is None or du == (0.0, 0.0):
            continue
        pu = g.pos[u]
        for a, b in g.edges():
            if u in (a, b):
                continue
            hit = _ray_hit(pu, du, g.pos[a], g.pos[b])
            # tolerância: a ponta pode estar logo "depois" da aresta (t ligeiramente < 0)
            if hit is None or not (-1.0 <= hit[0] <= p.candidate_max_dist):
                continue
            t, sp, q = hit
            if g.hops(u, a, p.min_hops_shortcut) is not None or g.hops(u, b, p.min_hops_shortcut) is not None:
                continue
            seg_len = g.dist(a, b)
            if seg_len < 1e-6:
                continue
            along = sample_along(rf, pu, q) if abs(t) >= 1.0 else np.array(
                [rf[int(round(pu[1])), int(round(pu[0]))]])
            gq = float(bilinear(rf, np.array([q[0]]), np.array([q[1]]))[0])
            g_nodes = 0.5 * (g.gray[u] + gq)
            closure = float(min(1.0, (along.mean() / g_nodes) if g_nodes > 0 else 0.0))
            if closure < p.min_closure:
                continue
            simp = 1.0 - max(0.0, t) / p.candidate_max_dist
            score = p.w_continuity * 1.0 + p.w_closure * closure + p.w_simplicity * simp
            if score >= p.candidate_min_score:
                cands.append((-score, abs(t), u, a, b, q, t))
    cands.sort(key=lambda c: (c[0], c[1], c[2], c[3], c[4]))
    added = 0
    for _, _, u, a, b, q, t in cands:
        if g.degree(u) != 1 or b not in g.adj.get(a, set()):
            continue
        pu = g.pos[u]
        if any(segments_cross(pu, q, g.pos[x], g.pos[y]) for x, y in g.edges()
               if len({x, y} & {u, a, b}) == 0):
            continue
        g.remove_edge(a, b)
        if abs(t) < 1.0:
            m = u  # a ponta já está sobre a aresta: ela vira a junção
        else:
            qq = q
            if skeleton is not None:
                h, w = skeleton.shape
                best = None
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        x, y = int(round(q[0])) + dx, int(round(q[1])) + dy
                        if 0 <= x < w and 0 <= y < h and skeleton[y, x]:
                            dd = math.hypot(x - q[0], y - q[1])
                            if best is None or dd < best[0]:
                                best = (dd, (float(x), float(y)))
                if best is not None:
                    qq = best[1]
            m = g.add_node(qq[0], qq[1], float(
                bilinear(rf, np.array([qq[0]]), np.array([qq[1]]))[0]), 'juncao')
            g.add_edge(u, m)
        g.add_edge(a, m)
        g.add_edge(m, b)
        added += 1
    return added


def enforce_max_degree(g: NodeGraph, relief: np.ndarray, max_degree: int) -> None:
    """Grau > 4: remove as arestas mais fracas (menor cinza ao longo)."""
    rf = relief.astype(np.float32)
    for n in g.nodes():
        while g.degree(n) > max_degree:
            worst = min(g.neighbors(n), key=lambda m: (
                sample_along(rf, g.pos[n], g.pos[m]).mean(), -m))
            g.remove_edge(n, worst)


def build_graph(relief: np.ndarray, skeleton: np.ndarray, params: Optional[GraphParams] = None,
                c_xy: Optional[np.ndarray] = None) -> NodeGraph:
    """III-C completa: devolve o grafo de nós e conexões (Fig. 2c do artigo)."""
    p = params or GraphParams()
    skeleton = np.asarray(skeleton, bool)
    if c_xy is None:
        c_xy = ranking_count(relief)
    g = place_nodes(relief, skeleton, c_xy, p.min_node_distance)
    connect_local(g, skeleton)
    enforce_max_degree(g, relief, p.max_degree)
    stretch_ends(g, skeleton, relief, p.stretch_radius)
    split_isolated(g, skeleton, relief, p.stretch_radius)
    if p.edge_first:
        edge_candidates(g, relief, p, skeleton)
        candidate_connections(g, relief, p)
        edge_candidates(g, relief, p, skeleton)
    else:
        candidate_connections(g, relief, p)
        edge_candidates(g, relief, p, skeleton)
    enforce_max_degree(g, relief, p.max_degree)
    return g


def components(g: NodeGraph) -> List[Set[int]]:
    """Componentes conexos (ordem determinística)."""
    seen: Set[int] = set()
    out: List[Set[int]] = []
    for n in g.nodes():
        if n in seen:
            continue
        comp, stack = set(), [n]
        while stack:
            u = stack.pop()
            if u in comp:
                continue
            comp.add(u)
            stack.extend(v for v in g.adj[u] if v not in comp)
        seen |= comp
        out.append(comp)
    return out
