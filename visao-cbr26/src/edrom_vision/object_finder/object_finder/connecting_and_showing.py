#!/usr/bin/env python3
"""
Nó ROS 2 ``vision`` (executável ``finder``): YOLO + estrutura de linhas.

Lê a imagem do ``usb_cam`` (``/camera/image_raw``, remapeável por
``image_topic``), chama ``LineVisionPipeline.process`` e publica nos tópicos
do ``object_finder`` (todos parametrizáveis em ``topics.*``):

* ``balls_in_image``, ``goal_posts_in_image``, ``robots_in_image``
  (``soccer_vision_2d_msgs``);
* ``markings_in_image`` (``MarkingArray``: ``intersections`` **com
  heading_rays**, ``segments`` e ``ellipses``);
* ``field_boundary_in_image`` (``FieldBoundary``);
* ``processed_image_topic`` (overlay, ``sensor_msgs/Image`` bgr8);
* opcional (``publish_projection``): ``line_vision/markings_relative``
  (``soccer_vision_3d_msgs/MarkingArray``), projeção ao chão própria
  (tópico distinto do ``markings_relative`` de um IPM futuro).
"""

from __future__ import annotations

from pathlib import Path
import time
from typing import Any

import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image
import soccer_vision_2d_msgs.msg as sv2d
import soccer_vision_attribute_msgs.msg as attr
import vision_msgs.msg as vm

from . import msg_conversion as mc
from .calibration.ros_image import image_msg_to_bgr
from .detector import make_detector
from .overlay import render_result as render
from .params import default_params_file, load_params
from .pipeline import LineVisionPipeline

try:  # QoS de sensor (como no object_finder); os testes usam um rclpy falso
    from rclpy.qos import qos_profile_sensor_data as QOS_CAMERA
except ImportError:  # pragma: no cover
    QOS_CAMERA = 1


def _share_dir() -> Path:
    try:
        from ament_index_python.packages import get_package_share_directory
        return Path(get_package_share_directory('object_finder'))
    except Exception:  # noqa: BLE001 - fora do ament (testes)
        return Path(__file__).resolve().parents[1]


class LineVisionNode(Node):
    """Nó de visão por estrutura de linhas + YOLO."""

    def __init__(self, name: str = 'vision') -> None:
        super().__init__(name)
        share = _share_dir()
        P = self.declare_parameter
        self.img_output = bool(P('vision.img_output', False).value)
        self.processing_fps = float(P('vision.processing_fps', 0.0).value)  # 0 = todos os frames
        # calibração de cor: config/ (reescrita a cada calibração); calib_dir troca a pasta
        calib_dir = str(P('calib_dir', '').value) or str(share / 'config')
        model_path = str(P('model_path', '').value) or str(share / 'modelo' / 'best.pt')
        use_yolo = bool(P('use_yolo', True).value)
        params_file = str(P('params_file', '').value) or str(default_params_file() or '')
        self.image_topic = str(P('image_topic', '/camera/image_raw').value)
        self.camera_info_topic = str(P('camera_info_topic', '/camera/camera_info').value)
        t = {k: str(P(f'topics.{k}', v).value) for k, v in {
            'balls': 'balls_in_image', 'goalposts': 'goal_posts_in_image', 'robots': 'robots_in_image',
            'markings': 'markings_in_image', 'field_boundary': 'field_boundary_in_image',
            'debug_image': 'processed_image_topic', 'projection': 'line_vision/markings_relative'}.items()}
        self.publish_projection = bool(P('publish_projection', False).value)
        self.projection_frame = str(P('projection_frame', 'base_footprint').value)
        self.camera_height = float(P('camera.altura_m', 0.70).value)
        self.camera_pitch = float(P('camera.pitch_rad', 0.0).value)
        self.publish_debug = bool(P('publish_debug_image', True).value)

        params = load_params(params_file or None)
        detector = None
        if use_yolo and Path(model_path).is_file():
            p = params.detector
            detector = make_detector(model_path, imgsz=p.imgsz,
                                     conf=p.conf, iou=p.iou, max_det=p.max_det)
        elif use_yolo:
            self.get_logger().warn(f'modelo nao encontrado ({model_path}): rodando sem YOLO')
        green = Path(calib_dir) / 'green_pixels.csv'
        white = Path(calib_dir) / 'white_pixels.csv'
        self.pipeline = LineVisionPipeline(params, str(green), str(white), detector)
        self.get_logger().info(
            f'calibracao: {calib_dir} | modelo: {model_path if detector else "sem YOLO"}')

        self.pub = {
            'balls': self.create_publisher(sv2d.BallArray, t['balls'], 1),
            'goalposts': self.create_publisher(sv2d.GoalpostArray, t['goalposts'], 1),
            'robots': self.create_publisher(sv2d.RobotArray, t['robots'], 1),
            'markings': self.create_publisher(sv2d.MarkingArray, t['markings'], 1),
            'field_boundary': self.create_publisher(sv2d.FieldBoundary, t['field_boundary'], 1),
            'debug_image': self.create_publisher(Image, t['debug_image'], 1),
        }
        if self.publish_projection:
            import geometry_msgs.msg as geo
            import soccer_vision_3d_msgs.msg as sv3d
            self._sv3d, self._geo = sv3d, geo
            self.pub['projection'] = self.create_publisher(sv3d.MarkingArray, t['projection'], 10)
        self.create_subscription(CameraInfo, self.camera_info_topic, self._on_camera_info, 1)
        self.create_subscription(Image, self.image_topic, self._on_image, QOS_CAMERA)
        self.get_logger().info(f'>> assinando {self.image_topic}')
        self._fps = 0.0
        self._last = time.perf_counter()

    # ------------------------------------------------------------ entradas
    def _on_camera_info(self, info: Any) -> None:
        if self.pipeline.camera is None or self.pipeline.camera.nome == 'camera_info':
            self.pipeline.camera = mc.camera_info_to_model(
                info, self.camera_height, self.camera_pitch)
            self.pipeline._camera_auto = False

    def _on_image(self, msg: Any) -> None:
        if self.processing_fps > 0 and time.perf_counter() - self._last < 1.0 / self.processing_fps:
            return  # limita a taxa de processamento
        try:
            frame = image_msg_to_bgr(msg)
        except ValueError as exc:
            self.get_logger().error(str(exc))
            return
        self.process(frame, msg.header)

    # -------------------------------------------------------- processamento
    def process(self, frame: np.ndarray, header: Any) -> None:
        """Roda o núcleo e publica tudo."""
        r = self.pipeline.process(frame)
        now = time.perf_counter()
        self._fps = 0.9 * self._fps + 0.1 / \
            max(1e-6, now - self._last) if self._fps else 1.0 / max(1e-6, now - self._last)
        self._last = now

        for k, msg in mc.detections_to_msgs(r.detections, header, sv2d, vm, attr).items():
            self.pub[k].publish(msg)
        self.pub['markings'].publish(mc.markings_to_msg(
            r.crossings, r.lines, r.ellipses, header, sv2d, vm, attr))
        if r.stage1.field_detected:  # fronteira vazia derruba o IPM (soccer_ipm)
            self.pub['field_boundary'].publish(mc.field_boundary_to_msg(
                r.stage1.boundary_image_points(), r.stage1.field_detected, header, sv2d, vm, attr))
        if self.publish_projection:
            h3 = type(header)(stamp=header.stamp, frame_id=self.projection_frame)
            self.pub['projection'].publish(mc.projection_to_msg(
                r.crossings, r.lines, self.pipeline.camera, h3, self._sv3d, self._geo, attr))
        if self.publish_debug or self.img_output:
            img = render(frame, r, self._fps)
            if self.publish_debug:
                import sensor_msgs.msg as sm
                self.pub['debug_image'].publish(mc.bgr_to_image_msg(img, header, sm))
            if self.img_output:  # pragma: no cover - precisa de tela
                cv2.imshow('inference_frame', img)
                cv2.waitKey(1)
        self.last_result = r


def main(args: Any = None) -> None:  # pragma: no cover - precisa de ROS
    """Ponto de entrada do ``ros2 run object_finder finder``."""
    rclpy.init(args=args)
    node = LineVisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('encerrado (Ctrl+C)')
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':  # pragma: no cover
    main()
