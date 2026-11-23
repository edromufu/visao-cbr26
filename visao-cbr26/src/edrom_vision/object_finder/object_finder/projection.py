"""IPM: pixel -> plano do chão, dada a pose da câmera em base_footprint e a intrínseca.

Referencial da câmera: x ao longo do eixo óptico, y para a esquerda, z para cima. Um pixel vira o raio
(1, -xn, -yn), onde (xn, yn) são as coordenadas normalizadas sem distorção (convenção do OpenCV: x para a
direita, y para baixo).
"""
import math

import cv2
import numpy as np

BALL_RADIUS = 0.07
LINE_CLASS = 2      # valor das linhas na máscara do YOEO


class Intrinsics:
    """Matriz K e distorção (plumb_bob/rational_polynomial, como no camera_info)."""

    def __init__(self, k, d=None):
        self.k = np.asarray(k, float).reshape(3, 3)
        d = np.zeros(0) if d is None else np.asarray(d, float).ravel()
        self.d = d if np.any(d != 0) else None
        self.fx, self.fy = self.k[0, 0], self.k[1, 1]
        self.cx, self.cy = self.k[0, 2], self.k[1, 2]

    @classmethod
    def from_fov(cls, width, height, fov_horizontal):
        """Pinhole ideal com FOV horizontal, centro no meio da imagem, sem distorção."""
        f = (width / 2.0) / math.tan(fov_horizontal / 2.0)
        return cls([[f, 0, width / 2.0], [0, f, height / 2.0], [0, 0, 1]])

    @classmethod
    def from_camera_info(cls, msg, width=None, height=None):
        """None se o camera_info não tem calibração (K zerada). Reescala K se a imagem tem outro tamanho."""
        k = np.asarray(msg.k, float).reshape(3, 3)
        if k[0, 0] <= 0 or k[1, 1] <= 0:
            return None
        if width and height and msg.width and msg.height and (msg.width, msg.height) != (width, height):
            k = k.copy()
            k[0] *= width / msg.width
            k[1] *= height / msg.height
        return cls(k, msg.d)

    def normalize(self, u, v):
        u = np.atleast_1d(np.asarray(u, float))
        v = np.atleast_1d(np.asarray(v, float))
        if self.d is None:
            return (u - self.cx) / self.fx, (v - self.cy) / self.fy
        criteria = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 20, 1e-8)
        pts = cv2.undistortPointsIter(np.stack([u, v], -1).reshape(-1, 1, 2), self.k, self.d, None, None,
                                      criteria).reshape(-1, 2)
        return pts[:, 0], pts[:, 1]

    def project(self, xn, yn):
        """Coordenadas normalizadas -> pixel, com distorção."""
        if self.d is None:
            return self.cx + self.fx * xn, self.cy + self.fy * yn
        p, _ = cv2.projectPoints(np.array([[xn, yn, 1.0]]), np.zeros(3), np.zeros(3), self.k, self.d)
        return float(p[0, 0, 0]), float(p[0, 0, 1])


def pixels_to_ground(footprint_camera, intr, u, v, plane_height=0.0):
    """Projeta pixels no plano z = plane_height de base_footprint.

    Retorna [N, 2] com (x, y) em metros; NaN onde o raio não encontra o plano à frente da câmera.
    """
    xn, yn = intr.normalize(u, v)
    rays = np.stack([np.ones_like(xn), -xn, -yn], axis=1) @ footprint_camera[:3, :3].T
    origin = footprint_camera[:3, 3]
    out = np.full((len(xn), 2), np.nan)
    if origin[2] <= plane_height:
        return out
    hit = rays[:, 2] < -1e-6
    scale = (plane_height - origin[2]) / rays[hit, 2]
    out[hit] = origin[:2] + scale[:, None] * rays[hit, :2]
    return out


def pixel_to_ground(footprint_camera, intr, u, v, plane_height=0.0):
    p = pixels_to_ground(footprint_camera, intr, [u], [v], plane_height)[0]
    return None if np.isnan(p[0]) else (float(p[0]), float(p[1]))


def ground_to_pixel(footprint_camera, intr, x, y, z=0.0):
    """Inverso do IPM, para desenhar e testar. None se o ponto fica atrás da câmera."""
    p = footprint_camera[:3, :3].T @ (np.array([x, y, z]) - footprint_camera[:3, 3])
    if p[0] <= 1e-3:
        return None
    return intr.project(-p[1] / p[0], -p[2] / p[0])


def ball_ground_point(footprint_camera, intr, cx, cy, box_w, box_h, img_h):
    """Centro da bola no plano z = raio. Bola cortada pela borda inferior: o centro real fica abaixo."""
    v = float(cy)
    if box_h > 0 and cy + box_h / 2.0 >= img_h - 2:
        v = cy - box_h / 2.0 + box_w / 2.0
    return pixel_to_ground(footprint_camera, intr, float(cx), v, BALL_RADIUS)


def footpoint_ground_point(footprint_camera, intr, cx, cy, box_h, img_h, out_of_image_threshold=0.8):
    """Base da caixa (trave, robô) no chão.

    Mesma regra do soccer_ipm: None se a base passa de `out_of_image_threshold * altura da imagem`, porque o
    objeto pode estar cortado pela borda inferior e a base visível não é o pé.
    """
    bottom = cy + box_h / 2.0
    if bottom > out_of_image_threshold * img_h:
        return None
    return pixel_to_ground(footprint_camera, intr, float(cx), bottom)


def mask_line_points(footprint_camera, intr, mask, width, height, max_range=3.5, cell=0.1, max_points=80):
    """Pixels de linha da máscara do YOEO no chão, um por célula de `cell` m, até `max_points`."""
    rows, cols = np.nonzero(mask == LINE_CLASS)
    if rows.size == 0:
        return np.empty((0, 2))
    u = (cols + 0.5) * width / mask.shape[1]
    v = (rows + 0.5) * height / mask.shape[0]
    points = pixels_to_ground(footprint_camera, intr, u, v)
    points = points[~np.isnan(points[:, 0])]
    points = points[np.hypot(points[:, 0], points[:, 1]) <= max_range]
    if len(points) == 0:
        return points
    _, first = np.unique(np.round(points / cell).astype(int), axis=0, return_index=True)
    points = points[first]
    if len(points) > max_points:
        points = points[np.random.choice(len(points), max_points, replace=False)]
    return points
