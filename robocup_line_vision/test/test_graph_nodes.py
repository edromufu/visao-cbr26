"""III-C: posicionamento e conexão de nós (esqueletos construídos à mão)."""

from helpers import grid_from_strokes
import numpy as np
import pytest

from robocup_line_vision.graph_nodes import build_graph, GraphParams


def _components(g):
    seen, comps = set(), []
    for n in g.nodes():
        if n in seen:
            continue
        stack, comp = [n], set()
        while stack:
            u = stack.pop()
            if u in comp:
                continue
            comp.add(u)
            stack.extend(v for v in g.neighbors(u) if v not in comp)
        seen |= comp
        comps.append(comp)
    return comps


def test_nos_sobre_o_esqueleto_e_espacados():
    s1 = grid_from_strokes([((5, 30), (70, 30))])
    g = build_graph(s1.relief, s1.skeleton)
    assert len(g.nodes()) >= 15
    for n in g.nodes():
        x, y = g.pos[n]
        assert s1.skeleton[int(round(y)), int(round(x))]
    pts = np.array([g.pos[n] for n in g.nodes()])
    d = np.max(np.abs(pts[:, None, :] - pts[None, :, :]), axis=2) + np.eye(len(pts)) * 99
    assert d.min() >= 2  # pelo menos 2 pixels (Chebyshev) entre nós


def test_linha_reta_vira_cadeia_unica():
    s1 = grid_from_strokes([((5, 30), (70, 30))])
    g = build_graph(s1.relief, s1.skeleton)
    comps = _components(g)
    assert len(comps) == 1
    degs = [g.degree(n) for n in g.nodes()]
    assert max(degs) <= 2 and degs.count(1) == 2


def test_linha_diagonal_sem_triangulos():
    s1 = grid_from_strokes([((5, 5), (60, 50))], width_px=10)
    g = build_graph(s1.relief, s1.skeleton)
    assert len(_components(g)) == 1
    assert max(g.degree(n) for n in g.nodes()) <= 2


def test_lacuna_e_preenchida():
    s1 = grid_from_strokes([((5, 30), (34, 30)), ((38, 30), (70, 30))])
    g = build_graph(s1.relief, s1.skeleton)
    assert len(_components(g)) == 1


def test_grau_maximo_4_e_deterministico():
    strokes = [((5, 30), (70, 30)), ((38, 5), (38, 55)), ((10, 10), (60, 50))]
    s1 = grid_from_strokes(strokes)
    g1 = build_graph(s1.relief, s1.skeleton)
    g2 = build_graph(s1.relief.copy(), s1.skeleton.copy())
    assert max(g1.degree(n) for n in g1.nodes()) <= 4
    assert sorted(g1.pos.values()) == sorted(g2.pos.values())
    assert sorted(g1.edges()) == sorted(g2.edges())


@pytest.mark.parametrize('strokes', [
    [((10, 50), (40, 50)), ((40, 50), (40, 10))],                  # L
    [((5, 30), (70, 30)), ((38, 30), (38, 55))],                   # T
    [((5, 30), (70, 30)), ((38, 5), (38, 55))],                    # X
])
def test_cruzamentos_ficam_conectados(strokes):
    s1 = grid_from_strokes(strokes)
    g = build_graph(s1.relief, s1.skeleton)
    assert len(_components(g)) == 1


def test_parametros_padrao_documentados():
    p = GraphParams()
    assert p.max_degree == 4 and p.min_node_distance == 2


def test_ponta_encontra_aresta_e_forma_T():
    """Haste termina sobre a aresta que atravessa a junção (caso medido no sintético)."""
    from robocup_line_vision.graph_nodes import edge_candidates, NodeGraph
    g = NodeGraph()
    relief = np.full((20, 30), 80, np.uint8)
    a = g.add_node(5, 5, 80)
    b = g.add_node(15, 5, 80)
    g.add_edge(a, b)                        # linha horizontal (já ligada por cima da junção)
    s0 = g.add_node(10, 12, 80)
    s1 = g.add_node(10, 9, 80)
    e = g.add_node(10, 6, 80)               # ponta da haste, a 1 célula da aresta
    g.add_edge(s0, s1)
    g.add_edge(s1, e)
    n = edge_candidates(g, relief, GraphParams())
    assert n == 1
    degs = sorted(g.degree(k) for k in g.nodes())
    assert degs.count(3) == 1                # uma junção de grau 3 (T)
    j = [k for k in g.nodes() if g.degree(k) == 3][0]
    assert abs(g.pos[j][0] - 10) <= 1 and abs(g.pos[j][1] - 5) <= 1
