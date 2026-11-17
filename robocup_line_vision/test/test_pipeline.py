"""Pipeline completo, parâmetros e detector ONNX (sem ROS)."""

from pathlib import Path

import cv2
import numpy as np
import pytest

from robocup_line_vision.detector import make_detector, NullDetector
from robocup_line_vision.params import default_params_file, load_params, Params
from robocup_line_vision.pipeline import LineVisionPipeline

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(__file__).parent / 'data'


def test_yaml_padrao_igual_aos_padroes_do_codigo():
    p_yaml = load_params(str(ROOT / 'config' / 'params.yaml'))
    assert p_yaml == Params()
    assert default_params_file() is not None


def test_parametro_desconhecido_falha():
    with pytest.raises(KeyError):
        load_params(overrides={'grafo': {'nao_existe': 1}})


def test_pipeline_no_frame_do_webots():
    img = cv2.imread(str(DATA / 'frame_webots.png'))
    pipe = LineVisionPipeline(detector=NullDetector())
    r = pipe.process(img)
    assert r.stage1.field_detected
    assert len(r.lines) >= 2
    assert all(0 <= a < 2 * np.pi for c in r.crossings for a in c.heading_rays)
    assert set(r.timings_ms) >= {'etapa1', 'III-C', 'IV-A', 'IV-B', 'fusao', 'total'}
    s = r.summary()
    assert s['campo_detectado'] is True


def test_projecao_no_chao_com_camera_fov():
    img = cv2.imread(str(DATA / 'frame_webots.png'))
    p = load_params(overrides={'camera': {'modelo': 'fov'}})
    r = LineVisionPipeline(p).process(img)
    near = [ln for ln in r.lines if ln.distancia_m is not None]
    # reta vertical na imagem = raio saindo do robô: distância perpendicular 0 é correta
    assert near and all(0 <= ln.distancia_m < 20 for ln in near)
    assert any(ln.distancia_m > 1 for ln in near)


def test_detector_sem_modelo_e_nulo():
    assert isinstance(make_detector(None), NullDetector)
    with pytest.raises(FileNotFoundError):
        make_detector('/nao/existe.pt')
