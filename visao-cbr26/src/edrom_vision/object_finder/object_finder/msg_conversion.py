"""
Conversão dos resultados do núcleo para mensagens ROS 2.

Funções puras: recebem os *módulos* de mensagem como argumento (``sv2d`` =
``soccer_vision_2d_msgs.msg``, ``vm`` = ``vision_msgs.msg``, ``attr`` =
``soccer_vision_attribute_msgs.msg``, ``img`` = ``sensor_msgs.msg``,
``sv3d`` = ``soccer_vision_3d_msgs.msg``, ``geo`` = ``geometry_msgs.msg``), o que
permite testá-las sem ROS (com classes falsas).
"""

from __future__ import annotations

import math
from typing import Any, Dict, Iterable, Optional, Sequence

import numpy as np

from .features import CrossingFeature, Detection, EllipseFeature, LineFeature

NUM_RAYS = {'L': 2, 'T': 3, 'X': 4}


def _point(vm: Any, x: float, y: float) -> Any:
    p = vm.Point2D()
    p.x, p.y = float(x), float(y)
    return p


def _bbox(vm: Any, x: float, y: float, w: float, h: float, theta: float = 0.0) -> Any:
    b = vm.BoundingBox2D()
    b.center.position.x = float(x)
    b.center.position.y = float(y)
    b.center.theta = float(theta)
    b.size_x = float(w)
    b.size_y = float(h)
    return b


def _conf(attr: Any, c: float) -> Any:
    k = attr.Confidence()
    k.confidence = float(c)
    return k


def detections_to_msgs(dets: Sequence[Detection], header: Any, sv2d: Any, vm: Any, attr: Any) -> Dict[str, Any]:
    """Bola, traves e robôs (aceitos) — nomes de classe, nunca números."""
    balls = sv2d.BallArray(header=header)
    posts = sv2d.GoalpostArray(header=header)
    robots = sv2d.RobotArray(header=header)
    for d in dets:
        if d.rejeitada:
            continue
        if d.classe == 'ball':
            b = sv2d.Ball()
            b.bb = _bbox(vm, d.x, d.y, d.w, d.h)
            b.center = _point(vm, d.x, d.y)
            b.confidence = _conf(attr, d.conf)
            balls.balls.append(b)
        elif d.classe == 'goalpost':
            g = sv2d.Goalpost()
            g.bb = _bbox(vm, d.x, d.y, d.w, d.h)
            g.confidence = _conf(attr, d.conf)
            posts.posts.append(g)
        elif d.classe == 'robot':
            r = sv2d.Robot()
            r.bb = _bbox(vm, d.x, d.y, d.w, d.h)
            r.confidence = _conf(attr, d.conf)
            robots.robots.append(r)
    return {'balls': balls, 'goalposts': posts, 'robots': robots}


def markings_to_msg(crossings: Iterable[CrossingFeature], lines: Iterable[LineFeature],
                    ellipses: Iterable[EllipseFeature], header: Any, sv2d: Any, vm: Any, attr: Any) -> Any:
    """``MarkingArray`` com interseções (com ``heading_rays``), segmentos e elipses."""
    m = sv2d.MarkingArray(header=header)
    for c in crossings:
        it = sv2d.MarkingIntersection()
        it.center = _point(vm, c.x, c.y)
        it.num_rays = int(NUM_RAYS.get(c.tipo, len(c.heading_rays)))
        it.heading_rays = [float(a) for a in c.heading_rays]  # vazio se só o YOLO viu
        it.confidence = _conf(attr, c.confianca)
        m.intersections.append(it)
    for ln in lines:
        s = sv2d.MarkingSegment()
        s.start = _point(vm, ln.x1, ln.y1)
        s.end = _point(vm, ln.x2, ln.y2)
        s.confidence = _conf(attr, ln.confianca)
        m.segments.append(s)
    for e in ellipses:
        el = sv2d.MarkingEllipse()
        el.bb = _bbox(vm, e.cx, e.cy, e.eixo_maior, e.eixo_menor, math.radians(e.angulo_graus))
        el.center = _point(vm, e.cx, e.cy)
        el.confidence = _conf(attr, e.confianca)
        m.ellipses.append(el)
    return m


def field_boundary_to_msg(points: np.ndarray, detected: bool, header: Any, sv2d: Any, vm: Any, attr: Any) -> Any:
    """``FieldBoundary`` em pixels da imagem."""
    fb = sv2d.FieldBoundary(header=header)
    for x, y in (points if detected else []):
        fb.points.append(_point(vm, x, y))
    fb.confidence = _conf(attr, 1.0 if detected else 0.0)
    return fb


def bgr_to_image_msg(frame: np.ndarray, header: Any, img_mod: Any) -> Any:
    """``sensor_msgs/Image`` bgr8 sem cv_bridge."""
    msg = img_mod.Image()
    msg.header = header
    msg.height, msg.width = int(frame.shape[0]), int(frame.shape[1])
    msg.encoding = 'bgr8'
    msg.is_bigendian = 0
    msg.step = int(frame.shape[1] * 3)
    msg.data = np.ascontiguousarray(frame, dtype=np.uint8).tobytes()
    return msg


def projection_to_msg(crossings: Iterable[CrossingFeature], lines: Iterable[LineFeature], camera: Any,
                      header: Any, sv3d: Any, geo: Any, attr: Any, ray_px: float = 20.0) -> Any:
    """
    Projeção ao chão própria (sem IPM) em ``soccer_vision_3d_msgs/MarkingArray``.

    Referencial do robô no chão, sob a câmera (``camera_model``): ``x`` à frente,
    ``y`` à esquerda, metros. Cruzamentos: ``center`` vem da distância/ângulo
    já calculados pelo pipeline; ``rays`` são os ``heading_rays`` levados ao
    chão (vetores unitários; vazio se o YOLO viu sozinho ou se não projeta).
    Segmentos: extremos projetados. Só entra o que tem projeção.
    """
    m = sv3d.MarkingArray(header=header)
    if camera is None or not camera.can_project:
        return m
    for c in crossings:
        if c.distancia_m is None or c.angulo_rad is None:
            continue
        it = sv3d.MarkingIntersection()
        it.center = geo.Point(x=float(c.distancia_m * math.cos(c.angulo_rad)),
                              y=float(c.distancia_m * math.sin(c.angulo_rad)), z=0.0)
        it.num_rays = int(NUM_RAYS.get(c.tipo, len(c.heading_rays)))
        p0 = camera.image_to_ground(c.x, c.y)
        rays = []
        for a in c.heading_rays:
            q = camera.image_to_ground(c.x + ray_px * math.cos(a), c.y + ray_px * math.sin(a))
            if p0 is None or q is None:
                rays = []
                break
            dx, dy = q[0] - p0[0], q[1] - p0[1]
            n = math.hypot(dx, dy)
            if n < 1e-9:
                rays = []
                break
            rays.append(geo.Vector3(x=dx / n, y=dy / n, z=0.0))
        it.rays = rays
        it.confidence = _conf(attr, c.confianca)
        m.intersections.append(it)
    for ln in lines:
        a = camera.image_to_ground(ln.x1, ln.y1)
        b = camera.image_to_ground(ln.x2, ln.y2)
        if a is None or b is None:
            continue
        s = sv3d.MarkingSegment()
        s.start = geo.Point(x=float(a[0]), y=float(a[1]), z=0.0)
        s.end = geo.Point(x=float(b[0]), y=float(b[1]), z=0.0)
        s.confidence = _conf(attr, ln.confianca)
        m.segments.append(s)
    return m


def camera_info_to_model(info: Any, height: Optional[float], pitch: float) -> Any:
    """``sensor_msgs/CameraInfo`` -> :class:`CameraModel`."""
    from .camera_model import CameraModel
    K = list(info.k) if hasattr(info, 'k') else list(info.K)
    D = list(info.d) if hasattr(info, 'd') else list(getattr(info, 'D', []))
    return CameraModel(K[0], K[4], K[2], K[5], height, pitch, np.array(D) if D else None, nome='camera_info')
