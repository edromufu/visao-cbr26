"""
Conversão de ``sensor_msgs/Image`` para BGR com numpy (sem cv_bridge).

Usado pela captura ROS, pelo calibrador (fonte ``--ros-topico``) e pelo nó.
O ``rclpy`` só é importado dentro de :class:`RosImageSource`.
"""

from __future__ import annotations

import threading
from typing import Any, Optional

import cv2
import numpy as np

SUPPORTED = ('bgr8', 'bgra8', 'rgb8', 'rgba8', 'mono8')


def image_msg_to_bgr(msg: Any) -> np.ndarray:
    """
    Converta uma mensagem ``sensor_msgs/Image`` em matriz BGR ``uint8``.

    Aceita ``bgr8``, ``bgra8``, ``rgb8``, ``rgba8`` e ``mono8``; respeita o
    ``step`` (preenchimento no fim de cada linha) e ``is_bigendian`` (sem
    efeito em 8 bits).
    """
    enc = str(msg.encoding).lower()
    if enc not in SUPPORTED:
        raise ValueError(f'encoding não suportado: {msg.encoding} (use {", ".join(SUPPORTED)})')
    ch = {'bgr8': 3, 'rgb8': 3, 'bgra8': 4, 'rgba8': 4, 'mono8': 1}[enc]
    h, w, step = int(msg.height), int(msg.width), int(msg.step)
    buf = np.frombuffer(bytes(msg.data), dtype=np.uint8)
    if step < w * ch or buf.size < step * h:
        raise ValueError(f'tamanho inconsistente: {buf.size} bytes, step={step}, {w}x{h}x{ch}')
    arr = buf[:step * h].reshape(h, step)[:, :w * ch].reshape(h, w, ch)
    if enc == 'bgr8':
        return arr.copy()
    if enc == 'bgra8':
        return cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
    if enc == 'rgb8':
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    if enc == 'rgba8':
        return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
    return cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)


class RosImageSource:  # pragma: no cover - precisa de ROS 2 (NÃO TESTADO aqui)
    """Assina um tópico de imagem num thread e guarda o frame mais recente."""

    def __init__(self, topic: str, node_name: str = 'rlv_image_source') -> None:
        import rclpy
        from rclpy.node import Node
        from sensor_msgs.msg import Image

        if not rclpy.ok():
            rclpy.init()
        self._rclpy = rclpy
        self._node = Node(node_name)
        self._lock = threading.Lock()
        self._frame: Optional[np.ndarray] = None
        self.count = 0
        self._node.create_subscription(Image, topic, self._cb, 5)
        self._thread = threading.Thread(target=rclpy.spin, args=(self._node,), daemon=True)
        self._thread.start()

    def _cb(self, msg: Any) -> None:
        try:
            frame = image_msg_to_bgr(msg)
        except ValueError as exc:
            self._node.get_logger().warn(str(exc))
            return
        with self._lock:
            self._frame = frame
            self.count += 1

    def read(self) -> Optional[np.ndarray]:
        """Último frame recebido (cópia) ou ``None``."""
        with self._lock:
            return None if self._frame is None else self._frame.copy()

    def close(self) -> None:
        """Encerra o nó."""
        self._node.destroy_node()
        if self._rclpy.ok():
            self._rclpy.shutdown()
