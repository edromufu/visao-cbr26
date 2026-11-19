"""
Republica o camera_info no formato da imagem retificada pelo image_proc.

Os pixels da imagem retificada (image_rect) seguem a matriz de projeção P do
camera_info, sem distorção, e não a K. O IPM sempre usa K (e D, se
use_distortion for True), então este nó publica um camera_info com
K = P[:3, :3] e D = 0. Com ele, o IPM fica correto para detecções feitas na
imagem retificada (com use_distortion: False).

Assina `camera_info` e publica `camera_info_rect`.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo


class CameraInfoRect(Node):

    def __init__(self):
        super().__init__('camera_info_rect')
        self.pub = self.create_publisher(CameraInfo, 'camera_info_rect', 1)
        self.create_subscription(CameraInfo, 'camera_info', self.ao_receber_camera_info, 1)

    def ao_receber_camera_info(self, msg):
        p = msg.p
        msg.k = [p[0], p[1], p[2],
                 p[4], p[5], p[6],
                 p[8], p[9], p[10]]
        msg.d = [0.0] * len(msg.d)
        msg.r = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = CameraInfoRect()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
