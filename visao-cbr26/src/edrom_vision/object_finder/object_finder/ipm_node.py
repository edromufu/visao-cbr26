#!/usr/bin/env python3
"""IPM das detecções do YOEO, com a pose da câmera por medidas fixas ou pela cadeia cinemática.

Mesmas entradas e saídas do soccer_ipm, sem precisar de TF: a pose da câmera é calculada aqui.
  fixed       sem URDF: altura do eixo do tilt, inclinação do corpo e offset da lente medidos no robô.
  kinematics  URDF do robô (urdf_path) + todos os ângulos de /joint_states.

Assina:
  balls_in_image, goal_posts_in_image, robots_in_image, markings_in_image (soccer_vision_2d_msgs)
  /vision/segmentation (sensor_msgs/Image)      máscara mono8 do YOEO (2 = linhas)
  camera_info (sensor_msgs/CameraInfo)          K e distorção; sem calibração (K zerada) usa camera.fov
  /joint_states (sensor_msgs/JointState)        pan/tilt (modo fixed) ou todas as juntas (modo kinematics)

Publica (frame base_footprint, stamp do frame da câmera):
  balls_relative, goal_posts_relative, robots_relative, markings_relative (soccer_vision_3d_msgs)
  ipm/line_points (sensor_msgs/PointCloud2)     pontos de linha no chão
  ipm/markers (visualization_msgs/MarkerArray)  para o RViz
  ipm/birdseye (sensor_msgs/Image)              vista de cima, bgr8
  TF base_footprint -> frame da câmera (convenção óptica, z para frente) e, no modo kinematics,
     base_footprint -> link do torso
"""
import array
import bisect
import math

import cv2
import numpy as np
import rclpy
import soccer_vision_2d_msgs.msg as sv2dm
import soccer_vision_3d_msgs.msg as sv3dm
from geometry_msgs.msg import Point, TransformStamped
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image, JointState, PointCloud2, PointField
from tf2_ros import TransformBroadcaster
from visualization_msgs.msg import Marker, MarkerArray

from .birdseye import BirdsEye
from .kinematics import CameraKinematics, RobotModel, fixed_pose
from .projection import (BALL_RADIUS, Intrinsics, ball_ground_point, footpoint_ground_point, mask_line_points,
                         pixel_to_ground)

JOINT_HISTORY_S = 1.0
MAX_JOINT_GAP_S = 0.25
OBJECT_TTL_S = 0.5
RAYS_LABEL = {2: 'L', 3: 'T', 4: 'X'}
# câmera (x frente, y esquerda, z cima) -> óptico (x direita, y baixo, z frente)
CAMERA_TO_OPTICAL = np.array([[0.0, 0.0, 1.0, 0.0], [-1.0, 0.0, 0.0, 0.0], [0.0, -1.0, 0.0, 0.0],
                              [0.0, 0.0, 0.0, 1.0]])


def stamp_s(stamp):
    return stamp.sec + stamp.nanosec * 1e-9


def matrix_to_quaternion(r):
    w = math.sqrt(max(0.0, 1.0 + r[0, 0] + r[1, 1] + r[2, 2])) / 2.0
    x = math.copysign(math.sqrt(max(0.0, 1.0 + r[0, 0] - r[1, 1] - r[2, 2])) / 2.0, r[2, 1] - r[1, 2])
    y = math.copysign(math.sqrt(max(0.0, 1.0 - r[0, 0] + r[1, 1] - r[2, 2])) / 2.0, r[0, 2] - r[2, 0])
    z = math.copysign(math.sqrt(max(0.0, 1.0 - r[0, 0] - r[1, 1] + r[2, 2])) / 2.0, r[1, 0] - r[0, 1])
    return x, y, z, w


class IPMNode(Node):

    def __init__(self):
        super().__init__('yoeo_ipm')
        p = self.declare_parameter
        self.mode = p('pose_source', 'fixed').value
        if self.mode not in ('fixed', 'kinematics'):
            raise ValueError("pose_source deve ser 'fixed' ou 'kinematics'")
        self.camera_offset = tuple(p('camera.offset', [0.0, 0.0, 0.0]).value)
        self.fov = p('camera.fov', 1.6).value
        self.default_size = (p('camera.width', 640).value, p('camera.height', 480).value)
        # modo fixed
        self.tilt_axis_height = p('fixed.tilt_axis_height', 0.49).value
        self.body_pitch = p('fixed.body_pitch', 0.0).value
        self.head_from_joints = p('head.from_joint_states', True).value
        self.pan_joint = p('head.pan_joint', 'head_pan').value
        self.tilt_joint = p('head.tilt_joint', 'head_tilt').value
        self.default_head = {self.pan_joint: p('head.pan', 0.0).value, self.tilt_joint: p('head.tilt', 0.0).value}
        # modo kinematics
        urdf = p('urdf_path', '').value
        torso_link = p('kinematics.torso_link', 'base_link').value
        camera_link = p('kinematics.camera_link', '').value
        foot_links = {'left': p('kinematics.left_foot_link', '').value,
                      'right': p('kinematics.right_foot_link', '').value}
        sole_offset = {'left': tuple(p('kinematics.sole_offset_left', [0.0, 0.0, 0.0]).value),
                       'right': tuple(p('kinematics.sole_offset_right', [0.0, 0.0, 0.0]).value)}
        self.support_mode = p('kinematics.support_foot', 'auto').value
        self.kin = None
        if self.mode == 'kinematics':
            if not urdf or not camera_link or not all(foot_links.values()):
                raise ValueError('modo kinematics precisa de urdf_path, kinematics.camera_link, '
                                 'kinematics.left_foot_link e kinematics.right_foot_link')
            self.kin = CameraKinematics(RobotModel(urdf), torso_link, camera_link, foot_links,
                                        self.camera_offset, sole_offset)
        self.post_threshold = p('goalposts.footpoint_out_of_image_threshold', 0.8).value
        self.robot_threshold = p('robots.footpoint_out_of_image_threshold', 0.8).value
        self.line_max_range = p('lines.max_range', 3.5).value
        self.line_max_points = p('lines.max_points', 80).value
        self.frame = p('output_frame', 'base_footprint').value
        self.show = p('debug.show', False).value
        self.birdseye = BirdsEye(max_x=p('debug.range', 4.0).value, scale=p('debug.scale', 100).value)

        self.joint_times, self.joint_states = [], []
        self.camera_info = None
        self.intr = None
        self.intr_key = None
        self.objects = {}           # tipo -> (instante, [(rótulo, (x, y))])
        self.lines = (0.0, np.empty((0, 2)))
        self.last_pose = None
        self.last_tf_stamp = None   # os 5 callbacks de um frame têm o mesmo stamp: TF uma vez só

        self.pub_ball = self.create_publisher(sv3dm.BallArray, 'balls_relative', 1)
        self.pub_goal = self.create_publisher(sv3dm.GoalpostArray, 'goal_posts_relative', 1)
        self.pub_robot = self.create_publisher(sv3dm.RobotArray, 'robots_relative', 1)
        self.pub_marking = self.create_publisher(sv3dm.MarkingArray, 'markings_relative', 1)
        self.pub_lines = self.create_publisher(PointCloud2, 'ipm/line_points', 5)
        self.pub_markers = self.create_publisher(MarkerArray, 'ipm/markers', 5)
        self.pub_birdseye = self.create_publisher(Image, 'ipm/birdseye', 2)
        self.tf = TransformBroadcaster(self)

        self.create_subscription(CameraInfo, 'camera_info', self.camera_info_callback, 1)
        self.create_subscription(sv2dm.BallArray, 'balls_in_image', self.balls_callback, 1)
        self.create_subscription(sv2dm.GoalpostArray, 'goal_posts_in_image', self.goalposts_callback, 1)
        self.create_subscription(sv2dm.RobotArray, 'robots_in_image', self.robots_callback, 1)
        self.create_subscription(sv2dm.MarkingArray, 'markings_in_image', self.markings_callback, 1)
        self.create_subscription(Image, '/vision/segmentation', self.segmentation_callback, 2)
        if self.head_from_joints or self.mode == 'kinematics':
            self.create_subscription(JointState, '/joint_states', self.joints_callback, 50)
        self.create_timer(0.1, self.draw)
        self.get_logger().info(f'IPM no modo {self.mode}' + (f' ({urdf})' if self.kin else ''))

    # ---------------- câmera ----------------
    def camera_info_callback(self, msg):
        self.camera_info = msg

    def image_size(self):
        info = self.camera_info
        if info is not None and info.width and info.height:
            return info.width, info.height
        return self.default_size

    def intrinsics(self):
        size = self.image_size()
        calibrated = self.camera_info is not None and self.camera_info.k[0] > 0
        key = (size, calibrated)
        if key != self.intr_key:
            self.intr_key = key
            self.intr = Intrinsics.from_camera_info(self.camera_info, *size) if calibrated else None
            if self.intr is None:
                self.intr = Intrinsics.from_fov(*size, self.fov)
                self.get_logger().warn(f'camera_info sem calibração: pinhole pelo FOV {self.fov:.3f} rad, '
                                       f'{size[0]}x{size[1]}, f={self.intr.fx:.1f} px')
            else:
                self.get_logger().info(f'intrínseca do camera_info: fx={self.intr.fx:.1f} fy={self.intr.fy:.1f} '
                                       f'cx={self.intr.cx:.1f} cy={self.intr.cy:.1f} '
                                       f'distorção={"sim" if self.intr.d is not None else "não"}')
        return self.intr

    # ---------------- pose da câmera ----------------
    def joints_callback(self, msg):
        t = stamp_s(msg.header.stamp)
        state = dict(self.joint_states[-1]) if self.joint_states else {}
        state.update(zip(msg.name, msg.position))
        if self.joint_times and t < self.joint_times[-1]:     # relógio voltou (simulação reiniciada)
            self.joint_times.clear()
            self.joint_states.clear()
        self.joint_times.append(t)
        self.joint_states.append(state)
        while self.joint_times and self.joint_times[0] < t - JOINT_HISTORY_S:
            self.joint_times.pop(0)
            self.joint_states.pop(0)

    def joints_at(self, t):
        """Juntas mais próximas do instante do frame; as mais recentes se o relógio não bate."""
        joints = dict(self.default_head)
        if not self.joint_states:
            return joints
        i = bisect.bisect_left(self.joint_times, t)
        best = min((j for j in (i - 1, i) if 0 <= j < len(self.joint_times)),
                   key=lambda j: abs(self.joint_times[j] - t))
        if abs(self.joint_times[best] - t) > MAX_JOINT_GAP_S:
            best = len(self.joint_states) - 1
        state = self.joint_states[best]
        if self.mode == 'kinematics':
            joints.update(state)
        elif self.head_from_joints:
            joints.update({k: state[k] for k in (self.pan_joint, self.tilt_joint) if k in state})
        return joints

    def camera_pose(self, header):
        joints = self.joints_at(stamp_s(header.stamp))
        if self.mode == 'kinematics':
            pose = self.kin.pose(joints, self.support_mode)
        else:
            pose = fixed_pose(self.tilt_axis_height, self.body_pitch, joints[self.pan_joint],
                              joints[self.tilt_joint], self.camera_offset)
        self.last_pose = pose
        self.publish_tf(pose, header)
        return pose

    # ---------------- detecções ----------------
    def store(self, kind, labelled_points):
        self.objects[kind] = (self.get_clock().now().nanoseconds * 1e-9, labelled_points)

    def balls_callback(self, msg):
        pose, intr, (_, h) = self.camera_pose(msg.header), self.intrinsics(), self.image_size()
        out = sv3dm.BallArray()
        out.header.stamp, out.header.frame_id = msg.header.stamp, self.frame
        points = []
        for ball in msg.balls:
            p = ball_ground_point(pose.footprint_camera, intr, ball.center.x, ball.center.y,
                                  ball.bb.size_x, ball.bb.size_y, h)
            if p is None:
                continue
            b = sv3dm.Ball()
            b.center = Point(x=p[0], y=p[1], z=BALL_RADIUS)
            b.confidence = ball.confidence
            out.balls.append(b)
            points.append(('ball', p))
        self.pub_ball.publish(out)
        self.store('ball', points)

    def footpoint_objects(self, msg, items, threshold):
        pose, intr, (_, h) = self.camera_pose(msg.header), self.intrinsics(), self.image_size()
        found = []
        for item in items:
            p = footpoint_ground_point(pose.footprint_camera, intr, item.bb.center.position.x,
                                       item.bb.center.position.y, item.bb.size_y, h, threshold)
            if p is not None:
                found.append((item, p))
        return found

    def fill_bb3d(self, obj, item, p, size):
        obj.bb.size.x, obj.bb.size.y, obj.bb.size.z = size
        obj.bb.center.position = Point(x=p[0], y=p[1], z=size[2] / 2.0)
        obj.bb.center.orientation.w = 1.0
        obj.attributes = item.attributes
        obj.confidence = item.confidence

    def goalposts_callback(self, msg):
        out = sv3dm.GoalpostArray()
        out.header.stamp, out.header.frame_id = msg.header.stamp, self.frame
        size = (0.1, 0.1, 1.0)
        found = self.footpoint_objects(msg, msg.posts, self.post_threshold)
        for item, p in found:
            g = sv3dm.Goalpost()
            self.fill_bb3d(g, item, p, size)
            out.posts.append(g)
        self.pub_goal.publish(out)
        self.store('goalpost', [('goalpost', p) for _, p in found])

    def robots_callback(self, msg):
        out = sv3dm.RobotArray()
        out.header.stamp, out.header.frame_id = msg.header.stamp, self.frame
        size = (0.2, 0.2, 1.0)
        found = self.footpoint_objects(msg, msg.robots, self.robot_threshold)
        for item, p in found:
            r = sv3dm.Robot()
            self.fill_bb3d(r, item, p, size)
            out.robots.append(r)
        self.pub_robot.publish(out)
        self.store('robot', [('robot', p) for _, p in found])

    def markings_callback(self, msg):
        pose, intr = self.camera_pose(msg.header), self.intrinsics()
        out = sv3dm.MarkingArray()
        out.header.stamp, out.header.frame_id = msg.header.stamp, self.frame
        points = []
        for inter in msg.intersections:
            p = pixel_to_ground(pose.footprint_camera, intr, inter.center.x, inter.center.y)
            if p is None:
                continue
            m = sv3dm.MarkingIntersection()
            m.center = Point(x=p[0], y=p[1], z=0.0)
            m.num_rays = inter.num_rays
            m.confidence = inter.confidence
            out.intersections.append(m)
            points.append((RAYS_LABEL.get(inter.num_rays, '?'), p))
        self.pub_marking.publish(out)
        self.store('marking', points)

    def segmentation_callback(self, msg):
        if msg.encoding != 'mono8':
            return
        mask = np.frombuffer(msg.data, np.uint8).reshape(msg.height, msg.step)[:, :msg.width]
        pose = self.camera_pose(msg.header)
        points = mask_line_points(pose.footprint_camera, self.intrinsics(), mask, *self.image_size(),
                                  max_range=self.line_max_range, max_points=self.line_max_points)
        self.lines = (self.get_clock().now().nanoseconds * 1e-9, points)
        cloud = PointCloud2()
        cloud.header.stamp, cloud.header.frame_id = msg.header.stamp, self.frame
        cloud.height, cloud.width = 1, len(points)
        cloud.fields = [PointField(name=n, offset=4 * i, datatype=PointField.FLOAT32, count=1)
                        for i, n in enumerate('xyz')]
        cloud.point_step, cloud.row_step = 12, 12 * len(points)
        cloud.is_dense = True
        xyz = np.zeros((len(points), 3), np.float32)
        xyz[:, :2] = points
        cloud.data = xyz.tobytes()
        self.pub_lines.publish(cloud)

    # ---------------- depuração ----------------
    def current_objects(self):
        now = self.get_clock().now().nanoseconds * 1e-9
        return [obj for t, objs in self.objects.values() if now - t < OBJECT_TTL_S for obj in objs]

    def draw(self):
        if self.last_pose is None:
            return
        objects = self.current_objects()
        self.publish_markers(objects)
        if not self.show and self.pub_birdseye.get_subscription_count() == 0:
            return
        pose, intr = self.last_pose, self.intrinsics()
        now = self.get_clock().now().nanoseconds * 1e-9
        lines = self.lines[1] if now - self.lines[0] < OBJECT_TTL_S else np.empty((0, 2))
        w, h = self.image_size()
        header = [f'{self.mode}  cam h={pose.height:.3f} m  pitch={math.degrees(pose.pitch):.1f} deg'
                  + (f'  apoio={pose.support}' if pose.support else ''),
                  (f'torso h={pose.footprint_torso[2, 3]:.3f} m  ' if pose.footprint_torso is not None
                   else f'eixo do tilt h={self.tilt_axis_height:.3f} m  ') + f'{w}x{h}  f={intr.fx:.0f} px']
        img = self.birdseye.draw(pose, intr, (w, h), objects, lines, header)
        msg = Image()
        msg.header.stamp, msg.header.frame_id = self.get_clock().now().to_msg(), self.frame
        msg.height, msg.width = img.shape[:2]
        msg.encoding, msg.step = 'bgr8', img.shape[1] * 3
        msg.data = array.array('B', img.tobytes())
        self.pub_birdseye.publish(msg)
        if self.show:
            cv2.imshow('IPM (vista de cima)', img)
            cv2.waitKey(1)

    def publish_tf(self, pose, header):
        stamp = (header.stamp.sec, header.stamp.nanosec)
        if stamp == self.last_tf_stamp:     # evita TF_REPEATED_DATA nos listeners
            return
        self.last_tf_stamp = stamp
        camera_frame = header.frame_id or 'camera_optical_frame'
        msgs = []
        frames = [(camera_frame, pose.footprint_camera @ CAMERA_TO_OPTICAL)]
        if pose.footprint_torso is not None:
            frames.append((self.kin.torso_link, pose.footprint_torso))
        for child, t in frames:
            tf = TransformStamped()
            tf.header.stamp, tf.header.frame_id, tf.child_frame_id = header.stamp, self.frame, child
            tf.transform.translation.x, tf.transform.translation.y, tf.transform.translation.z = map(float, t[:3, 3])
            q = matrix_to_quaternion(t[:3, :3])
            tf.transform.rotation.x, tf.transform.rotation.y, tf.transform.rotation.z, tf.transform.rotation.w = q
            msgs.append(tf)
        self.tf.sendTransform(msgs)

    def publish_markers(self, objects):
        markers = MarkerArray()
        clear = Marker()
        clear.action = Marker.DELETEALL
        markers.markers.append(clear)
        colors = {'ball': (1.0, 0.55, 0.0), 'goalpost': (1.0, 0.9, 0.0), 'robot': (0.0, 0.5, 1.0)}
        stamp = self.get_clock().now().to_msg()
        for i, (label, (x, y)) in enumerate(objects):
            m = Marker()
            m.header.stamp, m.header.frame_id = stamp, self.frame
            m.ns, m.id = label, i
            m.type = Marker.SPHERE if label == 'ball' else Marker.CYLINDER if label in colors else Marker.CUBE
            m.pose.position = Point(x=float(x), y=float(y), z=BALL_RADIUS if label == 'ball' else 0.02)
            m.pose.orientation.w = 1.0
            m.scale.x = m.scale.y = {'ball': 0.14, 'goalpost': 0.1, 'robot': 0.2}.get(label, 0.08)
            m.scale.z = 0.14 if label == 'ball' else 0.04
            m.color.r, m.color.g, m.color.b = colors.get(label, (1.0, 0.0, 1.0))
            m.color.a = 0.9
            markers.markers.append(m)
        self.pub_markers.publish(markers)


def main(args=None):
    rclpy.init(args=args)
    node = IPMNode()
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
