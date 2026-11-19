"""Testes da captura (sem câmera/ROS) e da decodificação de sensor_msgs/Image."""

from types import SimpleNamespace

import cv2
import numpy as np
from object_finder.calibration.capture_frames import capture
from object_finder.calibration.capture_frames_ros import FrameSaver
from object_finder.calibration.ros_image import image_msg_to_bgr
import pytest


def _img():
    rng = np.random.default_rng(1)
    return rng.integers(0, 255, (5, 7, 3), dtype=np.uint8)


def _msg(arr, enc, pad=0):
    h, w = arr.shape[:2]
    ch = 1 if arr.ndim == 2 else arr.shape[2]
    rows = arr.reshape(h, w * ch)
    if pad:
        rows = np.hstack([rows, np.zeros((h, pad), np.uint8)])
    return SimpleNamespace(encoding=enc, height=h, width=w, step=w * ch + pad,
                           data=rows.tobytes(), is_bigendian=0)


@pytest.mark.parametrize('enc,conv', [
    ('bgr8', None), ('rgb8', cv2.COLOR_BGR2RGB), ('bgra8', cv2.COLOR_BGR2BGRA),
    ('rgba8', cv2.COLOR_BGR2RGBA)])
@pytest.mark.parametrize('pad', [0, 3])
def test_decodifica_encodings_com_step(enc, conv, pad):
    bgr = _img()
    src = bgr if conv is None else cv2.cvtColor(bgr, conv)
    out = image_msg_to_bgr(_msg(src, enc, pad))
    assert out.shape == bgr.shape and np.array_equal(out, bgr)


def test_mono8_e_encoding_invalido():
    g = _img()[..., 0]
    out = image_msg_to_bgr(_msg(g, 'mono8'))
    assert np.array_equal(out[..., 1], g)
    with pytest.raises(ValueError):
        image_msg_to_bgr(_msg(g, '16UC1'))


def test_capture_salva_n_frames_no_intervalo(tmp_path):
    t = {'now': 0.0}

    def clock():
        return t['now']

    def sleep(dt):
        t['now'] += max(dt, 0.01)

    def read():
        t['now'] += 0.1
        return _img()

    saved = capture(read, 3, 1.0, tmp_path, clock=clock, sleep=sleep)
    assert len(saved) == 3 and all(p.is_file() for p in saved)
    assert t['now'] >= 2.0  # respeitou o intervalo


def test_frame_saver_ros(tmp_path):
    s = FrameSaver(2, 1.0, tmp_path)
    m = _msg(_img(), 'bgr8')
    assert s.on_msg(m, 0.0) is not None
    assert s.on_msg(m, 0.5) is None
    assert s.on_msg(m, 1.1) is not None
    assert s.done and s.on_msg(m, 5.0) is None
