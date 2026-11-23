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
    Node.overrides = {'use_yolo': False, 'publish_projection': True}
    mod = importlib.import_module('object_finder.connecting_and_showing')
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
            'field_boundary_in_image', 'processed_image_topic', 'line_vision/markings_relative'} <= set(n.publishers)
    assert '/camera/image_raw' in n.subscriptions and '/camera/camera_info' in n.subscriptions


def test_publica_marcacoes_com_heading_rays(node_mod):
    mod, _ = node_mod
    import sensor_msgs.msg as sm
    import std_msgs.msg as std
    n = mod.LineVisionNode()
    # camera_info da simulação (AUREA: 1080x720, fov 0.785)
    info = sm.CameraInfo()
    f = 540 / math.tan(0.785 / 2)
    info.k = [f, 0, 540, 0, f, 360, 0, 0, 1]
    n.subscriptions['/camera/camera_info'][1](info)
    img = cv2.imread(str(DATA / 'frame_webots.png'))
    h = std.Header(frame_id='camera_optical_frame')
    n.subscriptions['/camera/image_raw'][1](_image_msg(img, sm, h))
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
    m3 = n.publishers['line_vision/markings_relative'].msgs[-1]
    assert m3.header.frame_id == 'base_footprint'
    r = n.last_result
    proj = [c for c in r.crossings if c.distancia_m is not None]
    assert proj and len(m3.intersections) == len(proj)
    for it, c in zip(m3.intersections, proj):
        assert it.num_rays in (2, 3, 4)
        assert math.isclose(math.hypot(it.center.x, it.center.y), c.distancia_m, rel_tol=1e-6)
        assert it.center.x > 0                      # à frente do robô
        assert len(it.rays) in (0, len(c.heading_rays))
        for v in it.rays:
            assert math.isclose(math.hypot(v.x, v.y), 1.0, rel_tol=1e-6)
    assert len(m3.segments) >= 1
    for s in m3.segments:
        assert s.start.x > 0 and s.end.x > 0


def test_mensagens_de_deteccao_por_nome():
    ros_fakes.install()
    try:
        import soccer_vision_2d_msgs.msg as sv
        import soccer_vision_attribute_msgs.msg as attr
        import std_msgs.msg as std
        import vision_msgs.msg as vm

        from object_finder.features import Detection
        from object_finder import msg_conversion as mc
        dets = [Detection('ball', 99, 0.9, 10, 20, 5, 5), Detection('goalpost', 0, 0.8, 50, 60, 10, 40),
                Detection('robot', 1, 0.7, 5, 5, 3, 3, rejeitada=True, motivo='outside_field')]
        out = mc.detections_to_msgs(dets, std.Header(), sv, vm, attr)
        assert len(out['balls'].balls) == 1 and out['balls'].balls[0].center.x == 10
        assert len(out['goalposts'].posts) == 1 and out['goalposts'].posts[0].bb.size_y == 40
        assert out['robots'].robots == []
        img = mc.bgr_to_image_msg(np.zeros((2, 3, 3), np.uint8),
                                  std.Header(), __import__('sensor_msgs.msg').msg)
        assert img.step == 9 and len(img.data) == 18
    finally:
        ros_fakes.uninstall()


def _run_node(mod, Node, img, rotate):
    import sensor_msgs.msg as sm
    import std_msgs.msg as std
    Node.overrides = {'use_yolo': False, 'publish_projection': True, 'rotate_180': rotate}
    n = mod.LineVisionNode()
    info = sm.CameraInfo()
    f = 540 / math.tan(0.785 / 2)
    info.k = [f, 0, 539.5, 0, f, 359.5, 0, 0, 1]   # centro exato: igual na imagem girada
    info.width, info.height = 1080, 720
    n.subscriptions['/camera/camera_info'][1](info)
    n.subscriptions['/camera/image_raw'][1](_image_msg(img, sm, std.Header(frame_id='camera_optical_frame')))
    return n


def test_rotate_180_publica_na_imagem_original(node_mod):
    """Câmera de cabeça para baixo + rotate_180 = câmera em pé, com os pixels espelhados."""
    mod, Node = node_mod
    upright = cv2.imread(str(DATA / 'frame_webots.png'))
    a = _run_node(mod, Node, upright, False)
    b = _run_node(mod, Node, cv2.rotate(upright, cv2.ROTATE_180), True)
    w, h = 1080, 720
    ma, mb = a.publishers['markings_in_image'].msgs[-1], b.publishers['markings_in_image'].msgs[-1]
    assert len(ma.segments) >= 2 and len(ma.segments) == len(mb.segments)
    for sa, sb in zip(ma.segments, mb.segments):
        assert (w - sb.start.x, h - sb.start.y) == pytest.approx((sa.start.x, sa.start.y))
        assert (w - sb.end.x, h - sb.end.y) == pytest.approx((sa.end.x, sa.end.y))
    assert len(ma.intersections) == len(mb.intersections)
    for ia, ib in zip(ma.intersections, mb.intersections):
        assert (w - ib.center.x, h - ib.center.y) == pytest.approx((ia.center.x, ia.center.y))
        for ra, rb in zip(ia.heading_rays, ib.heading_rays):
            assert math.cos(ra) == pytest.approx(-math.cos(rb), abs=1e-9)
            assert math.sin(ra) == pytest.approx(-math.sin(rb), abs=1e-9)
    fa, fb = a.publishers['field_boundary_in_image'].msgs[-1], b.publishers['field_boundary_in_image'].msgs[-1]
    assert [(w - p.x, h - p.y) for p in fb.points][::-1] == pytest.approx([(p.x, p.y) for p in fa.points])
    # a projeção ao chão não depende da rotação
    pa = a.publishers['line_vision/markings_relative'].msgs[-1]
    pb = b.publishers['line_vision/markings_relative'].msgs[-1]
    assert [(s.start.x, s.start.y) for s in pb.segments] == pytest.approx([(s.start.x, s.start.y) for s in pa.segments])
    assert b.publishers['processed_image_topic'].msgs[-1].height == 720
