#!/usr/bin/env python3
"""
Balanco de branco FIXO por software (ganho por canal B, G, R).

Para cameras USB cuja correcao de cor propria nao resolve (imagem roxa,
esverdeada etc. mesmo com o white_balance da camera ajustado). O ganho e
calculado uma vez, com uma folha BRANCA ou CINZA ocupando o centro da imagem,
e depois aplicado em todo frame via LUT (< 1 ms). Ganho fixo e melhor que
"gray world" a cada frame: no campo, o tapete verde engana o gray world do
mesmo jeito que engana o AWB da camera.

Calibracao (com o usb_cam rodando, ex.: pelo vision.launch.py):
    # segure uma folha branca/cinza cobrindo o CENTRO da imagem e rode:
    ros2 run yoeo_vision wb_calib --ros-args -p out:=$HOME/wb_gains.json

Depois passe o arquivo para o no de visao:
    ros2 launch yoeo_vision vision.launch.py wb_file:=$HOME/wb_gains.json
"""
import json
import time

import cv2
import numpy as np


def make_lut(gains_bgr):
    """LUT (1,256,3) que multiplica cada canal pelo seu ganho, com saturacao em 255."""
    x = np.arange(256, dtype=np.float32)
    lut = np.stack([np.clip(x * g, 0, 255) for g in gains_bgr], axis=1)
    return lut.astype(np.uint8)[None]


def load_wb_lut(path):
    """Le os ganhos salvos e devolve (lut, ganhos), ou (None, None) se nao houver arquivo."""
    try:
        with open(path) as f:
            gains = json.load(f)["gains_bgr"]
    except (OSError, KeyError, ValueError, TypeError):
        return None, None
    return make_lut(gains), gains


def apply_wb(frame_bgr, lut):
    return cv2.LUT(frame_bgr, lut) if lut is not None else frame_bgr


def main(args=None):
    """No ROS 2 que calibra os ganhos a partir do topico da camera."""
    import rclpy
    from cv_bridge import CvBridge
    from rclpy.node import Node
    from rclpy.qos import qos_profile_sensor_data
    from sensor_msgs.msg import Image

    class WBCalib(Node):
        def __init__(self):
            super().__init__('wb_calib')
            self.topic = self.declare_parameter('image_topic', '/camera/image_raw').value
            self.roi = float(self.declare_parameter('roi', 0.4).value)
            self.n_frames = int(self.declare_parameter('frames', 30).value)
            self.warmup = float(self.declare_parameter('warmup_s', 2.0).value)
            self.out = self.declare_parameter('out', 'wb_gains.json').value
            self.bridge = CvBridge()
            self.sums = np.zeros(3)
            self.count = 0
            self.last = None
            self.t0 = None
            self.done = False
            self.create_subscription(Image, self.topic, self.cb, qos_profile_sensor_data)
            self.get_logger().info(
                f'Lendo {self.topic}. Segure uma folha branca/cinza no CENTRO da imagem...')

        def cb(self, msg):
            if self.done:
                return
            now = time.monotonic()
            if self.t0 is None:
                self.t0 = now
            if now - self.t0 < self.warmup:  # espera a exposicao estabilizar
                return
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            h, w = frame.shape[:2]
            rh, rw = int(h * self.roi / 2), int(w * self.roi / 2)
            roi = frame[h // 2 - rh:h // 2 + rh, w // 2 - rw:w // 2 + rw]
            roi = roi.reshape(-1, 3).astype(np.float32)
            # ignora pixels estourados ou muito escuros: nao dizem nada sobre a cor
            ok_px = (roi.max(1) < 250) & (roi.min(1) > 15)
            if ok_px.sum() < 100:
                self.get_logger().warn(
                    'Regiao central estourada ou escura demais: afaste a folha da '
                    'lampada ou ajuste a exposicao', throttle_duration_sec=2.0)
                return
            self.sums += roi[ok_px].mean(0)
            self.count += 1
            self.last = frame
            if self.count >= self.n_frames:
                self.finish()

        def finish(self):
            self.done = True
            mean_bgr = self.sums / self.count
            gains = np.clip(mean_bgr.mean() / mean_bgr, 0.5, 2.0)
            log = self.get_logger()
            log.info(f'media B,G,R na folha: {mean_bgr.round(1).tolist()}')
            log.info(f'ganhos B,G,R:         {gains.round(3).tolist()}')
            if gains.max() / gains.min() > 1.6:
                log.warn('Ganhos muito diferentes entre si: a camera pode estar captando '
                         'infravermelho (lente sem filtro IR-cut). A correcao ajuda, mas e parcial.')
            with open(self.out, 'w') as f:
                json.dump({'gains_bgr': gains.tolist(), 'mean_bgr': mean_bgr.tolist(),
                           'time': time.strftime('%Y-%m-%d %H:%M:%S')}, f, indent=2)
            check = self.out.rsplit('.', 1)[0] + '_check.jpg'
            cv2.imwrite(check, np.hstack([self.last, apply_wb(self.last, make_lut(gains))]))
            log.info(f'Salvo: {self.out}  |  comparacao antes|depois: {check}')

    rclpy.init(args=args)
    node = WBCalib()
    try:
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
