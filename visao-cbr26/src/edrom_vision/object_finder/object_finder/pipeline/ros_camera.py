"""Quadros da câmera pelo `usb_cam` (ROS), para o `calibrar --ros`.

Assina o tópico de imagem do `usb_cam` (padrão `/camera/image_raw`, o mesmo do `vision.launch.py`). Se ninguém
publica nele (visão parada), sobe o `usb_cam` com o `config/usb_cam.yaml` e o derruba no fim. Assim a calibração
vê a imagem com o mesmo formato, resolução e controles de câmera que a visão usa na partida e, com a visão
rodando, não disputa a câmera com ela.

O ROS só é importado aqui dentro, então o resto de `object_finder.pipeline` continua funcionando sem ROS.
"""

import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

DEFAULT_TOPIC = '/camera/image_raw'
DISCOVERY_SEC = 2.0        # espera para descobrir se alguém já publica no tópico
FIRST_FRAME_SEC = 15.0     # o usb_cam leva alguns segundos para abrir a câmera
READ_TIMEOUT_SEC = 1.0


def usb_cam_config() -> Optional[Path]:
    """`config/usb_cam.yaml` instalado (colcon) ou, sem instalar, o da árvore de fontes."""
    try:
        from ament_index_python.packages import get_package_share_directory
        path = Path(get_package_share_directory('object_finder')) / 'config' / 'usb_cam.yaml'
        if path.is_file():
            return path
    except Exception:  # pacote não instalado ou ament ausente
        pass
    path = Path(__file__).resolve().parents[2] / 'config' / 'usb_cam.yaml'
    return path if path.is_file() else None


def read_usb_cam_params(path: Optional[Path] = None) -> dict:
    """Os `ros__parameters` do usb_cam.yaml ({} se não houver arquivo)."""
    path = path or usb_cam_config()
    if path is None:
        return {}
    import yaml
    with open(path) as f:
        data = yaml.safe_load(f) or {}
    return next(iter(data.values()), {}).get('ros__parameters', {}) if data else {}


def image_to_bgr(encoding: str, height: int, width: int, step: int, data: bytes) -> np.ndarray:
    """sensor_msgs/Image -> BGR (sem cv_bridge)."""
    import cv2
    buf = np.frombuffer(data, np.uint8)
    channels = {'rgb8': 3, 'bgr8': 3, 'mono8': 1, 'yuv422_yuy2': 2, 'yuyv': 2}.get(encoding)
    if channels is None:
        raise RuntimeError(f"formato de imagem '{encoding}' não suportado (use pixel_format yuyv2rgb no usb_cam)")
    rows = buf.reshape(height, step)[:, :width * channels]
    image = rows.reshape(height, width, channels) if channels > 1 else rows.reshape(height, width)
    if encoding == 'rgb8':
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if encoding == 'mono8':
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if channels == 2:
        return cv2.cvtColor(image, cv2.COLOR_YUV2BGR_YUYV)
    return image.copy()


class RosCamera:
    """Mesma interface usada do cv2.VideoCapture: `isOpened()`, `read()`, `set()` e `release()`."""

    def __init__(self, topic: str = DEFAULT_TOPIC, video_device: Optional[str] = None):
        try:
            import rclpy
            from rclpy.qos import qos_profile_sensor_data
            from sensor_msgs.msg import Image
        except ImportError as error:
            raise RuntimeError(f'--ros precisa do ROS 2 (source /opt/ros/<distro>/setup.bash): {error}')

        self._rclpy = rclpy
        self._owns_context = not rclpy.ok()
        if self._owns_context:
            rclpy.init()
        self.topic = topic
        self.node = rclpy.create_node('calibrar')
        self._frame: Optional[np.ndarray] = None
        self._fresh = False
        self._error: Optional[str] = None
        self._process: Optional[subprocess.Popen] = None
        self.node.create_subscription(Image, topic, self._on_image, qos_profile_sensor_data)

        try:
            if not self._wait_for_publisher(DISCOVERY_SEC):
                self._start_usb_cam(video_device)
            else:
                print(f'calibrar: usando o {topic} que já está sendo publicado (visão/usb_cam rodando)')
            if not self._wait_for_frame(FIRST_FRAME_SEC):
                raise RuntimeError(self._error or f'nenhuma imagem em {topic} depois de {FIRST_FRAME_SEC:.0f} s '
                                   '(o usb_cam abriu a câmera? confira o video_device e a saída acima)')
        except BaseException:
            self.release()
            raise

    # -- ROS --------------------------------------------------------------------------------------

    def _on_image(self, msg) -> None:
        try:
            self._frame = image_to_bgr(msg.encoding, msg.height, msg.width, msg.step, bytes(msg.data))
            self._fresh = True
        except RuntimeError as error:
            self._error = str(error)

    def _spin_until(self, done, timeout: float) -> bool:
        deadline = time.monotonic() + timeout
        while not done():
            if time.monotonic() > deadline:
                return False
            if self._process is not None and self._process.poll() is not None:
                raise RuntimeError(f'o usb_cam fechou (código {self._process.returncode}); veja a mensagem acima')
            self._rclpy.spin_once(self.node, timeout_sec=0.05)
        return True

    def _wait_for_publisher(self, timeout: float) -> bool:
        return self._spin_until(lambda: self.node.count_publishers(self.topic) > 0, timeout)

    def _wait_for_frame(self, timeout: float) -> bool:
        return self._spin_until(lambda: self._fresh or self._error is not None, timeout) and self._error is None

    def _start_usb_cam(self, video_device: Optional[str]) -> None:
        config = usb_cam_config()
        if config is None:
            raise RuntimeError('config/usb_cam.yaml não encontrado (rode colcon build e source install/setup.bash)')
        namespace, _, name = self.topic.rstrip('/').rpartition('/')
        cmd = ['ros2', 'run', 'usb_cam', 'usb_cam_node_exe', '--ros-args',
               '-r', '__node:=usb_cam', '-r', f'__ns:={namespace or "/"}', '--params-file', str(config)]
        if name != 'image_raw':
            cmd += ['-r', f'image_raw:={name}']
        if video_device:
            cmd += ['-p', f'video_device:={video_device}']
        device = video_device or read_usb_cam_params(config).get('video_device', '?')
        print(f'calibrar: ninguém publica em {self.topic}; subindo o usb_cam ({device}, {config})')
        self._process = subprocess.Popen(cmd, start_new_session=True)

    # -- interface do VideoCapture ----------------------------------------------------------------

    def isOpened(self) -> bool:  # noqa: N802 (nome do OpenCV)
        return self._frame is not None

    def set(self, *_args) -> bool:
        return False  # resolução e formato vêm do usb_cam.yaml

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        self._fresh = False
        if not self._spin_until(lambda: self._fresh, READ_TIMEOUT_SEC):
            return False, None
        return True, self._frame

    def release(self) -> None:
        if self._process is not None and self._process.poll() is None:
            try:
                os.killpg(self._process.pid, signal.SIGINT)
                self._process.wait(timeout=5)
            except (subprocess.TimeoutExpired, ProcessLookupError):
                try:
                    os.killpg(self._process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        self._process = None
        if getattr(self, 'node', None) is not None:
            self.node.destroy_node()
            self.node = None
        if self._owns_context and self._rclpy.ok():
            self._rclpy.shutdown()
        self._owns_context = False
