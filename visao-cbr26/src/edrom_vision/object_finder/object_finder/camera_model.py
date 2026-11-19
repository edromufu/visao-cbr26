"""
Modelo de câmera: distorção e projeção ao chão (referencial egocêntrico).

Convenções:

* imagem: ``u`` para a direita, ``v`` para baixo (pixels);
* robô (egocêntrico, no chão, sob a câmera): ``x`` para a frente, ``y`` para a
  esquerda; ângulo = ``atan2(y, x)`` (positivo à esquerda, como o
  ``localization_pkg`` da EDROM espera);
* ``pitch`` positivo = câmera inclinada para baixo.

Dois jeitos de ir ao chão: pinhole (altura + inclinação, ex.: AUREA no Webots)
ou homografia imagem->chão (``homography_matrix.npy`` da EDROM). A homografia
do kit é a identidade (não calibrada): :meth:`CameraModel.from_edrom` a ignora
e avisa.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from pathlib import Path
from typing import Optional, Sequence, Tuple
import warnings

import cv2
import numpy as np


@dataclass
class CameraModel:
    """Câmera pinhole com distorção opcional e altura/inclinação para o chão."""

    fx: float
    fy: float
    cx: float
    cy: float
    height: Optional[float] = None          # metros
    pitch: float = 0.0                      # rad, + para baixo
    dist: Optional[np.ndarray] = None       # coeficientes do OpenCV
    homography: Optional[np.ndarray] = None  # imagem (sem distorção) -> chão (m)
    nome: str = ''
    _K: np.ndarray = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._K = np.array([[self.fx, 0, self.cx], [0, self.fy, self.cy], [0, 0, 1]], float)
        if self.dist is not None:
            self.dist = np.asarray(self.dist, float).reshape(-1)
            if not np.any(self.dist):
                self.dist = None

    # ---------------------------------------------------------- fábricas
    @staticmethod
    def from_fov(width: int, height_px: int, hfov: float, height: Optional[float] = None,
                 pitch: float = 0.0, nome: str = 'fov') -> 'CameraModel':
        """Pinhole ideal a partir do campo de visão horizontal (Webots)."""
        fx = (width / 2.0) / math.tan(hfov / 2.0)
        return CameraModel(fx, fx, width / 2.0, height_px / 2.0, height, pitch, nome=nome)

    @staticmethod
    def from_edrom(camera_matrix: Path, dist_coeffs: Optional[Path] = None,
                   homography: Optional[Path] = None, height: Optional[float] = None,
                   pitch: float = 0.0, scale_to: Optional[Tuple[int, int]] = None,
                   calib_size: Tuple[int, int] = (640, 480)) -> 'CameraModel':
        """
        Arquivos ``.npy`` da EDROM (``object_finder/resource``).

        ``scale_to=(w, h)`` reescala K se a resolução usada for diferente da
        calibração (``calib_size``, suposta 640x480: cx≈349, cy≈215).
        """
        K = np.load(str(camera_matrix)).astype(float)
        if scale_to is not None:
            sx, sy = scale_to[0] / calib_size[0], scale_to[1] / calib_size[1]
            K = K.copy()
            K[0, :] *= sx
            K[1, :] *= sy
        d = np.load(str(dist_coeffs)) if dist_coeffs else None
        H = None
        if homography:
            H = np.load(str(homography)).astype(float)
            if np.allclose(H, np.eye(3)):
                warnings.warn('homography_matrix.npy é a identidade (não calibrada): ignorada')
                H = None
        return CameraModel(K[0, 0], K[1, 1], K[0, 2], K[1, 2], height, pitch, d, H, nome='edrom')

    @property
    def K(self) -> np.ndarray:
        """Matriz intrínseca 3x3."""
        return self._K

    # -------------------------------------------------------- distorção
    def undistort_points(self, pts: np.ndarray) -> np.ndarray:
        """Pixels distorcidos -> pixels sem distorção (mesma K)."""
        pts = np.asarray(pts, float).reshape(-1, 2)
        if self.dist is None or len(pts) == 0:
            return pts.copy()
        out = cv2.undistortPoints(pts.reshape(-1, 1, 2), self._K, self.dist, P=self._K)
        return out.reshape(-1, 2)

    def distort_points(self, pts: np.ndarray) -> np.ndarray:
        """Pixels sem distorção -> pixels da imagem original."""
        pts = np.asarray(pts, float).reshape(-1, 2)
        if self.dist is None or len(pts) == 0:
            return pts.copy()
        norm = (pts - [self.cx, self.cy]) / [self.fx, self.fy]
        obj = np.hstack([norm, np.ones((len(norm), 1))]).reshape(-1, 1, 3)
        img, _ = cv2.projectPoints(obj, np.zeros(3), np.zeros(3), self._K, self.dist)
        return img.reshape(-1, 2)

    # ------------------------------------------------------------- chão
    @property
    def can_project(self) -> bool:
        """Indica se há modelo de chão (homografia ou altura)."""
        return self.homography is not None or self.height is not None

    def image_to_ground(self, u: float, v: float, undistorted: bool = False) -> Optional[Tuple[float, float]]:
        """Pixel -> (x à frente, y à esquerda) em metros, ou ``None`` (acima do horizonte)."""
        if not undistorted:
            u, v = self.undistort_points(np.array([[u, v]]))[0]
        if self.homography is not None:
            p = self.homography @ np.array([u, v, 1.0])
            if abs(p[2]) < 1e-12:
                return None
            return float(p[0] / p[2]), float(p[1] / p[2])
        if self.height is None:
            return None
        xn, yn = (u - self.cx) / self.fx, (v - self.cy) / self.fy
        c, s = math.cos(self.pitch), math.sin(self.pitch)
        X = c * 1.0 - s * yn
        Y = -xn
        Z = -s * 1.0 - c * yn
        if Z >= -1e-9:
            return None
        t = self.height / -Z
        return float(t * X), float(t * Y)

    def ground_to_image(self, x: float, y: float) -> Tuple[float, float]:
        """(x à frente, y à esquerda) no chão -> pixel sem distorção."""
        if self.height is None:
            raise ValueError('modelo sem altura')
        c, s = math.cos(self.pitch), math.sin(self.pitch)
        Xp = c * x + s * self.height
        Zp = s * x - c * self.height
        z, xo, yo = Xp, -y, -Zp
        return float(self.cx + self.fx * xo / z), float(self.cy + self.fy * yo / z)

    @staticmethod
    def polar(x: float, y: float) -> Tuple[float, float]:
        """(distância, ângulo) egocêntricos."""
        return float(math.hypot(x, y)), float(math.atan2(y, x))

    def line_polar(self, p1: Sequence[float], p2: Sequence[float],
                   undistorted: bool = True) -> Optional[Tuple[float, float, float]]:
        """Reta pelos pixels p1, p2 -> (distância perpendicular, ângulo do pé, comprimento) no chão."""
        a = self.image_to_ground(p1[0], p1[1], undistorted)
        b = self.image_to_ground(p2[0], p2[1], undistorted)
        if a is None or b is None:
            return None
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        if L < 1e-9:
            return None
        nx, ny = -dy / L, dx / L
        d = a[0] * nx + a[1] * ny
        if d < 0:
            nx, ny, d = -nx, -ny, -d
        return float(d), float(math.atan2(ny, nx)), float(L)
