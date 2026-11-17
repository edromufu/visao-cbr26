"""Testes do adaptador da etapa 1 (código original em vendor/)."""

import os
from pathlib import Path

import cv2
import numpy as np
import pytest

from robocup_line_vision import stage1_adapter as sa
from robocup_line_vision.calibration import core

DATA = Path(__file__).parent / 'data'


@pytest.fixture(scope='module')
def frame():
    img = cv2.imread(str(DATA / 'frame_webots.png'))
    assert img is not None
    return img


def test_limiar_do_branco_original():
    lower, up = sa.white_thresholds_from_csv(sa.DEFAULT_WHITE_CSV)
    assert lower.tolist() == [45, 0, 213] and up.tolist() == [164, 43, 255]


def test_ambiente_restaurado_e_sem_saida(capsys, tmp_path):
    os.environ.pop('RLV_WHITE_CSV', None)
    sa.white_thresholds_from_csv(sa.DEFAULT_WHITE_CSV)
    assert 'RLV_WHITE_CSV' not in os.environ
    assert capsys.readouterr().out == ''


def test_equivalente_ao_processar(frame):
    s = sa.Stage1Segmenter(baseline_polylines=True)
    r = s.process(frame)
    ref = s.vendor_segmenter.processar(frame)
    assert np.array_equal(r.skeleton, ref['skeleton'])
    assert np.array_equal(r.field_mask, ref['mascara_convexa'])
    assert r.field_detected == ref['campo_detectado'] is True
    assert r.baseline['segmentos_linhas'] == ref['segmentos_linhas']
    assert r.grid_shape == (90, 135) and r.scale == (8.0, 8.0)


def test_duas_calibracoes_no_mesmo_processo(frame):
    a = sa.Stage1Segmenter()
    b = sa.Stage1Segmenter(white_range=([0, 0, 250], [179, 10, 255]))
    ra, rb = a.process(frame), b.process(frame)
    ra2 = a.process(frame)
    assert rb.white_mask.sum() < ra.white_mask.sum()
    assert np.array_equal(ra.white_mask, ra2.white_mask)  # b não contaminou a


def test_caixa_do_verde_equivale_ao_csv_denso(frame, tmp_path):
    rng = core.HSVRange((52, 133, 102), (62, 255, 172))
    core.write_green_csv(tmp_path / 'g.csv', rng)
    s_csv = sa.Stage1Segmenter(tmp_path / 'g.csv')
    s_box = sa.Stage1Segmenter()
    s_box.set_green_box(rng.lower, rng.upper)
    assert np.array_equal(s_csv.process(frame).green_mask, s_box.process(frame).green_mask)


def test_mascara_de_caixas_antes_do_esqueleto(frame):
    s = sa.Stage1Segmenter()
    full = s.process(frame)
    ys, xs = np.nonzero(full.skeleton)
    gx, gy = int(xs[0]), int(ys[0])
    cx, cy = full.grid_to_image(gx, gy)
    masked = s.process(frame, mask_boxes=[(cx, cy, 40, 40)])
    assert not masked.skeleton[gy, gx]
    assert masked.skeleton.sum() < full.skeleton.sum()
    assert masked.field_detected == full.field_detected


def test_ranking_count_igual_ao_original(frame):
    r = sa.Stage1Segmenter().process(frame)
    c = sa.ranking_count(r.relief)
    assert np.array_equal((r.relief > 0) & (c < 3) & _interior(c.shape), r.skeleton)


def _interior(shape):
    m = np.zeros(shape, bool)
    m[1:-1, 1:-1] = True
    return m
