"""Fusão grafo x YOLO."""

import numpy as np

from object_finder.features import CrossingFeature, Detection
from object_finder.fusion import fuse, FusionParams, mask_boxes


class S1:
    """Campo = metade de baixo da imagem 640x480 (grade 80x60)."""

    image_shape = (480, 640)
    grid_shape = (60, 80)
    scale = (8.0, 8.0)
    field_detected = True

    def __init__(self):
        self.field_mask = np.zeros((60, 80), np.uint8)
        self.field_mask[30:] = 255
        self.field_mask_full = np.zeros((480, 640), np.uint8)
        self.field_mask_full[240:] = 255


def det(cls, x, y, w=20, h=20, conf=0.8):
    ids = {'ball': 0, 'goalpost': 1, 'robot': 2, 'L-Intersection': 3, 'T-Intersection': 4,
           'X-Intersection': 5, 'crossbar': 6}
    return Detection(cls, ids[cls], conf, x, y, w, h)


def test_rejeita_deteccao_fora_do_campo():
    dets = [det('ball', 300, 100), det('ball', 300, 400), det('robot', 100, 230, 40, 40)]
    out = fuse([], dets, S1(), FusionParams())
    rej = {(d.classe, d.y): d.motivo for d in out.detections if d.rejeitada}
    assert rej == {('ball', 100): 'outside_field'}
    # o robô tem o pé (base da caixa, y=250) dentro do campo
    assert not [d for d in out.detections if d.classe == 'robot' and d.rejeitada]


def test_mascara_so_bola_robo_trave_aceitas():
    dets = [det('ball', 300, 400), det('goalpost', 50, 300, 10, 80), det('L-Intersection', 200, 400),
            det('ball', 300, 50)]
    out = fuse([], dets, S1(), FusionParams())
    boxes = mask_boxes(out.detections, FusionParams())
    assert len(boxes) == 2  # bola no campo + trave; cruzamento e bola fora não mascaram


def test_confirmacao_sobe_confianca_e_yolo_sozinho_e_rebaixado():
    g = CrossingFeature('L', 200.0, 400.0, [0.0, 1.5], 0.6)
    g2 = CrossingFeature('L', 500.0, 400.0, [0.0, 1.5], 0.6)
    dets = [det('L-Intersection', 205, 398, conf=0.9),       # confirma o L
            det('X-Intersection', 500, 402, conf=0.9),       # L x X: incompatível, não confirma
            det('T-Intersection', 350, 300, conf=0.9)]       # sem estrutura de linha
    out = fuse([g, g2], dets, S1(), FusionParams())
    by_xy = {(round(c.x), round(c.y)): c for c in out.crossings}
    assert by_xy[(200, 400)].fonte == 'grafo+yolo' and by_xy[(200, 400)].confianca > 0.6
    assert by_xy[(500, 400)].fonte == 'grafo' and by_xy[(500, 400)].confianca == 0.6
    y = by_xy[(350, 300)]
    assert y.fonte == 'yolo' and y.heading_rays == [] and y.confianca < 0.9 * 0.6
    assert y.tipo == 'T'


def test_classes_mapeadas_por_nome_nao_por_numero():
    d = Detection('X-Intersection', 3, 0.9, 200, 400, 20, 20)  # id "errado" de propósito
    g = CrossingFeature('X', 200.0, 400.0, [0, 1, 2, 3], 0.5)
    out = fuse([g], [d], S1(), FusionParams())
    assert out.crossings[0].fonte == 'grafo+yolo'


def test_T_do_grafo_vira_X_quando_o_yolo_ve_X():
    import math
    g = CrossingFeature('T', 300.0, 400.0, [0.0, math.pi / 2, math.pi], 0.8)  # haste para baixo
    out = fuse([g], [det('X-Intersection', 304, 398, conf=0.8)], S1(), FusionParams())
    c = out.crossings[0]
    assert c.tipo == 'X' and c.fonte == 'grafo+yolo' and len(c.heading_rays) == 4
    assert any(abs(a - 1.5 * math.pi) < 1e-6 for a in c.heading_rays)
