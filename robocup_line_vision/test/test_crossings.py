"""IV-A: cruzamentos L/T/X com esqueletos construídos à mão."""

import math

from helpers import angle_close, grid_from_strokes
import pytest

from robocup_line_vision.crossings import CrossingParams, crossings_from_lines, detect_crossings
from robocup_line_vision.graph_nodes import build_graph
from robocup_line_vision.lines import extract_lines, LineParams


def run(strokes, **kw):
    s1 = grid_from_strokes(strokes, **{k: v for k, v in kw.items()
                           if k in ('circles', 'blobs', 'width_px')})
    g = build_graph(s1.relief, s1.skeleton)
    return s1, detect_crossings(g, s1, CrossingParams())


def _near(c, gx, gy, s1, tol_cells=1.6):
    x, y = s1.grid_to_image(gx, gy)
    return math.hypot(c.x - x, c.y - y) <= tol_cells * s1.scale[0]


def test_L():
    s1, cr = run([((10, 50), (40, 50)), ((40, 50), (40, 10))])
    assert [c.tipo for c in cr] == ['L']
    c = cr[0]
    assert _near(c, 40, 50, s1)
    assert len(c.heading_rays) == 2
    # braços: para a esquerda (pi) e para cima (-pi/2 = 3pi/2)
    assert any(angle_close(a, math.pi, 12) for a in c.heading_rays)
    assert any(angle_close(a, 1.5 * math.pi, 12) for a in c.heading_rays)
    assert c.heading_rays == sorted(c.heading_rays)
    assert all(0 <= a < 2 * math.pi for a in c.heading_rays)
    assert c.verificacao['circulo'] and c.verificacao['caminho_branco']


def test_T():
    s1, cr = run([((5, 30), (70, 30)), ((38, 30), (38, 55))])
    assert [c.tipo for c in cr] == ['T']
    assert _near(cr[0], 38, 30, s1)
    assert len(cr[0].heading_rays) == 3


def test_X():
    s1, cr = run([((5, 30), (70, 30)), ((38, 5), (38, 55))])
    assert [c.tipo for c in cr] == ['X']
    assert _near(cr[0], 38, 30, s1)
    assert len(cr[0].heading_rays) == 4


def test_X_obliquo():
    s1, cr = run([((5, 10), (70, 50)), ((5, 50), (70, 10))])
    assert [c.tipo for c in cr] == ['X']


def test_linha_reta_sem_cruzamento():
    _, cr = run([((5, 30), (70, 30))])
    assert cr == []


def test_linha_com_lacuna_sem_cruzamento():
    _, cr = run([((5, 30), (34, 30)), ((38, 30), (70, 30))])
    assert cr == []


def test_ponta_curta_nao_vira_T():
    # ruído: um tracinho de 2 células grudado numa linha reta
    _, cr = run([((5, 30), (70, 30)), ((38, 30), (38, 32))])
    assert [c.tipo for c in cr if c.tipo == 'T'] == []


def test_circulo_nao_gera_L():
    _, cr = run([], circles=[((40, 30), 18)])
    assert [c for c in cr if c.tipo == 'L'] == []


def test_circulo_cortado_pela_linha_do_meio_gera_2_X():
    s1, cr = run([((2, 30), (78, 30))], circles=[((40, 30), 15)])
    xs = [c for c in cr if c.tipo == 'X']
    assert len(xs) == 2
    assert {round(s1.image_to_grid(c.x, c.y)[0] / 5) for c in xs} == {5, 11}


def test_verificacao_rejeita_juncao_sem_branco():
    # grau 3 forçado sem caminho branco: apagar o branco de um braço
    s1 = grid_from_strokes([((5, 30), (70, 30)), ((38, 30), (38, 55))])
    g = build_graph(s1.relief, s1.skeleton)
    s1.white_resized[33:, :] = 0  # some com o braço de baixo nas imagens de cor
    s1.green_resized[33:, :] = 255
    cr = detect_crossings(g, s1, CrossingParams())
    assert [c.tipo for c in cr if c.tipo == 'T'] == []


# ---- extensão: cruzamentos a partir das retas (IV-B) e da elipse ----------


def run_lines(strokes, **kw):
    s1 = grid_from_strokes(strokes, **kw)
    g = build_graph(s1.relief, s1.skeleton)
    lines, ells = extract_lines(g, s1, LineParams())
    return s1, crossings_from_lines(lines, ells, s1, CrossingParams())


@pytest.mark.parametrize('strokes,tipo,gx,gy', [
    ([((10, 50), (40, 50)), ((40, 50), (40, 10))], 'L', 40, 50),
    ([((5, 30), (70, 30)), ((38, 30), (38, 55))], 'T', 38, 30),
    ([((5, 30), (70, 30)), ((38, 5), (38, 55))], 'X', 38, 30),
    ([((5, 20), (70, 20)), ((20, 20), (50, 50))], 'T', 20, 20),     # T oblíquo
])
def test_retas_geram_o_tipo_certo(strokes, tipo, gx, gy):
    s1, cr = run_lines(strokes)
    assert [c.tipo for c in cr] == [tipo]
    assert _near(cr[0], gx, gy, s1, 1.2)
    assert len(cr[0].heading_rays) == {'L': 2, 'T': 3, 'X': 4}[tipo]
    assert cr[0].fonte == 'retas'


def test_retas_paralelas_ou_distantes_nao_cruzam():
    _, cr = run_lines([((5, 20), (70, 20)), ((5, 40), (70, 40))])
    assert cr == []
    _, cr = run_lines([((5, 20), (30, 20)), ((50, 10), (50, 50))])  # longe da ponta
    assert cr == []


def test_reta_x_elipse_gera_dois_X():
    s1, cr = run_lines([((2, 30), (78, 30))], circles=[((40, 30), 15)])
    xs = [c for c in cr if c.tipo == 'X']
    assert len(xs) == 2
    assert sorted(round(s1.image_to_grid(c.x, c.y)[0])
                  for c in xs) == pytest.approx([25, 55], abs=1.5)
