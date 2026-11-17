"""
Gerador de campo sintético com verdade de terreno automática.

Campo KidSize (regras RoboCup Humanoid): 9 x 6 m, linhas de 5 cm, área do gol
1 x 3 m, área de pênalti 2 x 5 m, marca do pênalti a 1,5 m, círculo central
de 1,5 m de diâmetro, carpete com 1 m de borda. Câmera pinhole com os
parâmetros do AUREA (1080x720, FOV horizontal 0,785 rad, 0,70 m de altura).

A imagem é renderizada por raio: cada pixel (com superamostragem) é projetado
no chão; a cor vem da distância às linhas (analítica). A verdade de terreno
traz os cruzamentos visíveis (tipo L/T/X e as marcas), os segmentos de linha
visíveis e o círculo, já projetados na imagem.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

from .camera_model import CameraModel

L, W = 9.0, 6.0
LW = 0.05
GOAL_AREA = (1.0, 3.0)
PENALTY_AREA = (2.0, 5.0)
PENALTY_MARK = 1.5
CIRCLE_R = 0.75
BORDER = 1.0


def field_segments() -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
    """Segmentos (centros das linhas) em metros, origem no centro do campo."""
    hl, hw = L / 2, W / 2
    s = [((-hl, -hw), (hl, -hw)), ((-hl, hw), (hl, hw)),          # laterais
         ((-hl, -hw), (-hl, hw)), ((hl, -hw), (hl, hw)),          # linhas de fundo
         ((0, -hw), (0, hw))]                                     # linha do meio
    for sx in (-1, 1):
        x0 = sx * hl
        for (d, w) in (GOAL_AREA, PENALTY_AREA):
            x1 = x0 - sx * d
            s += [((x0, -w / 2), (x1, -w / 2)), ((x0, w / 2),
                                                 (x1, w / 2)), ((x1, -w / 2), (x1, w / 2))]
    return s


def field_crossings() -> List[Tuple[str, float, float]]:
    """Cruzamentos do campo (tipo, x, y). 'M' = marca (centro/pênalti)."""
    hl, hw = L / 2, W / 2
    c: List[Tuple[str, float, float]] = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            c.append(('L', sx * hl, sy * hw))
            for (d, w) in (GOAL_AREA, PENALTY_AREA):
                c.append(('T', sx * hl, sy * w / 2))
                c.append(('L', sx * (hl - d), sy * w / 2))
        c.append(('M', sx * (hl - PENALTY_MARK), 0.0))
    c += [('T', 0.0, -hw), ('T', 0.0, hw), ('X', 0.0, -CIRCLE_R),
          ('X', 0.0, CIRCLE_R), ('M', 0.0, 0.0)]
    return c


@dataclass
class Pose:
    """Pose da câmera no campo: posição (m), rumo (rad), inclinação (rad)."""

    x: float
    y: float
    yaw: float
    pitch: float = 0.0
    height: float = 0.70


@dataclass
class SyntheticFrame:
    """Imagem + verdade de terreno no mesmo formato do ``gt_marcacoes.json``."""

    image: np.ndarray
    gt: Dict[str, Any]
    pose: Pose
    camera: CameraModel
    info: Dict[str, Any] = field(default_factory=dict)


def _dist_to_segments(px: np.ndarray, py: np.ndarray, segs) -> np.ndarray:
    d = np.full(px.shape, np.inf, np.float32)
    for (x1, y1), (x2, y2) in segs:
        dx, dy = x2 - x1, y2 - y1
        L2 = dx * dx + dy * dy
        t = np.clip(((px - x1) * dx + (py - y1) * dy) / L2, 0, 1)
        d = np.minimum(d, np.hypot(px - x1 - t * dx, py - y1 - t * dy))
    return d


def _world_to_robot(pose: Pose, x: np.ndarray, y: np.ndarray):
    c, s = math.cos(pose.yaw), math.sin(pose.yaw)
    dx, dy = x - pose.x, y - pose.y
    return c * dx + s * dy, -s * dx + c * dy


def _robot_to_world(pose: Pose, xr, yr):
    c, s = math.cos(pose.yaw), math.sin(pose.yaw)
    return pose.x + c * xr - s * yr, pose.y + s * xr + c * yr


def render(pose: Pose, width: int = 1080, height: int = 720, hfov: float = 0.785, ss: int = 2,
           rng: Optional[np.random.Generator] = None, green_bgr=(36, 150, 40), white_bgr=(235, 235, 235),
           max_dist: float = 7.0) -> SyntheticFrame:
    """Renderiza um frame com a pose dada."""
    rng = rng or np.random.default_rng(0)
    cam = CameraModel.from_fov(width, height, hfov, pose.height, pose.pitch)
    # superamostragem
    us = (np.arange(width * ss) + 0.5) / ss - 0.5
    vs = (np.arange(height * ss) + 0.5) / ss - 0.5
    U, V = np.meshgrid(us, vs)
    xn, yn = (U - cam.cx) / cam.fx, (V - cam.cy) / cam.fy
    c, s = math.cos(pose.pitch), math.sin(pose.pitch)
    X, Y, Z = c - s * yn, -xn, -s - c * yn
    ground = Z < -1e-6
    t = np.where(ground, pose.height / np.where(ground, -Z, 1), 0)
    xr, yr = t * X, t * Y
    xw, yw = _robot_to_world(pose, xr, yr)
    dist = np.hypot(xr, yr)
    on_carpet = ground & (np.abs(xw) <= L / 2 + BORDER) & (np.abs(yw) <= W / 2 + BORDER)
    dline = _dist_to_segments(xw, yw, field_segments())
    dline = np.minimum(dline, np.abs(np.hypot(xw, yw) - CIRCLE_R))
    # marcas (cruzinhas 10 cm)
    for typ, mx, my in field_crossings():
        if typ == 'M':
            dline = np.minimum(dline, _dist_to_segments(xw, yw, [((mx - 0.05, my), (mx + 0.05, my)),
                                                                 ((mx, my - 0.05), (mx, my + 0.05))]))
    is_line = on_carpet & (dline <= LW / 2)
    img = np.zeros((height * ss, width * ss, 3), np.float32)
    sky = ~ground
    img[sky] = (200, 140, 90)
    img[ground & ~on_carpet] = (120, 120, 120)
    img[on_carpet] = green_bgr
    img[is_line] = white_bgr
    # placas atrás do carpete: faixa clara logo acima do horizonte "longe"
    img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
    noise = rng.normal(0, 4.0, img.shape).astype(np.float32)
    img = np.clip(img + noise, 0, 255).astype(np.uint8)
    gt = _ground_truth(pose, cam, width, height, max_dist)
    # cruzamentos colados na borda da imagem não têm braços visíveis: fora da conta
    gt['cruzamentos'] = [c for c in gt['cruzamentos'] if 16 <=
                         c['x'] < width - 16 and 16 <= c['y'] < height - 16]
    for c in gt['cruzamentos']:
        gp = cam.image_to_ground(c['x'], c['y'])
        c['dist_m'] = round(math.hypot(*gp), 2) if gp else None
    del dist
    return SyntheticFrame(img, gt, pose, cam)


def _visible(cam: CameraModel, pose: Pose, xw: float, yw: float, w: int, h: int, max_dist: float):
    xr, yr = _world_to_robot(pose, np.array(xw), np.array(yw))
    xr, yr = float(xr), float(yr)
    if xr <= 0.2 or math.hypot(xr, yr) > max_dist:
        return None
    u, v = cam.ground_to_image(xr, yr)
    if 0 <= u < w and 0 <= v < h:
        return u, v
    return None


def _ground_truth(pose: Pose, cam: CameraModel, w: int, h: int, max_dist: float) -> Dict[str, Any]:
    cruz, linhas, circ = [], [], []
    for typ, x, y in field_crossings():
        uv = _visible(cam, pose, x, y, w, h, max_dist)
        if uv is None:
            continue
        cruz.append({'tipo': 'X' if typ == 'M' else typ,
                    'x': uv[0], 'y': uv[1], 'marca': typ == 'M'})
    for (p, q) in field_segments():
        n = int(max(2, math.hypot(q[0] - p[0], q[1] - p[1]) / 0.02))
        pts = []
        for k in range(n + 1):
            tt = k / n
            uv = _visible(cam, pose, p[0] + tt * (q[0] - p[0]),
                          p[1] + tt * (q[1] - p[1]), w, h, max_dist)
            pts.append(uv)
        run: List[Tuple[float, float]] = []
        for uv in pts + [None]:
            if uv is not None:
                run.append(uv)
            elif len(run) >= 2:
                (x1, y1), (x2, y2) = run[0], run[-1]
                if math.hypot(x2 - x1, y2 - y1) >= 8:
                    linhas.append({'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2})
                run = []
            else:
                run = []
    cpts = []
    for k in range(180):
        a = 2 * math.pi * k / 180
        uv = _visible(cam, pose, CIRCLE_R * math.cos(a), CIRCLE_R * math.sin(a), w, h, max_dist)
        if uv is not None:
            cpts.append({'x': uv[0], 'y': uv[1]})
    if len(cpts) >= 5:
        circ.append({'fechado': len(cpts) == 180, 'pontos': cpts})
    return {'largura': w, 'altura': h, 'cruzamentos': cruz, 'linhas': linhas, 'circulos': circ}


def random_pose(rng: np.random.Generator, pitch_range=(0.0, 0.5)) -> Pose:
    """Pose aleatória dentro do campo, olhando para algum lugar do campo."""
    x = rng.uniform(-L / 2 + 0.5, L / 2 - 0.5)
    y = rng.uniform(-W / 2 + 0.3, W / 2 - 0.3)
    yaw = rng.uniform(-math.pi, math.pi)
    return Pose(x, y, yaw, rng.uniform(*pitch_range))


def perturb(img: np.ndarray, rng: np.random.Generator, brightness=(0.75, 1.25), blur_max: int = 2) -> np.ndarray:
    """Variante com ruído de brilho e borrão."""
    f = img.astype(np.float32) * rng.uniform(*brightness)
    k = int(rng.integers(0, blur_max + 1))
    out = np.clip(f, 0, 255).astype(np.uint8)
    if k > 0:
        out = cv2.GaussianBlur(out, (2 * k + 1, 2 * k + 1), 0)
    return out


def dataset(n: int, seed: int = 0, min_crossings: int = 1, variants: bool = False, **kw) -> List[SyntheticFrame]:
    """Gera ``n`` frames com pelo menos ``min_crossings`` cruzamentos visíveis."""
    rng = np.random.default_rng(seed)
    out: List[SyntheticFrame] = []
    tries = 0
    while len(out) < n and tries < 50 * n:
        tries += 1
        pose = random_pose(rng)
        fr = render(pose, rng=rng, **kw)
        real = [c for c in fr.gt['cruzamentos'] if not c['marca']]
        if len(real) < min_crossings:
            continue
        if variants:
            fr.image = perturb(fr.image, rng)
            fr.info['variante'] = True
        out.append(fr)
    return out
