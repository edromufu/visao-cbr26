"""Espaço de cor dinâmico do campo (artigo Bit-Bots, Seção 3.1)."""

import cv2
import numpy as np

from object_finder.pipeline import (
    DEFAULT_COLOR_SPACES,
    ColorSpaceHSV,
    DynamicColorSpace,
    PipelineConfig,
    VisionPipeline,
    build_color_detector,
)
from object_finder.pipeline.dynamic_color import below_boundary_mask

WALL = (110, 60, 200)       # parede azulada acima do campo
ODD = (20, 200, 200)        # cor estranha (laranja) que aparece espalhada no campo


def field_scene(seed, v_field=180, wall=WALL, speckles=None):
    """240x320: parede em cima (linhas 0-79); campo verde com V em torno de `v_field`."""
    rng = np.random.default_rng(seed)
    hsv = np.empty((240, 320, 3), np.uint8)
    hsv[..., 0] = np.clip(rng.normal(60, 2, (240, 320)), 0, 179)
    hsv[..., 1] = np.clip(rng.normal(180, 10, (240, 320)), 0, 255)
    hsv[..., 2] = np.clip(rng.normal(v_field, 12, (240, 320)), 0, 255)
    hsv[:80] = wall
    if speckles is not None:                    # pixels isolados no campo, cercados de verde
        ys = rng.integers(90, 240, 300)
        xs = rng.integers(0, 320, 300)
        hsv[ys, xs] = speckles
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def calibrated_spaces():
    spaces = dict(DEFAULT_COLOR_SPACES)
    spaces['field'] = ColorSpaceHSV(50, 70, 100, 255, 150, 255)    # calibrado com V em torno de 180
    return spaces


def field_coverage(pipeline, frame):
    mask = pipeline.color_detector.field_mask(frame)
    return np.count_nonzero(mask[80:]) / mask[80:].size


def make_pipeline(dynamic):
    config = PipelineConfig(process_width=0, n_line_samples=0, dynamic_color=dynamic, dynamic_every_n_frames=1)
    return VisionPipeline(build_color_detector(calibrated_spaces()), config, seed=0)


def darkening(pipeline, frames=60):
    """A luz cai aos poucos: V do campo vai de 180 a 110 (abaixo da calibração, 150)."""
    for i in range(frames):
        result = pipeline.run(field_scene(i, v_field=180 - 70 * i / (frames - 1)))
    return result


def test_follows_a_gradual_change_of_light():
    pipeline = make_pipeline(dynamic=True)
    result = darkening(pipeline)
    assert result.field_detected and result.dynamic_colors > 0
    assert field_coverage(pipeline, field_scene(999, v_field=110)) > 0.85   # sem o dinâmico: < 0.1
    assert np.count_nonzero(pipeline.color_detector.field_mask(field_scene(999, v_field=110))[:80]) == 0


def test_without_dynamic_color_the_darker_field_is_lost():
    pipeline = make_pipeline(dynamic=False)
    result = darkening(pipeline)
    assert result.dynamic_colors == 0
    assert field_coverage(pipeline, field_scene(999, v_field=110)) < 0.1


def test_isolated_colors_inside_the_field_are_learned():
    pipeline = make_pipeline(dynamic=True)
    for seed in range(5):
        pipeline.run(field_scene(seed, speckles=ODD))
    odd = cv2.cvtColor(np.full((1, 1, 3), ODD, np.uint8), cv2.COLOR_HSV2BGR)
    assert pipeline.color_detector.field_mask(odd).all()


def test_colors_seen_above_the_boundary_are_never_learned():
    pipeline = make_pipeline(dynamic=True)
    for seed in range(5):
        pipeline.run(field_scene(seed, wall=ODD, speckles=ODD))      # a mesma cor também está na parede
    odd = cv2.cvtColor(np.full((1, 1, 3), ODD, np.uint8), cv2.COLOR_HSV2BGR)
    assert not pipeline.color_detector.field_mask(odd).any()


def test_forgets_colors_that_stop_appearing():
    space = DynamicColorSpace(history=3)
    hsv = np.zeros((20, 20, 3), np.uint8)
    hsv[..., 0], hsv[..., 1], hsv[..., 2] = 60, 180, 90
    field = np.full((20, 20), 255, np.uint8)
    field[10, 10] = 0                                           # um pixel fora, cercado de campo
    below = np.full((20, 20), 255, np.uint8)
    assert space.update(hsv, field, below) == 1 and space.n_colors == 1
    nothing = np.zeros((20, 20), np.uint8)
    for _ in range(3):
        space.update(hsv, nothing, below)                      # nada cercado de campo
    assert space.n_colors == 0 and not space.mask(hsv).any()


def test_below_boundary_mask_fills_under_the_points():
    mask = below_boundary_mask((10, 10), [(0, 4), (9, 4)])
    assert not mask[:4].any() and mask[4:].all()
