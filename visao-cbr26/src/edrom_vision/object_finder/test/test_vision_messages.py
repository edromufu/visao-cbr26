"""Mensagens ROS reais: o rclpy valida tipos (ex.: int em campo double levanta AssertionError)."""

import pytest

pytest.importorskip('rclpy')
sv2dm = pytest.importorskip('soccer_vision_2d_msgs.msg')

from std_msgs.msg import Header  # noqa: E402

from object_finder.detections import Detection, YoloClass  # noqa: E402
from object_finder.vision_messages import (  # noqa: E402
    build_detection_messages,
    build_field_boundary_message,
    rotate_message_180,
)


def make_header():
    header = Header()
    header.frame_id = 'camera_optical_frame'
    header.stamp.sec = 12
    return header


def make_detection(yolo_class, cx=100, cy=200, w=40, h=60, score=0.8):
    # ints de propósito: o conversor precisa transformá-los em float
    return Detection(yolo_class, score, cx, cy, w, h)


def test_each_class_goes_to_its_topic_message():
    detections = [
        make_detection(YoloClass.BALL),
        make_detection(YoloClass.GOALPOST),
        make_detection(YoloClass.ROBOT),
        make_detection(YoloClass.L_INTERSECTION),
        make_detection(YoloClass.T_INTERSECTION),
        make_detection(YoloClass.X_INTERSECTION),
        make_detection(YoloClass.CROSSBAR),
    ]
    messages = build_detection_messages(make_header(), detections)

    assert len(messages.balls.balls) == 1
    assert len(messages.goalposts.posts) == 1
    assert len(messages.robots.robots) == 1
    assert [i.num_rays for i in messages.markings.intersections] == [2, 3, 4]
    for array in (messages.balls, messages.goalposts, messages.robots, messages.markings):
        assert array.header.frame_id == 'camera_optical_frame'


def test_ball_geometry_matches_what_the_ipm_reads():
    ball = build_detection_messages(make_header(), [make_detection(YoloClass.BALL)]).balls.balls[0]
    assert (ball.center.x, ball.center.y) == (100.0, 200.0)
    assert (ball.bb.center.position.x, ball.bb.size_y) == (100.0, 60.0)
    assert ball.confidence.confidence == pytest.approx(0.8)


def test_goalpost_and_robot_bounding_boxes():
    messages = build_detection_messages(
        make_header(), [make_detection(YoloClass.GOALPOST), make_detection(YoloClass.ROBOT)])
    for bb in (messages.goalposts.posts[0].bb, messages.robots.robots[0].bb):
        assert (bb.center.position.x, bb.center.position.y) == (100.0, 200.0)
        assert (bb.size_x, bb.size_y) == (40.0, 60.0)


def test_empty_detections_still_produce_valid_empty_messages():
    messages = build_detection_messages(make_header(), [])
    assert messages.balls.balls == [] and messages.markings.intersections == []


def test_field_boundary_is_none_when_empty_and_float_points_otherwise():
    assert build_field_boundary_message(make_header(), []) is None
    message = build_field_boundary_message(make_header(), [(0, 360), (4, 361)])
    assert [(p.x, p.y) for p in message.points] == [(0.0, 360.0), (4.0, 361.0)]


def test_rotate_180_goes_back_to_camera_image():
    messages = build_detection_messages(make_header(), [
        make_detection(YoloClass.BALL, cx=100, cy=200, w=40, h=60),
        make_detection(YoloClass.ROBOT, cx=300, cy=100, w=20, h=80),
        make_detection(YoloClass.T_INTERSECTION, cx=10, cy=20),
    ])
    ball = rotate_message_180(messages.balls, 640, 480).balls[0]
    assert (ball.center.x, ball.center.y) == (540.0, 280.0)
    assert (ball.bb.center.position.x, ball.bb.center.position.y) == (540.0, 280.0)
    assert (ball.bb.size_x, ball.bb.size_y) == (40.0, 60.0)
    robot = rotate_message_180(messages.robots, 640, 480).robots[0]
    assert (robot.bb.center.position.x, robot.bb.center.position.y) == (340.0, 380.0)
    inter = rotate_message_180(messages.markings, 640, 480).intersections[0]
    assert (inter.center.x, inter.center.y) == (630.0, 460.0)

    boundary = rotate_message_180(
        build_field_boundary_message(make_header(), [(0, 100), (640, 120)]), 640, 480)
    assert [(p.x, p.y) for p in boundary.points] == [(0.0, 360.0), (640.0, 380.0)]
