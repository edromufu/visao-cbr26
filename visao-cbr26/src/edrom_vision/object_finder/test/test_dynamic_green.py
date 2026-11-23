"""Verde dinâmico (artigo Bit-Bots, Seção 3.1) sobre a LUT do verde da etapa 1."""

import cv2
import numpy as np

from object_finder.dynamic_color import DynamicColorSpace
from object_finder.params import load_params
from object_finder.pipeline import LineVisionPipeline
from object_finder.stage1_adapter import Stage1Segmenter

SKY = (105, 120, 220)       # HSV
ODD = (20, 200, 200)        # laranja: aparece espalhado no campo


def scene(seed, v_field=180, sky=SKY, speckles=None):
    """320x240 (BGR): céu nas 80 linhas de cima, campo verde com V em torno de `v_field` e duas linhas."""
    rng = np.random.default_rng(seed)
    hsv = np.empty((240, 320, 3), np.uint8)
    hsv[..., 0] = np.clip(rng.normal(60, 2, (240, 320)), 0, 179)
    hsv[..., 1] = np.clip(rng.normal(180, 10, (240, 320)), 0, 255)
    hsv[..., 2] = np.clip(rng.normal(v_field, 12, (240, 320)), 0, 255)
    hsv[:80] = sky
    if speckles is not None:
        hsv[rng.integers(90, 240, 300), rng.integers(0, 320, 300)] = speckles
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    cv2.line(img, (0, 170), (319, 170), (235, 235, 235), 5)
    cv2.line(img, (160, 90), (160, 239), (235, 235, 235), 5)
    return img


def segmenter(dynamic):
    seg = Stage1Segmenter()
    seg.set_green_box((50, 100, 150), (70, 255, 255))     # calibrado com V em torno de 180
    seg.set_dynamic(DynamicColorSpace() if dynamic else None)
    return seg


def green_coverage(seg, frame):
    s1 = seg.process(frame)
    rows = s1.green_mask[90:]
    return np.count_nonzero(rows) / rows.size, s1


def darkening(seg, frames=60):
    for i in range(frames):
        s1 = seg.process(scene(i, v_field=180 - 70 * i / (frames - 1)))
        seg.learn(s1)


def test_follows_a_gradual_change_of_light():
    seg = segmenter(dynamic=True)
    darkening(seg)
    coverage, s1 = green_coverage(seg, scene(999, v_field=110))
    assert coverage > 0.8 and s1.field_detected
    assert not s1.green_mask[:80].any()                         # o céu não virou campo


def test_without_dynamic_green_the_darker_field_is_lost():
    seg = segmenter(dynamic=False)
    darkening(seg)
    coverage, _ = green_coverage(seg, scene(999, v_field=110))
    assert coverage < 0.1


def test_colors_seen_above_the_boundary_are_never_learned():
    odd = cv2.cvtColor(np.full((1, 1, 3), ODD, np.uint8), cv2.COLOR_HSV2BGR)
    for sky, learned in ((SKY, True), (ODD, False)):            # com a mesma cor no céu, não aprende
        seg = segmenter(dynamic=True)
        for seed in range(5):
            seg.learn(seg.process(scene(seed, sky=sky, speckles=ODD)))
        h, s, v = cv2.cvtColor(odd, cv2.COLOR_BGR2HSV)[0, 0]
        assert bool(seg.vendor_segmenter.lut_verde[h, s, v]) is learned


def test_calibration_box_is_kept_under_the_learned_colors():
    seg = segmenter(dynamic=True)
    darkening(seg, frames=20)
    seg.set_green_box((50, 100, 150), (70, 255, 255))           # recalibrar não apaga o aprendido
    assert seg.dynamic.n_colors > 0
    seg.set_dynamic(None)                                       # desligar volta à calibração pura
    coverage, _ = green_coverage(seg, scene(999, v_field=110))
    assert coverage < 0.1


def test_pipeline_turns_it_on_from_params():
    pipe = LineVisionPipeline(load_params(None))
    assert pipe.seg.dynamic is not None
    for seed in range(3):
        result = pipe.process(scene(seed))
    assert 'verde_aprendido' in result.info
    off = LineVisionPipeline(load_params(None, {'verde_dinamico': {'ativo': False}}))
    assert off.seg.dynamic is None and 'verde_aprendido' not in off.process(scene(0)).info
