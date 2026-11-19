"""Sessão simulada do calibrador (sem janela)."""

import cv2
import numpy as np

from object_finder.calibration import core
from object_finder.calibration.calibrator_cv import Calibrador
from object_finder.stage1_adapter import Stage1Segmenter, white_thresholds_from_csv


def campo_sintetico(verde=(40, 150, 60), branco=(235, 235, 235)):
    """Céu azul em cima, carpete verde embaixo, duas linhas brancas."""
    img = np.zeros((240, 320, 3), np.uint8)
    img[:80] = (200, 120, 60)
    img[80:] = verde
    rng = np.random.default_rng(0)
    noise = rng.integers(-6, 7, img[80:].shape)
    img[80:] = np.clip(img[80:].astype(int) + noise, 0, 255).astype(np.uint8)
    cv2.line(img, (0, 170), (319, 170), branco, 5)
    cv2.line(img, (160, 90), (160, 239), branco, 5)
    return img


class FakeClock:

    def __init__(self):
        self.t = 1_700_000_000.0

    def __call__(self):
        return self.t


def test_recalibracao_rapida_dois_cliques(tmp_path):
    img = campo_sintetico()
    cal = Calibrador({'f.png': img}, tmp_path, clock=FakeClock())
    s1, _ = cal.evaluate()
    assert not s1.field_detected  # calibração do Webots não serve aqui
    cal.on_key(ord('r'))
    cal.on_mouse(cv2.EVENT_LBUTTONDOWN, 60, 210)    # carpete
    cal.on_mouse(cv2.EVENT_LBUTTONDOWN, 100, 170)   # linha horizontal
    assert cal.quick_step is None
    s1, m = cal.evaluate()
    assert s1.field_detected and m['ok'], m
    assert s1.skeleton.sum() > 10
    d = cal.save()
    lower, up = white_thresholds_from_csv(d / 'white_pixels.csv')
    assert tuple(lower) == cal.white.lower and tuple(up) == cal.white.upper
    seg = Stage1Segmenter(d / 'green_pixels.csv', d / 'white_pixels.csv')
    s1b = seg.process(img)
    assert np.array_equal(s1b.skeleton, s1.skeleton)  # o que foi salvo = o que foi visto


def test_pincel_retangulo_desfazer_e_ajuste_fino(tmp_path):
    img = campo_sintetico()
    cal = Calibrador({'f.png': img}, tmp_path)
    cal.on_key(ord('g'))
    cal.on_key(ord('t'))  # retângulo
    cal.on_mouse(cv2.EVENT_LBUTTONDOWN, 10, 200)
    cal.on_mouse(cv2.EVENT_MOUSEMOVE, 120, 235)
    cal.on_mouse(cv2.EVENT_LBUTTONUP, 120, 235)
    cal.on_key(ord('b'))
    cal.on_key(ord('t'))  # pincel
    cal.on_mouse(cv2.EVENT_LBUTTONDOWN, 20, 170)
    for x in range(22, 140, 3):
        cal.on_mouse(cv2.EVENT_MOUSEMOVE, x, 170)
    cal.on_mouse(cv2.EVENT_LBUTTONUP, 140, 170)
    assert [s.classe for s in cal.samples] == ['verde', 'branco']
    assert cal.evaluate()[0].field_detected
    v0 = cal.white.lower[2]
    cal.set_channel('branco', 'lower', 2, v0 + 5)
    assert cal.manual and cal.white.lower[2] == v0 + 5
    cal.on_mouse(cv2.EVENT_RBUTTONDOWN, 5, 5)  # desfazer
    assert len(cal.samples) == 1
    img_out = cal.render()
    assert img_out.shape[0] == img.shape[0] + 118


def test_sair_pede_confirmacao_se_nao_salvou(tmp_path):
    cal = Calibrador({'f.png': campo_sintetico()}, tmp_path)
    cal.add_sample(core.Sample('verde', 'clique', 'f.png', pontos=[(50, 200)], raio=8))
    assert cal.on_key(27) is True      # primeiro ESC só avisa
    assert cal.on_key(27) is False     # segundo sai
    cal2 = Calibrador({'f.png': campo_sintetico()}, tmp_path)
    assert cal2.on_key(ord('q')) is False  # nada a salvar: sai direto


def test_camera_ao_vivo_congela_e_amostra(tmp_path):
    cal = Calibrador({}, tmp_path, clock=FakeClock())
    cal.set_live_frame(campo_sintetico())
    cal.on_key(ord('r'))
    cal.on_mouse(cv2.EVENT_LBUTTONDOWN, 60, 210)
    cal.set_live_frame(campo_sintetico())  # frame novo entre os cliques
    cal.on_mouse(cv2.EVENT_LBUTTONDOWN, 100, 170)
    assert len(cal.frames) == 2 and len(cal.samples) == 2
    assert {s.imagem for s in cal.samples} == set(cal.frames)
    cal.on_key(ord('f'))
    assert cal.frozen
    d = cal.save()
    assert len(list((d / 'frames').iterdir())) == 2


def test_tecla_A_tira_placas_brancas_da_fronteira(tmp_path):
    img = campo_sintetico()
    img[64:80] = (212, 212, 212)  # placas cinza-claro encostadas no campo
    cal = Calibrador({'f.png': img}, tmp_path)
    cal.add_sample(core.Sample('verde', 'retangulo', 'f.png', retangulo=(10, 190, 140, 235)))
    cal.add_sample(core.Sample('branco', 'pincel', 'f.png',
                   pontos=[(10, 170), (150, 170)], raio=2))
    cal.set_channel('branco', 'lower', 2, 200)  # usuária deixou largo demais
    s1, m = cal.evaluate()
    assert m['branco_na_fronteira'] > 0.25
    sug = cal.apply_vmin_suggestion()
    assert sug == 213
    s1, m = cal.evaluate()
    assert m['branco_na_fronteira'] <= 0.25 and s1.skeleton.sum() > 10


def test_importar_json_do_html(tmp_path):
    import json

    from object_finder.calibration.importar_json import importar
    j = {'versao': 1, 'formato': 'object_finder.calib', 'origem': 'calibrador.html',
         'criada_em': '2026-11-13T09:15:00', 'imagens': ['a.png'], 'resolucao': [640, 480],
         'verde': {'lower': [48, 125, 106], 'upper': [65, 255, 191]},
         'branco': {'lower': [0, 0, 241], 'upper': [179, 37, 255]}, 'ajuste_manual': False,
         'amostras': [{'classe': 'verde', 'tipo': 'clique', 'imagem': 'a.png', 'pontos': [[1, 2]],
                       'raio': 16, 'retangulo': None}], 'metricas': {}}
    p = tmp_path / 'calib_x.json'
    p.write_text(json.dumps(j))
    d = importar(p, tmp_path / 'cal')
    assert d.name == 'calib_20261113_091500'
    lower, up = white_thresholds_from_csv(d / 'white_pixels.csv')
    assert lower.tolist() == [0, 0, 241] and up.tolist() == [179, 37, 255]
    assert (tmp_path / 'cal' / 'ultima' / 'green_pixels.csv').is_file()
