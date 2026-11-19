"""A calibração de cor é gravada (e sobrescrita) direto em object_finder/config/."""

import json

import numpy as np
from object_finder.calibration import core
from object_finder.calibration.calibrator_cv import Calibrador
from object_finder.stage1_adapter import white_thresholds_from_csv


def _cal(v_min_branco):
    return core.Calibration(green=core.HSVRange([40, 100, 60], [70, 255, 200]),
                            white=core.HSVRange([0, 0, v_min_branco], [179, 40, 255]))


def test_save_to_config_overwrites_in_every_dir(tmp_path):
    src, share = tmp_path / 'src_config', tmp_path / 'share_config'
    core.save_to_config(_cal(200), [src, share])
    core.save_to_config(_cal(230), [src, share])   # nova calibração: sobrescreve
    for d in (src, share):
        assert sorted(p.name for p in d.iterdir()) == ['calib.json', 'green_pixels.csv',
                                                       'white_pixels.csv']   # sem temporários
        lower, _ = white_thresholds_from_csv(d / 'white_pixels.csv')
        assert lower.tolist() == [0, 0, 230]
        assert json.loads((d / 'calib.json').read_text())['branco']['lower'] == [0, 0, 230]
        cal, green, white = core.load_calibration_dir(d)
        assert tuple(cal.white.lower) == (0, 0, 230) and green.is_file() and white.is_file()


def test_save_to_config_writes_once_through_symlinks(tmp_path):
    src = tmp_path / 'src'
    share = tmp_path / 'share'
    src.mkdir()
    share.mkdir()
    for name in ('green_pixels.csv', 'white_pixels.csv', 'calib.json'):
        (src / name).write_text('x')
        (share / name).symlink_to(src / name)          # colcon --symlink-install
    assert core.save_to_config(_cal(210), [src, share]) == [src]
    lower, _ = white_thresholds_from_csv(share / 'white_pixels.csv')
    assert lower.tolist() == [0, 0, 210]


def test_calibrador_save_goes_to_config_without_history(tmp_path):
    frame = np.zeros((48, 64, 3), np.uint8)
    frame[16:] = (40, 140, 40)
    cal = Calibrador({'f.png': frame}, out_root=None, initial=_cal(220),
                     config_dirs=[tmp_path / 'config'])
    saved = cal.save()
    assert saved == tmp_path / 'config'
    assert (tmp_path / 'config' / 'green_pixels.csv').is_file()
    assert not any(p.name.startswith('calib_') for p in tmp_path.iterdir())
