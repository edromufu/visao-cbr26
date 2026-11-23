#!/usr/bin/env python3
"""Nó de visão com o YOEO-26n (OpenVINO): detecção + segmentação de campo e linhas.

Assina:
  /camera/image_raw (sensor_msgs/Image)          do usb_cam (rgb8/bgr8/yuyv)
  /camera/camera_info (sensor_msgs/CameraInfo)   K e distorção, para tirar a distorção da imagem (undistort)
Publica (header = header da imagem):
  balls_in_image (soccer_vision_2d_msgs/BallArray)
  goal_posts_in_image (soccer_vision_2d_msgs/GoalpostArray)
  robots_in_image (soccer_vision_2d_msgs/RobotArray)
  markings_in_image (soccer_vision_2d_msgs/MarkingArray)   cruzamentos L/T/X (num_rays 2/3/4)
  /vision/segmentation (sensor_msgs/Image)       mono8 a 1/4 da entrada da rede, só a área do frame:
                                                 0 fundo, 1 campo, 2 linhas
  vision_debug (sensor_msgs/Image)               bgr8 com caixas e máscara, se debug_image for True

Com undistort=True (padrão) e calibração no camera_info, a imagem é corrigida antes da rede e as
coordenadas publicadas são em pixels sem distorção.
"""
import array
import os

import cv2
import numpy as np
import rclpy
import soccer_vision_2d_msgs.msg as sv2dm
from ament_index_python.packages import get_package_share_directory
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, Image

from .yoeo_infer import YOEOInfer, draw

NUM_RAYS = {'L-Intersection': 2, 'T-Intersection': 3, 'X-Intersection': 4}


def image_msg_to_bgr(msg):
    """sensor_msgs/Image -> BGR só com NumPy (o cv_bridge do Humble não funciona com NumPy 2)."""
    if msg.encoding in ('yuv422_yuy2', 'yuyv'):
        yuyv = np.frombuffer(msg.data, np.uint8).reshape(msg.height, msg.step)[:, :msg.width * 2]
        return cv2.cvtColor(yuyv.reshape(msg.height, msg.width, 2), cv2.COLOR_YUV2BGR_YUYV)
    channels = {'bgr8': 3, 'rgb8': 3, 'bgra8': 4, 'rgba8': 4}[msg.encoding]
    rows = np.frombuffer(msg.data, np.uint8).reshape(msg.height, msg.step)
    pixels = rows[:, :msg.width * channels].reshape(msg.height, msg.width, channels)
    if msg.encoding.startswith('rgb'):
        pixels = pixels[:, :, 2::-1]
    return np.ascontiguousarray(pixels[:, :, :3])


def array_to_image_msg(img, encoding, header):
    msg = Image()
    msg.header = header
    msg.height, msg.width = img.shape[:2]
    msg.encoding = encoding
    msg.step = msg.width * (3 if img.ndim == 3 else 1)
    msg.data = array.array('B', np.ascontiguousarray(img).tobytes())
    return msg


class YOEOVision(Node):

    def __init__(self):
        super().__init__('vision')
        p = self.declare_parameter
        model_path = p('model_path', '').value or os.path.join(
            get_package_share_directory('object_finder'), 'modelo', 'yoeo26n.xml')
        device = p('device', 'CPU').value
        class_conf = {'ball': p('conf_ball', 0.45).value, 'goalpost': p('conf_goalpost', 0.45).value,
                      'robot': p('conf_robot', 0.45).value}
        conf_pt = p('conf_intersection', 0.45).value
        class_conf.update({n: conf_pt for n in NUM_RAYS})
        self.show = p('img_output', False).value
        self.undistort = p('undistort', True).value
        self.net = YOEOInfer(model_path, device=device, threads=p('threads', 0).value, class_conf=class_conf,
                             max_det=30, cache_dir=os.path.expanduser('~/.cache/yoeo_ov'))
        self.get_logger().info(f'YOEO-26n: {model_path} em {device} (entrada {self.net.w}x{self.net.h}), '
                               f'classes {", ".join(self.net.names)}')

        self.pub_ball = self.create_publisher(sv2dm.BallArray, 'balls_in_image', 1)
        self.pub_goal = self.create_publisher(sv2dm.GoalpostArray, 'goal_posts_in_image', 1)
        self.pub_robot = self.create_publisher(sv2dm.RobotArray, 'robots_in_image', 1)
        self.pub_marking = self.create_publisher(sv2dm.MarkingArray, 'markings_in_image', 1)
        self.pub_seg = self.create_publisher(Image, '/vision/segmentation', 2)
        self.pub_debug = self.create_publisher(Image, 'vision_debug', 2) if p('debug_image', False).value else None
        self.latency = []
        self.camera_info = None
        self.maps = None            # (tamanho, map1, map2) do undistort
        self.create_subscription(Image, '/camera/image_raw', self.image_callback, qos_profile_sensor_data)
        if self.undistort:
            self.create_subscription(CameraInfo, '/camera/camera_info', self.camera_info_callback, 1)

    def camera_info_callback(self, msg):
        self.camera_info = msg

    def undistort_maps(self, w, h):
        """Mapas do remap a partir do camera_info; None se não há calibração."""
        info = self.camera_info
        if info is None or info.k[0] <= 0 or not any(info.d):
            return None
        if self.maps is None or self.maps[0] != (w, h):
            k = np.array(info.k, float).reshape(3, 3)
            if info.width and info.height and (info.width, info.height) != (w, h):
                k[0] *= w / info.width
                k[1] *= h / info.height
            d = np.array(info.d, float)
            new_k, _ = cv2.getOptimalNewCameraMatrix(k, d, (w, h), 0, (w, h))
            self.maps = ((w, h), *cv2.initUndistortRectifyMap(k, d, None, new_k, (w, h), cv2.CV_16SC2))
            self.get_logger().info(f'corrigindo a distorção da lente ({w}x{h}) com o camera_info')
        return self.maps[1:]

    def image_callback(self, msg):
        try:
            frame = image_msg_to_bgr(msg)
        except (KeyError, ValueError) as e:
            self.get_logger().error(f'imagem não suportada ({msg.encoding}): {e}', throttle_duration_sec=5)
            return
        try:
            if self.undistort:
                maps = self.undistort_maps(frame.shape[1], frame.shape[0])
                if maps is not None:
                    frame = cv2.remap(frame, *maps, interpolation=cv2.INTER_LINEAR)
            res = self.net(frame)
        except Exception as e:      # noqa: BLE001 - não derrubar o nó por um frame ruim
            self.get_logger().error(f'falha ao processar o frame: {e}', throttle_duration_sec=5)
            return
        self.publish_detections(res, msg.header)
        self.publish_mask(res, msg.header)
        self.latency.append(res.times_ms['total'])
        if len(self.latency) == 300:
            lat = np.array(self.latency)
            self.get_logger().info(f'latência do YOEO (300 frames): p50 {np.percentile(lat, 50):.1f} ms, '
                                   f'p95 {np.percentile(lat, 95):.1f} ms')
            self.latency.clear()
        if self.show or self.pub_debug:
            vis = draw(frame, res, names=self.net.names)
            if self.pub_debug:
                self.pub_debug.publish(array_to_image_msg(vis, 'bgr8', msg.header))
            if self.show:
                cv2.imshow('YOEO', vis)
                cv2.waitKey(1)

    def publish_detections(self, res, header):
        balls = sv2dm.BallArray(header=header)
        posts = sv2dm.GoalpostArray(header=header)
        robots = sv2dm.RobotArray(header=header)
        markings = sv2dm.MarkingArray(header=header)
        for (x0, y0, x1, y1), score, cls in zip(res.boxes, res.scores, res.classes):
            name = self.net.names[int(cls)]
            cx, cy, w, h = (x0 + x1) / 2.0, (y0 + y1) / 2.0, x1 - x0, y1 - y0
            if name == 'ball':
                b = sv2dm.Ball()
                b.center.x, b.center.y = float(cx), float(cy)
                self.fill_bb(b.bb, cx, cy, w, h)
                b.confidence.confidence = float(score)
                balls.balls.append(b)
            elif name == 'goalpost':
                g = sv2dm.Goalpost()
                self.fill_bb(g.bb, cx, cy, w, h)
                g.confidence.confidence = float(score)
                posts.posts.append(g)
            elif name == 'robot':
                r = sv2dm.Robot()
                self.fill_bb(r.bb, cx, cy, w, h)
                r.confidence.confidence = float(score)
                robots.robots.append(r)
            elif name in NUM_RAYS:
                i = sv2dm.MarkingIntersection()
                i.center.x, i.center.y = float(cx), float(cy)
                i.num_rays = NUM_RAYS[name]
                i.confidence.confidence = float(score)
                markings.intersections.append(i)
        self.pub_ball.publish(balls)
        self.pub_goal.publish(posts)
        self.pub_robot.publish(robots)
        self.pub_marking.publish(markings)

    @staticmethod
    def fill_bb(bb, cx, cy, w, h):
        bb.center.position.x, bb.center.position.y = float(cx), float(cy)
        bb.size_x, bb.size_y = float(w), float(h)

    def publish_mask(self, res, header):
        valid = res.mask != 255
        rows, cols = np.where(valid.any(1))[0], np.where(valid.any(0))[0]
        if len(rows) and len(cols):
            mask = res.mask[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1]
            self.pub_seg.publish(array_to_image_msg(mask, 'mono8', header))


def main(args=None):
    rclpy.init(args=args)
    node = YOEOVision()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
