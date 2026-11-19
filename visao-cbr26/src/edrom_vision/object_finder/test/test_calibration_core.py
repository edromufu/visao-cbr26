"""Testes do núcleo da calibração de cor."""

import json

import cv2
import numpy as np
from object_finder.calibration import core
from object_finder.stage1_adapter import white_thresholds_from_csv
import pandas as pd
import pytest


@pytest.mark.parametrize('lo,up', [
    ((0, 0, 213), (179, 43, 255)),
    ((45, 0, 213), (164, 43, 255)),
    ((0, 0, 150), (179, 80, 255)),
    ((10, 5, 100), (20, 9, 101)),
    ((0, 0, 0), (0, 0, 0)),
    ((179, 255, 255), (179, 255, 255)),
    ((3, 0, 254), (177, 1, 255)),
])
def test_white_csv_reproduz_faixa_pela_formula_original(tmp_path, lo, up):
    rng = core.HSVRange(lo, up)
    path = tmp_path / 'white_pixels.csv'
    core.write_white_csv(path, rng)
    lower, upper = white_thresholds_from_csv(path)
    assert tuple(lower) == rng.lower
    assert tuple(upper) == rng.upper
    df = pd.read_csv(path)
    assert list(df.columns) == ['H', 'S', 'V', 'class']
    assert set(df['class']) == {'branco'}


def test_green_csv_denso(tmp_path):
    rng = core.HSVRange((50, 140, 120), (52, 142, 121))
    path = tmp_path / 'green_pixels.csv'
    n = core.write_green_csv(path, rng)
    df = pd.read_csv(path)
    assert n == 3 * 3 * 2 == len(df)
    assert list(df.columns) == ['H', 'S', 'V']
    assert set(map(tuple, df.values.tolist())) == {
        (h, s, v) for h in (50, 51, 52) for s in (140, 141, 142) for v in (120, 121)}


def test_proposta_verde_cobre_amostras_com_margem():
    rng = np.random.default_rng(0)
    px = np.stack([rng.integers(55, 62, 500), rng.integers(150, 230, 500),
                   rng.integers(120, 155, 500)], axis=1)
    g = core.propose_green_range(px)
    assert g.contains(px).mean() > 0.97
    assert g.lower[0] <= 55 - 3 and g.upper[0] >= 61 + 3
    assert g.upper[1] == 255


def test_filtro_do_branco_descarta_carpete_e_borda_escura():
    green = core.HSVRange((50, 120, 80), (70, 255, 180))
    carpete = np.tile([[60, 180, 130]], (300, 1))
    linha = np.tile([[100, 10, 240]], (60, 1))
    borda = np.tile([[90, 60, 150]], (60, 1))  # transição, nem verde nem branco
    px = np.concatenate([carpete, linha, borda])
    kept = core.filter_white_candidates(px, green)
    assert (kept[:, 2] >= 200).all()
    w = core.propose_white_range(px, green)
    assert w.lower[2] > 150 and w.upper[1] <= 40
    assert (w.lower[0], w.upper[0]) == (0, 179)


def test_amostra_pincel_e_retangulo():
    s = core.Sample('verde', 'pincel', 'a', pontos=[(10, 10), (20, 10)], raio=2)
    m = s.mask((30, 30))
    assert m[10, 15] == 255 and m[0, 0] == 0
    r = core.Sample('branco', 'retangulo', 'a', retangulo=(5, 5, 7, 6))
    assert r.mask((30, 30)).sum() // 255 == 3 * 2


def test_salvar_versiona_e_atualiza_ultima(tmp_path):
    import datetime as dt
    cal = core.Calibration(core.HSVRange((54, 140, 110), (62, 255, 160)),
                           core.HSVRange((0, 0, 200), (179, 40, 255)))
    t = dt.datetime(2026, 11, 13, 9, 0, 0)
    frame = np.zeros((8, 8, 3), np.uint8)
    d1 = core.save_calibration(cal, tmp_path, {'f.png': frame}, now=t)
    d2 = core.save_calibration(cal, tmp_path, now=t)  # mesmo segundo: não sobrescreve
    assert d1.name == 'calib_20261113_090000' and d2.name == 'calib_20261113_090000_2'
    assert (d1 / 'frames' / 'f.png').is_file()
    ult = tmp_path / 'ultima'
    assert (ult / 'green_pixels.csv').is_file() and (ult / 'white_pixels.csv').is_file()
    data = json.loads((ult / 'calib.json').read_text(encoding='utf-8'))
    assert data['pasta'] == d2.name and data['verde']['lower'] == [54, 140, 110]
    c2, gcsv, wcsv = core.load_calibration_dir(d1)
    assert c2.green.lower == (54, 140, 110)
    lower, upper = white_thresholds_from_csv(wcsv)
    assert tuple(lower) == (0, 0, 200) and tuple(upper) == (179, 40, 255)


def test_hsvrange_corrige_limites_invertidos_e_fora_da_faixa():
    r = core.HSVRange((200, -5, 10), (170, 300, 5))
    assert r.lower == (170, 0, 5) and r.upper == (170, 255, 5)
    hsv = cv2.cvtColor(np.full((2, 2, 3), 255, np.uint8), cv2.COLOR_BGR2HSV)
    assert core.HSVRange((0, 0, 250), (179, 10, 255)).mask(hsv).all()
