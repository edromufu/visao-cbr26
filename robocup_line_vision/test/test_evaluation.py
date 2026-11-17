"""Métricas de avaliação."""

from types import SimpleNamespace as NS

from robocup_line_vision.evaluation import is_mark, line_metrics, match_crossings

GT = {'cruzamentos': [{'tipo': 'X', 'x': 100, 'y': 100}, {'tipo': 'X', 'x': 300, 'y': 200},
                      {'tipo': 'L', 'x': 50, 'y': 300}],
      'linhas': [{'x1': 0, 'y1': 200, 'x2': 600, 'y2': 200},      # longa
                 {'x1': 95, 'y1': 100, 'x2': 105, 'y2': 100}],     # traço da marca
      'circulos': []}


def test_marca_x_separada_do_cruzamento():
    assert is_mark(GT['cruzamentos'][0], GT)           # perto de linha curta
    assert not is_mark(GT['cruzamentos'][1], GT)       # sobre a linha longa
    assert not is_mark(GT['cruzamentos'][2], GT)       # L nunca é marca


def test_casamento_um_para_um_no_raio():
    dets = [NS(tipo='X', x=305, y=203), NS(tipo='T', x=52, y=298), NS(tipo='L', x=400, y=400),
            NS(tipo='X', x=301, y=199)]
    r = match_crossings(dets, GT['cruzamentos'][1:], radius=15)
    assert (r.tp, r.fp, r.fn, r.tp_tipo) == (2, 2, 0, 1)


def test_linhas_longas_e_precisao():
    dets = [NS(x1=10, y1=203, x2=580, y2=198), NS(x1=0, y1=400, x2=300, y2=400)]
    m = line_metrics(dets, GT)
    assert (m.gt_longas, m.gt_longas_cobertas, m.gt_curtas) == (1, 1, 1)
    assert (m.det, m.det_corretas) == (2, 1)
