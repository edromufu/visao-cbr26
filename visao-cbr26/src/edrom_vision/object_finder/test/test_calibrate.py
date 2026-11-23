"""Calibração de cor (`calibrar` = `python3 -m object_finder.pipeline.calibrate`): faixas, saídas e comandos."""

import os
import re
import sys

import cv2
import numpy as np
import pytest

from object_finder.pipeline import DEFAULT_COLOR_SPACES, VisionPipeline, build_color_detector, load_color_spaces_from_csv
from object_finder.pipeline import calibrate as cal
from object_finder.vision_parameters import _hsv_space
from scene import make_scene

LAUNCH_FILE = os.path.join(os.path.dirname(__file__), '..', 'launch', 'vision.launch.py')


def hsv_to_bgr_image(h, s, v, shape, rng, noise=(3, 15, 15)):
    """Imagem BGR com pixels HSV ao redor de (h, s, v)."""
    hsv = np.stack([
        np.clip(rng.normal(h, noise[0], shape), 0, 179),
        np.clip(rng.normal(s, noise[1], shape), 0, 255),
        np.clip(rng.normal(v, noise[2], shape), 0, 255)], axis=-1).astype(np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def dry_grass_frame(seed=0):
    """Campo 'real' amarelado (H=28), fora das faixas de exemplo (H 35-85), com céu em cima."""
    rng = np.random.default_rng(seed)
    frame = np.zeros((480, 640, 3), np.uint8)
    frame[:200] = hsv_to_bgr_image(105, 120, 220, (200, 640), rng)
    frame[200:] = hsv_to_bgr_image(28, 140, 120, (280, 640), rng)
    return frame


# ---------------------------------------------------------------- cálculo das faixas

def test_hue_range_wraps_around_zero_for_red():
    hues = np.concatenate([np.arange(172, 180), np.arange(0, 6)] * 50)
    h_min, h_max = cal.hue_range(hues, 2, 98, margin=3)
    assert h_min > h_max                              # faixa circular
    space = cal.ColorSpaceHSV(h_min, h_max, 0, 255, 0, 255)
    pixels = np.stack([hues, np.full_like(hues, 200), np.full_like(hues, 200)], axis=1)
    assert cal.coverage(space, pixels) > 0.95


def test_hue_range_plain_interval_when_not_wrapping():
    h_min, h_max = cal.hue_range(np.arange(50, 71).repeat(20), 2, 98, margin=4)
    assert 44 <= h_min <= 52 and 68 <= h_max <= 76 and h_min < h_max


def test_space_from_pixels_covers_samples_and_stays_in_bounds():
    rng = np.random.default_rng(1)
    pixels = np.clip(rng.normal([60, 150, 150], [4, 20, 20], (5000, 3)), 0, 255).astype(np.uint8)
    space = cal.space_from_pixels(pixels)
    assert cal.coverage(space, pixels) > 0.95
    assert 0 <= space.h_min <= space.h_max <= 179
    assert 0 <= space.s_min <= space.s_max <= 255 and 0 <= space.v_min <= space.v_max <= 255


def test_margin_widens_the_measured_range():
    pixels = np.stack([np.full(2000, 60), np.linspace(100, 120, 2000), np.linspace(150, 170, 2000)], axis=1)
    wide = cal.space_from_pixels(pixels, margin=(5, 30, 40))
    tight = cal.space_from_pixels(pixels, margin=(0, 0, 0))
    assert wide.s_min <= 72 and wide.s_max >= 148 and wide.v_min <= 112 and wide.v_max >= 208
    assert tight.s_min >= 99 and tight.s_max <= 121


def test_fit_spaces_ignores_hue_for_white_and_keeps_uncalibrated_classes():
    samples = cal.Samples()
    bluish_white = hsv_to_bgr_image(105, 20, 240, (40, 80), np.random.default_rng(4), noise=(1, 3, 3))
    samples.add_box('white', bluish_white, (0, 0, 80, 40))
    spaces, calibrated, _ = cal.fit_spaces(samples, dict(DEFAULT_COLOR_SPACES))
    assert calibrated == ['white'] and (spaces['white'].h_min, spaces['white'].h_max) == (0, 179)
    assert spaces['field'] == DEFAULT_COLOR_SPACES['field'] and spaces['marking'] == spaces['white']


def test_white_ignores_hue():
    rng = np.random.default_rng(2)
    pixels = np.stack([rng.integers(0, 180, 3000), rng.integers(0, 30, 3000), rng.integers(220, 256, 3000)], axis=1)
    space = cal.space_from_pixels(pixels, hue_free=True)
    assert (space.h_min, space.h_max) == (0, 179)


def test_warnings_flag_a_region_that_is_not_the_class():
    sky = np.full((3000, 3), (105, 120, 220), np.uint8)       # céu amostrado como "campo"
    space = cal.space_from_pixels(sky)
    assert any('não ser grama' in w for w in cal.check_samples('field', sky, space))
    few = sky[:100]
    assert any('pixels amostrados' in w for w in cal.check_samples('field', few, space))


def test_parse_sample_accepts_valid_and_rejects_invalid():
    assert cal.parse_sample('field=0.4,0.8,0.2,0.15') == ('field', (0.4, 0.8, 0.2, 0.15))
    for bad in ('field', 'grass=0.1,0.1,0.1,0.1', 'field=0.1,0.1,0.1', 'field=0.9,0.1,0.3,0.1', 'field=0.1,0.1,0,0.1'):
        with pytest.raises(ValueError):
            cal.parse_sample(bad)


# ---------------------------------------------------------------- saídas

def test_csv_round_trips_through_the_pipeline_loader(tmp_path):
    spaces = dict(DEFAULT_COLOR_SPACES)
    spaces['field'] = cal.ColorSpaceHSV(20, 40, 90, 200, 60, 180)
    path = tmp_path / 'hsv.csv'
    path.write_text(cal.spaces_to_csv(spaces), encoding='utf-8')
    loaded = load_color_spaces_from_csv(str(path))
    assert loaded['field'] == spaces['field']
    assert loaded['marking'] == loaded['white'] == spaces['white']
    assert loaded['red'] == spaces['red']                          # hue circular preservado


def test_ros_yaml_only_has_calibrated_classes_and_passes_node_validation():
    spaces = dict(DEFAULT_COLOR_SPACES)
    spaces['field'] = cal.ColorSpaceHSV(20, 40, 90, 200, 60, 180)
    text = cal.spaces_to_ros_yaml(spaces, ['field'])
    assert 'field_min: [20, 90, 60]' in text and 'field_max: [40, 200, 180]' in text
    assert 'red_min' not in text
    yaml = pytest.importorskip('yaml')
    params = yaml.safe_load(text)['vision']['ros__parameters']['hsv']
    assert _hsv_space('field', params['field_min'], params['field_max']) == spaces['field']


def test_ros_yaml_uses_the_node_name_of_the_launch():
    # Se o nome não bater, o ROS ignora o params_file em silêncio e a calibração não vale.
    with open(LAUNCH_FILE, encoding='utf-8') as f:
        launch = f.read()
    finder = launch[launch.index("executable='finder'"):]
    assert re.search(r"name='([^']+)'", finder).group(1) == cal.NODE_NAME


def test_camera_index_accepts_number_and_device_path():
    assert cal.camera_index('2') == 2 and cal.camera_index('/dev/video2') == 2
    assert cal.camera_index('jogo.mp4') is None and cal.camera_index('/dev/videox') is None


# ---------------------------------------------------------------- comandos sem tela

def test_hsv_headless_on_an_image_fixes_a_field_the_defaults_miss(tmp_path):
    frame = dry_grass_frame()
    image = tmp_path / 'campo.png'
    cv2.imwrite(str(image), frame)
    field_rows = slice(200, 480)
    default_mask = DEFAULT_COLOR_SPACES['field'].mask(frame)
    assert np.count_nonzero(default_mask[field_rows]) / default_mask[field_rows].size < 0.1   # o padrão não vê o campo

    out = tmp_path / 'calib'
    code = cal.main(['hsv', '--source', str(image), '--sample', 'field=0.2,0.6,0.5,0.3', '--out', str(out)])
    assert code == 0
    for name in ('hsv.csv', 'hsv_params.yaml', 'hsv_preview.png'):
        assert (out / name).exists()

    spaces = load_color_spaces_from_csv(str(out / 'hsv.csv'))
    mask = spaces['field'].mask(frame)
    assert np.count_nonzero(mask[field_rows]) / mask[field_rows].size > 0.95
    assert np.count_nonzero(mask[:200]) == 0                                                   # céu não entra
    assert VisionPipeline(build_color_detector(spaces), seed=0).run(frame).field_detected


def test_hsv_headless_calibrates_white_on_the_synthetic_scene(tmp_path):
    image = tmp_path / 'cena.png'
    cv2.imwrite(str(image), make_scene())
    out = tmp_path / 'calib'
    code = cal.main(['hsv', '--source', str(image), '--out', str(out),
                     '--sample', 'field=0.40,0.80,0.20,0.15', '--sample', 'white=0.10,0.724,0.18,0.004'])
    assert code == 0
    yaml_text = (out / 'hsv_params.yaml').read_text(encoding='utf-8')
    assert 'field_min' in yaml_text and 'white_min' in yaml_text and 'blue_min' not in yaml_text


def test_hsv_headless_from_camera_discards_warmup_and_samples_the_rest(tmp_path, monkeypatch):
    warmup = [np.zeros((480, 640, 3), np.uint8)] * 3               # exposição ainda instável: tudo preto
    frames = warmup + [dry_grass_frame(seed) for seed in range(5)]

    class FakeCap:
        def __init__(self):
            self.reads = 0

        def read(self):
            frame = frames[self.reads % len(frames)]
            self.reads += 1
            return True, frame

        def release(self):
            self.released = True

    cap = FakeCap()
    monkeypatch.setattr(cal, 'open_camera', lambda *a, **k: cap)
    code = cal.main(['hsv', '--source', '0', '--frames', '5', '--skip', '3', '--out', str(tmp_path),
                     '--sample', 'field=0.2,0.6,0.5,0.3'])
    assert code == 0 and cap.reads == 8 and cap.released
    spaces = load_color_spaces_from_csv(str(tmp_path / 'hsv.csv'))
    assert spaces['field'].v_min >= 40                              # o preto do aquecimento ficou de fora
    assert (tmp_path / 'hsv_preview.png').exists()


def test_snapshot_writes_photo_and_grid(tmp_path, monkeypatch):
    class FakeCap:
        def read(self):
            return True, dry_grass_frame()

        def release(self):
            pass

    monkeypatch.setattr(cal, 'open_camera', lambda *a, **k: FakeCap())
    assert cal.main(['snapshot', '--source', '0', '--skip', '1', '--out', str(tmp_path)]) == 0
    assert (tmp_path / 'snapshot.png').exists() and (tmp_path / 'snapshot_grade.png').exists()


def test_errors_return_code_2_with_a_message(tmp_path, capsys, monkeypatch):
    assert cal.main(['hsv', '--source', str(tmp_path / 'nao_existe.png'), '--sample', 'field=0.1,0.1,0.2,0.2']) == 2
    assert 'ERRO' in capsys.readouterr().err
    assert cal.main(['hsv', '--source', '0', '--sample', 'grama=0.1,0.1,0.2,0.2']) == 2
    if sys.platform.startswith('linux'):
        monkeypatch.delenv('DISPLAY', raising=False)
        monkeypatch.delenv('WAYLAND_DISPLAY', raising=False)
        image = tmp_path / 'x.png'
        cv2.imwrite(str(image), dry_grass_frame())
        assert cal.main(['hsv', '--source', str(image)]) == 2                  # interativo sem tela
        assert 'sem tela' in capsys.readouterr().err


# ---------------------------------------------------------------- modo interativo (janela simulada)

def fake_window(monkeypatch, make_steps):
    """Troca as chamadas de janela do OpenCV; `make_steps(handlers)` devolve a tecla de cada `waitKey`."""
    handlers = {}
    queue = iter(make_steps(handlers))
    monkeypatch.setenv('DISPLAY', ':0')
    monkeypatch.setattr(cv2, 'namedWindow', lambda *a, **k: None)
    monkeypatch.setattr(cv2, 'setMouseCallback', lambda name, fn: handlers.update(callback=fn))
    monkeypatch.setattr(cv2, 'imshow', lambda name, image: None)
    monkeypatch.setattr(cv2, 'waitKey', lambda ms: next(queue)())
    monkeypatch.setattr(cv2, 'destroyAllWindows', lambda: None)


def drag(handlers, start, end):
    def action():
        callback = handlers['callback']
        callback(cv2.EVENT_LBUTTONDOWN, start[0], start[1], 0, None)
        callback(cv2.EVENT_MOUSEMOVE, end[0], end[1], 0, None)
        callback(cv2.EVENT_LBUTTONUP, end[0], end[1], 0, None)
        return -1
    return action


def test_gui_drag_samples_a_region_and_s_saves(tmp_path, monkeypatch):
    image = tmp_path / 'campo.png'
    cv2.imwrite(str(image), dry_grass_frame())
    fake_window(monkeypatch, lambda h: [lambda: -1, drag(h, (100, 300), (400, 420)), lambda: ord('p'),
                                        lambda: ord('s'), lambda: ord('q')])
    out = tmp_path / 'calib'
    assert cal.main(['hsv', '--source', str(image), '--out', str(out)]) == 0
    spaces = load_color_spaces_from_csv(str(out / 'hsv.csv'))
    mask = spaces['field'].mask(dry_grass_frame())
    assert np.count_nonzero(mask[200:]) / mask[200:].size > 0.95
    assert (out / 'hsv_params.yaml').exists() and (out / 'hsv_preview.png').exists()


def test_gui_quit_without_saving_writes_nothing(tmp_path, monkeypatch, capsys):
    image = tmp_path / 'campo.png'
    cv2.imwrite(str(image), dry_grass_frame())
    fake_window(monkeypatch, lambda h: [lambda: -1, drag(h, (100, 300), (400, 420)), lambda: ord('q')])
    out = tmp_path / 'calib'
    assert cal.main(['hsv', '--source', str(image), '--out', str(out)]) == 0
    assert not out.exists()
    assert 'saiu sem salvar' in capsys.readouterr().out


def test_gui_x_clears_the_class_and_s_then_does_nothing(tmp_path, monkeypatch):
    image = tmp_path / 'campo.png'
    cv2.imwrite(str(image), dry_grass_frame())
    fake_window(monkeypatch, lambda h: [lambda: -1, drag(h, (100, 300), (400, 420)), lambda: ord('x'),
                                        lambda: ord('s'), lambda: ord('q')])
    out = tmp_path / 'calib'
    assert cal.main(['hsv', '--source', str(image), '--out', str(out)]) == 0
    assert not out.exists()                                       # sem classe calibrada, 's' não grava


# --- calibrar --ros (imagem do usb_cam) ------------------------------------------------------------

def test_ros_option_passes_the_topic_and_the_device_to_open_camera(tmp_path, monkeypatch):
    calls = []

    class FakeCap:
        def read(self):
            return True, dry_grass_frame(0)

        def release(self):
            pass

    def fake_open(source, *_args, ros_topic=None):
        calls.append((source, ros_topic))
        return FakeCap()

    monkeypatch.setattr(cal, 'open_camera', fake_open)
    assert cal.main(['snapshot', '--ros', '--skip', '0', '--out', str(tmp_path)]) == 0
    assert cal.main(['snapshot', '--ros', '/robo/img', '--source', '/dev/video2', '--skip', '0',
                     '--out', str(tmp_path)]) == 0
    assert calls == [('', cal.DEFAULT_ROS_TOPIC), ('/dev/video2', '/robo/img')]


def test_source_defaults_to_the_video_device_of_usb_cam_yaml(monkeypatch):
    from object_finder.pipeline import ros_camera
    monkeypatch.setattr(ros_camera, 'read_usb_cam_params', lambda *a: {'video_device': '/dev/video7'})
    assert cal.parse_args(['snapshot']).source == '/dev/video7'
    assert cal.parse_args(['snapshot', '--source', '3']).source == '3'


def test_ros_image_conversion_handles_rgb_yuyv_and_row_padding():
    from object_finder.pipeline.ros_camera import image_to_bgr
    bgr = np.zeros((4, 6, 3), np.uint8)
    bgr[:] = (10, 200, 30)                                          # verde do campo
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    padded = np.zeros((4, 6 * 3 + 2), np.uint8)                     # step maior que largura*3
    padded[:, :18] = rgb.reshape(4, 18)
    assert np.array_equal(image_to_bgr('rgb8', 4, 6, 20, padded.tobytes()), bgr)
    assert np.array_equal(image_to_bgr('bgr8', 4, 6, 18, bgr.tobytes()), bgr)

    def yuyv(y, u, v):                                              # Y U Y V, a mesma cor em todos os pixels
        return np.tile(np.array([y, u, y, v], np.uint8), (4, 3)).tobytes()

    gray = image_to_bgr('yuv422_yuy2', 4, 6, 12, yuyv(120, 128, 128))
    assert gray.shape == (4, 6, 3) and np.ptp(gray[0, 0].astype(int)) <= 1   # U = V = 128: sem cor
    b, g, r = image_to_bgr('yuv422_yuy2', 4, 6, 12, yuyv(128, 70, 42))[0, 0].astype(int)
    assert g > b + 100 and g > r + 100                              # U e V baixos: verde

    with pytest.raises(RuntimeError, match='não suportado'):
        image_to_bgr('bayer_rggb8', 4, 6, 6, bytes(24))
