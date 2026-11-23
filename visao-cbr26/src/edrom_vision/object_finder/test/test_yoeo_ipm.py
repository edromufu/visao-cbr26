import math
import os

import numpy as np
import pytest

from object_finder.kinematics import CameraKinematics, RobotModel, fixed_pose, rot_y
from object_finder.projection import (
    Intrinsics, ball_ground_point, footpoint_ground_point, ground_to_pixel, mask_line_points, pixel_to_ground)

# Robô de teste com nomes próprios (não é a Aurea): torso a 0,30 m do chão com as pernas retas.
URDF = os.path.join(os.path.dirname(__file__), 'robo_teste.urdf')
SOLE = (0.0, 0.0, -0.05)


@pytest.fixture
def kin():
    return CameraKinematics(RobotModel(URDF), 'tronco', 'cabeca', {'left': 'pe_e', 'right': 'pe_d'},
                            camera_offset=(0.05, 0.0, 0.0), sole_offset={'left': SOLE, 'right': SOLE})


def cam(tilt=0.6, pan=0.0, h=0.49):
    return fixed_pose(h, 0.0, pan, tilt, (0.05, 0.0, 0.02)).footprint_camera


def crouch(a):
    """Postura simétrica: quadril e tornozelo -a, joelho 2a (torso continua vertical)."""
    return {f'{j}_{s}': v for s in 'ed' for j, v in (('quadril', -a), ('joelho', 2 * a), ('tornozelo', -a))}


# ---------------- modo fixed (sem URDF) ----------------
def test_fixed_height_is_tilt_axis_plus_offset():
    pose = fixed_pose(0.49, 0.0, 0.0, 0.0, (0.05, 0.0, 0.02))
    assert pose.height == pytest.approx(0.51, abs=1e-9)
    assert pose.footprint_camera[0, 3] == pytest.approx(0.05, abs=1e-9)
    assert pose.pitch == pytest.approx(0.0, abs=1e-9)
    assert pose.footprint_torso is None


def test_fixed_tilt_and_body_pitch_add_up():
    assert fixed_pose(0.49, 0.0, 0.0, 0.5, (0, 0, 0)).pitch == pytest.approx(0.5, abs=1e-9)
    assert fixed_pose(0.49, 0.1, 0.0, 0.5, (0, 0, 0)).pitch == pytest.approx(0.6, abs=1e-9)


def test_fixed_tilt_moves_lens_down():
    """Olhando para baixo, a lente que fica à frente do eixo desce."""
    level = fixed_pose(0.49, 0.0, 0.0, 0.0, (0.05, 0, 0)).height
    down = fixed_pose(0.49, 0.0, 0.0, 0.5, (0.05, 0, 0)).height
    assert down == pytest.approx(level - 0.05 * math.sin(0.5), abs=1e-9)


def test_fixed_pan_turns_left():
    pose = fixed_pose(0.49, 0.0, 0.3, 0.0, (0.05, 0, 0))
    assert pose.footprint_camera[1, 3] > 0        # lente vai para a esquerda


# ---------------- modo kinematics (URDF de outro robô) ----------------
def test_kinematics_straight_and_crouched(kin):
    straight = kin.pose({})
    assert straight.footprint_torso[2, 3] == pytest.approx(0.30, abs=1e-9)
    assert straight.height == pytest.approx(0.30 + 0.15 + 0.05, abs=1e-9)
    crouched = kin.pose(crouch(0.4))
    assert crouched.footprint_torso[2, 3] < 0.30 - 0.01
    assert np.allclose(crouched.footprint_torso[:3, :3], np.eye(3), atol=1e-9)


def test_kinematics_ankle_pitch_tilts_torso(kin):
    pose = kin.pose({'tornozelo_e': -0.1, 'tornozelo_d': -0.1})
    assert np.allclose(pose.footprint_torso[:3, :3], rot_y(0.1), atol=1e-9)


def test_kinematics_head_joints_from_urdf(kin):
    assert kin.pose({'tilt': 0.5}).pitch == pytest.approx(0.5, abs=1e-9)


def test_kinematics_support_is_lower_foot(kin):
    joints = crouch(0.3)
    joints.update({'quadril_d': -0.6, 'joelho_d': 1.2, 'tornozelo_d': -0.6})    # perna direita levantada
    assert kin.pose(joints).support == 'left'
    joints = crouch(0.3)
    joints.update({'quadril_e': -0.6, 'joelho_e': 1.2, 'tornozelo_e': -0.6})
    assert kin.pose(joints).support == 'right'


def test_kinematics_wrong_link_names_fail_early():
    with pytest.raises(ValueError, match='links disponíveis'):
        CameraKinematics(RobotModel(URDF), 'base_link', 'head_tilt_link', {'left': 'pe_e', 'right': 'pe_d'})


# ---------------- projeção ----------------
@pytest.mark.parametrize('distortion', [None, [-0.3, 0.1, 0.001, -0.001, 0.0]])
def test_pixel_ground_roundtrip(distortion):
    pose = cam(tilt=0.6, pan=0.2)
    intr = Intrinsics([[500, 0, 330], [0, 505, 235], [0, 0, 1]], distortion)
    for x, y in ((1.0, 0.2), (2.5, -0.4), (0.6, 0.0)):
        u, v = ground_to_pixel(pose, intr, x, y)
        assert pixel_to_ground(pose, intr, u, v) == pytest.approx((x, y), abs=1e-4)


def test_distortion_changes_result():
    pose = cam()
    k = [[500, 0, 320], [0, 500, 240], [0, 0, 1]]
    plain = pixel_to_ground(pose, Intrinsics(k), 50, 400)
    distorted = pixel_to_ground(pose, Intrinsics(k, [-0.3, 0.1, 0, 0, 0]), 50, 400)
    assert np.hypot(plain[0] - distorted[0], plain[1] - distorted[1]) > 0.02


def test_camera_info_without_calibration_is_none():
    class Info:
        k = [0.0] * 9
        d = []
        width = height = 0
    assert Intrinsics.from_camera_info(Info()) is None


def test_camera_info_rescaled_to_image_size():
    class Info:
        k = [1000.0, 0, 640, 0, 1000.0, 480, 0, 0, 1]
        d = [0.0] * 5
        width, height = 1280, 960
    intr = Intrinsics.from_camera_info(Info(), 640, 480)
    assert (intr.fx, intr.cx, intr.cy) == (500.0, 320.0, 240.0)


def test_above_horizon_is_none():
    assert pixel_to_ground(cam(tilt=0.0), Intrinsics.from_fov(640, 480, 1.6), 320, 100) is None


def test_ball_and_goalpost():
    pose = cam()
    intr = Intrinsics.from_fov(640, 480, 1.6)
    u, v = ground_to_pixel(pose, intr, 1.5, 0.0, z=0.07)
    assert ball_ground_point(pose, intr, u, v, 20, 20, 480) == pytest.approx((1.5, 0.0), abs=1e-6)
    u, v = ground_to_pixel(pose, intr, 1.5, 0.0)
    assert footpoint_ground_point(pose, intr, u, v - 50, 100, 480) == pytest.approx((1.5, 0.0), abs=1e-6)
    assert footpoint_ground_point(pose, intr, u, 420, 80, 480, 0.8) is None     # base na faixa inferior


def test_mask_line_points_within_range():
    pose = cam()
    intr = Intrinsics.from_fov(640, 480, 1.6)
    mask = np.zeros((120, 160), np.uint8)
    mask[80:82, :] = 2
    pts = mask_line_points(pose, intr, mask, 640, 480, max_range=3.5)
    assert len(pts) > 0
    assert np.all(np.hypot(pts[:, 0], pts[:, 1]) <= 3.5)
