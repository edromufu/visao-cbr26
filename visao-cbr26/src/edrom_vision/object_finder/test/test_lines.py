"""IV-B: linhas por split-and-merge e elipse do círculo central."""

import math

from helpers import grid_from_strokes
import numpy as np

from object_finder.camera_model import CameraModel
from object_finder.graph_nodes import build_graph
from object_finder.lines import degree2_components, extract_lines, LineParams, split_and_merge


def run(strokes, **kw):
    s1 = grid_from_strokes(strokes, **kw)
    g = build_graph(s1.relief, s1.skeleton)
    return s1, g, extract_lines(g, s1, LineParams())


def _ang(ln):
    return math.degrees(math.atan2(ln.y2 - ln.y1, ln.x2 - ln.x1)) % 180


def test_reta_unica_com_extremos_projetados():
    s1, g, (lines, ells) = run([((5, 30), (70, 30))])
    assert len(lines) == 1 and ells == []
    ln = lines[0]
    xs = sorted([ln.x1, ln.x2])
    assert abs(xs[0] - s1.grid_to_image(5, 30)[0]) <= 2.5 * 8
    assert abs(xs[1] - s1.grid_to_image(70, 30)[0]) <= 2.5 * 8
    assert abs(ln.y1 - ln.y2) < 2.0 and ln.n_nos >= 10


def test_L_vira_duas_linhas():
    _, _, (lines, _) = run([((10, 50), (40, 50)), ((40, 50), (40, 10))])
    assert len(lines) == 2
    horiz = [ln for ln in lines if min(_ang(ln), 180 - _ang(ln)) < 5]
    vert = [ln for ln in lines if abs(_ang(ln) - 90) < 5]
    assert len(horiz) == 1 and len(vert) == 1


def test_split_no_no_mais_distante():
    pts = np.array([[x, 0.0] for x in range(0, 20, 2)] + [[18 + k * 1.4, k * 1.4]
                   for k in range(1, 10)])
    segs = split_and_merge(pts, LineParams(
        split_dist=2.0, merge_angle_deg=5, merge_dist=1.0), scale=1.0)
    assert len(segs) == 2


def test_merge_de_colineares():
    a = np.array([[x, 10.0] for x in range(0, 40, 2)])
    b = np.array([[x, 10.4] for x in range(60, 100, 2)])
    from object_finder.lines import merge_segments, Segment
    segs = merge_segments([Segment.fit(a), Segment.fit(b)], LineParams(), scale=1.0)
    assert len(segs) == 1 and segs[0].n == len(a) + len(b)


def test_componente_com_menos_de_3_nos_descartado():
    s1, g, (lines, _) = run([((10, 30), (13, 30))])
    assert lines == []


def test_componentes_de_grau_2_incluem_vizinhos_de_outro_grau():
    s1 = grid_from_strokes([((5, 30), (70, 30)), ((38, 30), (38, 55))])
    g = build_graph(s1.relief, s1.skeleton)
    comps = degree2_components(g)
    junctions = [n for n in g.nodes() if g.degree(n) == 3]
    assert junctions
    j = junctions[0]
    assert sum(j in c for c in comps) == 3  # a junção entra nos 3 ramos


def test_circulo_vira_elipse_e_nao_linhas_curtas():
    s1, g, (lines, ells) = run([], circles=[((40, 30), 15)])
    assert len(ells) == 1
    e = ells[0]
    cx, cy = s1.grid_to_image(40, 30)
    assert abs(e.cx - cx) < 8 and abs(e.cy - cy) < 8
    assert abs(e.eixo_maior / 2 - 15 * 8) < 12
    assert len(lines) == 0


def test_circulo_e_linha_do_meio():
    s1, g, (lines, ells) = run([((2, 30), (78, 30))], circles=[((40, 30), 15)])
    assert len(ells) == 1
    assert any(abs(_ang(ln) % 180) < 3 or abs(_ang(ln) - 180) < 3 for ln in lines)


def test_distorcao_e_projecao_no_chao():
    cam = CameraModel.from_fov(1080, 720, math.radians(45), height=0.70, pitch=0.0)
    # um ponto 1 m à frente no chão aparece abaixo do centro
    u, v = cam.ground_to_image(1.0, 0.0)
    assert abs(u - 540) < 1e-6 and v > 360
    x, y = cam.image_to_ground(u, v)
    assert abs(x - 1.0) < 1e-6 and abs(y) < 1e-6
    assert cam.image_to_ground(540, 300) is None  # acima do horizonte
    # ponto à esquerda (y>0) fica à esquerda na imagem (u < cx)
    u2, _ = cam.ground_to_image(2.0, 0.5)
    assert u2 < 540
