#!/usr/bin/env python3
"""
Nó ROS 2 (Humble) ``line_vision_node``: casca fina sobre o núcleo.

Nenhuma lógica de visão aqui: o nó lê a imagem (tópico na simulação ou
câmera por índice no robô real), chama ``LineVisionPipeline.process`` e
publica nos mesmos tópicos do nó finder (todos remapeáveis/parametrizáveis):

* ``balls_in_image``, ``goal_posts_in_image``, ``robots_in_image``
  (``soccer_vision_2d_msgs``);
* ``markings_in_image`` (``MarkingArray``: ``intersections`` **com
  heading_rays**, ``segments`` e ``ellipses``);
* ``field_boundary_in_image`` (``FieldBoundary``);
* ``processed_image_topic`` (overlay, ``sensor_msgs/Image`` bgr8);
* opcional: ``vision/landmarks`` (``edrom_msgs/LandmarkArray``).

NÃO TESTADO com ROS real nesta sessão; testado com ``rclpy`` simulado
(``test/test_ros_node_mock.py``).
"""

from __future__ import annotations

from pathlib import Path
import threading
import time
from typing import Any, Optional

import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image
import soccer_vision_2d_msgs.msg as sv2d
import soccer_vision_attribute_msgs.msg as attr
from std_msgs.msg import Header
import vision_msgs.msg as vm

from . import msg_conversion as mc
from ..calibration.ros_image import image_msg_to_bgr
from ..detector import make_detector
from ..overlay import render_result as render
from ..params import default_params_file, load_params
from ..pipeline import LineVisionPipeline


def _share_dir() -> Path:
    try:
        from ament_index_python.packages import get_package_share_directory
        return Path(get_package_share_directory('robocup_line_vision'))
    except Exception:  # noqa: BLE001 - fora do ament (testes)
        return Path(__file__).resolve().parents[2]


class LineVisionNode(Node):
    """Nó de visão por estrutura de linhas + YOLO."""

    def __init__(self, name: str = 'line_vision_node') -> None:
        super().__init__(name)
        share = _share_dir()
        P = self.declare_parameter
        self.use_simulation = bool(P('use_simulation', True).value)
        self.img_output = bool(P('vision.img_output', False).value)
        self.camera_idx = int(P('vision.camera_idx', 0).value)
        self.cam_w = int(P('vision.largura', 0).value)
        self.cam_h = int(P('vision.altura', 0).value)
        self.processing_fps = float(P('vision.processing_fps', 30.0).value)
        calib_dir = str(P('calib_dir', '').value) or str(share / 'calib' / 'padrao_webots')
        model_path = str(P('model_path', '').value) or str(share / 'modelo' / 'best.pt')
        use_yolo = bool(P('use_yolo', True).value)
        params_file = str(P('params_file', '').value) or str(default_params_file() or '')
        self.image_topic = str(P('image_topic', '/AUREA/camera_optical_frame/image_color').value)
        self.camera_info_topic = str(
            P('camera_info_topic', '/AUREA/camera_optical_frame/camera_info').value)
        self.frame_id = str(P('frame_id', 'camera_optical_frame').value)
        t = {k: str(P(f'topics.{k}', v).value) for k, v in {
            'balls': 'balls_in_image', 'goalposts': 'goal_posts_in_image', 'robots': 'robots_in_image',
            'markings': 'markings_in_image', 'field_boundary': 'field_boundary_in_image',
            'debug_image': 'processed_image_topic', 'landmarks': 'vision/landmarks'}.items()}
        self.publish_landmarks = bool(P('publish_landmarks', False).value)
        self.landmark_ids = mc.parse_id_map(str(P('landmark_ids', 'L:4,T:5,X:6').value))
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
        if self.publish_landmarks:
            from edrom_msgs.msg import Landmark, LandmarkArray
            self._Landmark, self._LandmarkArray = Landmark, LandmarkArray
            self.pub['landmarks'] = self.create_publisher(LandmarkArray, t['landmarks'], 10)
        self.create_subscription(CameraInfo, self.camera_info_topic, self._on_camera_info, 1)
        self._lock = threading.Lock()
        self._frame: Optional[np.ndarray] = None
        self._fps = 0.0
        self._last = time.perf_counter()
        if self.use_simulation:
            self.create_subscription(Image, self.image_topic, self._on_image, 1)
            self.get_logger().info(f'>> SIMULACAO: assinando {self.image_topic}')
        else:
            self._start_camera()
            self.create_timer(1.0 / max(1.0, self.processing_fps), self._on_timer)

    # ------------------------------------------------------------ entradas
    def _on_camera_info(self, info: Any) -> None:
        if self.pipeline.camera is None or self.pipeline.camera.nome == 'camera_info':
            self.pipeline.camera = mc.camera_info_to_model(
                info, self.camera_height, self.camera_pitch)
            self.pipeline._camera_auto = False

    def _on_image(self, msg: Any) -> None:
        try:
            frame = image_msg_to_bgr(msg)
        except ValueError as exc:
            self.get_logger().error(str(exc))
            return
        self.process(frame, msg.header)

    def _start_camera(self) -> None:  # pragma: no cover - precisa de câmera
        self.cap = cv2.VideoCapture(self.camera_idx)
        if self.cam_w:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_w)
        if self.cam_h:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_h)
        if not self.cap.isOpened():
            self.get_logger().error(f'nao abriu a camera {self.camera_idx}')
            return
        threading.Thread(target=self._capture_loop, daemon=True).start()
        self.get_logger().info(f'>> ROBO REAL: camera {self.camera_idx}')

    def _capture_loop(self) -> None:  # pragma: no cover
        while rclpy.ok():
            ok, fr = self.cap.read()
            if ok:
                with self._lock:
                    self._frame = fr

    def _on_timer(self) -> None:  # pragma: no cover
        with self._lock:
            fr = None if self._frame is None else self._frame.copy()
        if fr is not None:
            h = Header()
            h.stamp = self.get_clock().now().to_msg()
            h.frame_id = self.frame_id
            self.process(fr, h)

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
        self.pub['field_boundary'].publish(mc.field_boundary_to_msg(
            r.stage1.boundary_image_points(), r.stage1.field_detected, header, sv2d, vm, attr))
        if self.publish_landmarks:
            arr = self._LandmarkArray()
            arr.header = header
            for d in mc.landmarks_from_crossings(r.crossings, self.landmark_ids):
                lm = self._Landmark()
                lm.id, lm.distance_m, lm.angle_rad = d['id'], d['distance_m'], d['angle_rad']
                arr.landmarks.append(lm)
            self.pub['landmarks'].publish(arr)
        if self.publish_debug or self.img_output:
            img = render(frame, r, self._fps)
            if self.publish_debug:
                self.pub['debug_image'].publish(mc.bgr_to_image_msg(img, header, Image_mod()))
            if self.img_output:  # pragma: no cover - precisa de tela
                cv2.imshow('robocup_line_vision', img)
                cv2.waitKey(1)
        self.last_result = r


def Image_mod() -> Any:
    """Módulo com a classe ``Image`` (para o conversor)."""
    import sensor_msgs.msg as m
    return m


def main(args: Any = None) -> None:  # pragma: no cover - precisa de ROS
    """Ponto de entrada do ``ros2 run robocup_line_vision line_vision_node``."""
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
