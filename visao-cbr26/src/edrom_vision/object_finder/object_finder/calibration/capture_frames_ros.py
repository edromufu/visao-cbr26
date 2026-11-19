"""
Captura N frames de um tópico ``sensor_msgs/Image`` a cada T segundos.

Não depende de ``cv_bridge``: decodifica ``bgr8/bgra8/rgb8/rgba8/mono8`` com
numpy (:func:`ros_image.image_msg_to_bgr`). Precisa de ROS 2 (Humble)::

    ros2 run object_finder capture_frames_ros --ros-args \
        -p topico:=/AUREA/camera_optical_frame/image_color -p n:=20 -p intervalo:=1.0 -p saida:=frames_sim

ou, sem instalar o pacote::

    python3 -m object_finder.calibration.capture_frames_ros \
        --topico /AUREA/camera_optical_frame/image_color -n 20 -t 1.0 --saida frames_sim

NÃO TESTADO com ROS real nesta sessão (só a decodificação tem teste).
"""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
import sys
import time
from typing import Any, Optional, Sequence

import cv2

from .ros_image import image_msg_to_bgr


class FrameSaver:
    """Lógica de salvar (testável sem ROS): decide quando gravar cada mensagem."""

    def __init__(self, n: int, interval: float, out_dir: Path, prefix: str = 'frame') -> None:
        self.n, self.interval, self.out_dir, self.prefix = n, interval, Path(out_dir), prefix
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.saved: list = []
        self.next_t = 0.0

    @property
    def done(self) -> bool:
        """Já salvou N frames."""
        return len(self.saved) >= self.n

    def on_msg(self, msg: Any, now: float) -> Optional[Path]:
        """Recebe uma mensagem; grava se passou o intervalo."""
        if self.done or now < self.next_t:
            return None
        frame = image_msg_to_bgr(msg)
        stamp = dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        path = self.out_dir / f'{self.prefix}_{stamp}_{len(self.saved):03d}.png'
        cv2.imwrite(str(path), frame)
        self.saved.append(path)
        self.next_t = now + self.interval
        return path


def main(argv: Optional[Sequence[str]] = None) -> int:  # pragma: no cover - precisa de ROS
    """Ponto de entrada (aceita argumentos de linha de comando ou parâmetros ROS)."""
    import rclpy
    from rclpy.node import Node
    from sensor_msgs.msg import Image

    ap = argparse.ArgumentParser()
    ap.add_argument('--topico', default='/camera/image_raw')
    ap.add_argument('-n', type=int, default=20)
    ap.add_argument('-t', type=float, default=1.0)
    ap.add_argument('--saida', default='frames_ros')
    a, ros_args = ap.parse_known_args(argv if argv is not None else sys.argv[1:])
    rclpy.init(args=ros_args)
    node = Node('capture_frames_ros')
    topico = node.declare_parameter('topico', a.topico).value
    n = int(node.declare_parameter('n', a.n).value)
    intervalo = float(node.declare_parameter('intervalo', a.t).value)
    saida = node.declare_parameter('saida', a.saida).value
    saver = FrameSaver(n, intervalo, Path(saida))

    def cb(msg: Any) -> None:
        try:
            p = saver.on_msg(msg, time.monotonic())
        except ValueError as exc:
            node.get_logger().error(str(exc))
            return
        if p is not None:
            node.get_logger().info(f'[{len(saver.saved)}/{n}] {p}')

    node.create_subscription(Image, topico, cb, 5)
    node.get_logger().info(f'assinando {topico}; salvando {n} frames em {saida}')
    try:
        while rclpy.ok() and not saver.done:
            rclpy.spin_once(node, timeout_sec=0.2)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()
    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
