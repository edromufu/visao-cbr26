"""Nó ROS com rclpy e mensagens simuladas (sem ROS instalado)."""

import importlib
import math
from pathlib import Path

import cv2
import numpy as np
import pytest

import ros_fakes

DATA = Path(__file__).parent / 'data'


@pytest.fixture()
def node_mod():
    rclpy, Node = ros_fakes.install()
    Node.overrides = {'use_yolo': False, 'publish_landmarks': True, 'landmark_ids': 'L:4,T:5,X:6'}
    mod = importlib.import_module('robocup_line_vision.ros.line_vision_node')
    yield mod, Node
    Node.overrides = {}
    ros_fakes.uninstall()


def _image_msg(img, sm, header):
    m = sm.Image()
    m.header = header
    m.height, m.width = img.shape[:2]
    m.encoding = 'bgr8'
    m.step = img.shape[1] * 3
    m.data = img.tobytes()
    return m


def test_topicos_iguais_aos_do_finder(node_mod):
    mod, _ = node_mod
    n = mod.LineVisionNode()
    assert {'balls_in_image', 'goal_posts_in_image', 'robots_in_image', 'markings_in_image',
            'field_boundary_in_image', 'processed_image_topic', 'vision/landmarks'} <= set(n.publishers)
    assert '/AUREA/camera_optical_frame/image_color' in n.subscriptions


def test_publica_marcacoes_com_heading_rays(node_mod):
    mod, _ = node_mod
    import sensor_msgs.msg as sm
    import std_msgs.msg as std
    n = mod.LineVisionNode()
    # camera_info da simulação (AUREA: 1080x720, fov 0.785)
    info = sm.CameraInfo()
    f = 540 / math.tan(0.785 / 2)
    info.k = [f, 0, 540, 0, f, 360, 0, 0, 1]
    n.subscriptions['/AUREA/camera_optical_frame/camera_info'][1](info)
    img = cv2.imread(str(DATA / 'frame_webots.png'))
    h = std.Header(frame_id='camera_optical_frame')
    n.subscriptions['/AUREA/camera_optical_frame/image_color'][1](_image_msg(img, sm, h))
    m = n.publishers['markings_in_image'].msgs[-1]
    assert m.header is h
    assert len(m.segments) >= 2
    for it in m.intersections:
        assert it.num_rays in (2, 3, 4)
        assert list(it.heading_rays) == sorted(it.heading_rays)
        assert len(it.heading_rays) in (0, it.num_rays)
    fb = n.publishers['field_boundary_in_image'].msgs[-1]
    assert len(fb.points) > 10 and fb.confidence.confidence == 1.0
    dbg = n.publishers['processed_image_topic'].msgs[-1]
    assert dbg.encoding == 'bgr8' and dbg.height == 720 and len(dbg.data) == 720 * 1080 * 3
    lms = n.publishers['vision/landmarks'].msgs[-1]
    r = n.last_result
    proj = [c for c in r.crossings if c.distancia_m is not None]
    assert len(lms.landmarks) == len([c for c in proj if c.tipo in 'LTX'])
    for lm in lms.landmarks:
        assert lm.id in (4, 5, 6) and lm.distance_m > 0


def test_mensagens_de_deteccao_por_nome():
    ros_fakes.install()
    try:
        import soccer_vision_2d_msgs.msg as sv
        import soccer_vision_attribute_msgs.msg as attr
        import std_msgs.msg as std
        import vision_msgs.msg as vm

        from robocup_line_vision.features import Detection
        from robocup_line_vision.ros import msg_conversion as mc
        dets = [Detection('ball', 99, 0.9, 10, 20, 5, 5), Detection('goalpost', 0, 0.8, 50, 60, 10, 40),
                Detection('robot', 1, 0.7, 5, 5, 3, 3, rejeitada=True, motivo='outside_field')]
        out = mc.detections_to_msgs(dets, std.Header(), sv, vm, attr)
        assert len(out['balls'].balls) == 1 and out['balls'].balls[0].center.x == 10
        assert len(out['goalposts'].posts) == 1 and out['goalposts'].posts[0].bb.size_y == 40
        assert out['robots'].robots == []
        assert mc.parse_id_map('L:4, T:5,X:6') == {'L': 4, 'T': 5, 'X': 6}
        img = mc.bgr_to_image_msg(np.zeros((2, 3, 3), np.uint8),
                                  std.Header(), __import__('sensor_msgs.msg').msg)
        assert img.step == 9 and len(img.data) == 18
    finally:
        ros_fakes.uninstall()
