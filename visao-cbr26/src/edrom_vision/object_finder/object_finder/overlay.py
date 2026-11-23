"""Desenho de overlays (fronteira, esqueleto, nós, cruzamentos, linhas, YOLO)."""

from __future__ import annotations

from typing import Any, Iterable, Optional, Sequence, Tuple

import cv2
import numpy as np

COR_FRONTEIRA = (0, 255, 255)   # amarelo
COR_ESQUELETO = (0, 0, 255)     # vermelho
COR_VERDE = (0, 200, 0)
COR_BRANCO = (255, 0, 255)      # magenta (branco detectado)
COR_LINHA = (255, 128, 0)       # azul claro
COR_NO = (255, 255, 0)
COR_ARESTA = (180, 180, 0)
COR_TIPO = {'L': (0, 165, 255), 'T': (255, 0, 255), 'X': (0, 0, 255)}
COR_YOLO = {'ball': (0, 140, 255), 'goalpost': (255, 255, 255), 'robot': (255, 0, 0),
            'L-Intersection': (0, 165, 255), 'T-Intersection': (255, 0, 255),
            'X-Intersection': (0, 0, 255), 'crossbar': (200, 200, 200)}


def _text(img: np.ndarray, txt: str, org: Tuple[int, int], color=(255, 255, 255),
          scale: float = 0.55, thick: int = 1) -> None:
    """Texto com contorno preto (legível em qualquer fundo)."""
    cv2.putText(img, txt, org, cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), thick + 2, cv2.LINE_AA)
    cv2.putText(img, txt, org, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thick, cv2.LINE_AA)


def draw_text_block(img: np.ndarray, lines: Sequence[str], org: Tuple[int, int] = (8, 20),
                    color=(255, 255, 255), scale: float = 0.5, dy: int = 18,
                    colors: Optional[Sequence[Tuple[int, int, int]]] = None) -> None:
    """Várias linhas de texto a partir de ``org``."""
    x, y = org
    for i, ln in enumerate(lines):
        _text(img, ln, (x, y + i * dy), colors[i] if colors else color, scale)


def draw_stage1(img: np.ndarray, s1: Any, masks: bool = True, skeleton: bool = True,
                boundary: bool = True, alpha: float = 0.35) -> np.ndarray:
    """Overlay da etapa 1: verde/branco tingidos, fronteira e esqueleto."""
    out = img.copy()
    if masks:
        tint = out.copy()
        tint[s1.green_mask > 0] = COR_VERDE
        tint[s1.white_mask > 0] = COR_BRANCO
        out = cv2.addWeighted(out, 1 - alpha, tint, alpha, 0)
    if skeleton:
        sx, sy = s1.scale
        ys, xs = np.nonzero(s1.skeleton)
        for gx, gy in zip(xs, ys):
            x0, y0 = int(gx * sx), int(gy * sy)
            cv2.rectangle(out, (x0, y0), (int((gx + 1) * sx) - 1, int((gy + 1) * sy) - 1),
                          COR_ESQUELETO, -1)
    if boundary and s1.field_detected:
        pts = s1.boundary_image_points()
        if len(pts) >= 2:
            cv2.polylines(out, [np.round(pts).astype(np.int32).reshape(-1, 1, 2)], False,
                          COR_FRONTEIRA, 2, cv2.LINE_AA)
    return out


def mask_view(mask: np.ndarray, field_mask_full: Optional[np.ndarray] = None) -> np.ndarray:
    """Máscara em BGR; fora do campo fica escurecida."""
    v = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    if field_mask_full is not None:
        out = v.copy()
        out[field_mask_full == 0] = (out[field_mask_full == 0] * 0.35).astype(np.uint8)
        return out
    return v


def draw_graph(img: np.ndarray, graph: Any, s1: Any, node_radius: int = 2) -> None:
    """Desenha o grafo da III-C (nós e conexões) sobre a imagem."""
    for (a, b) in graph.edges():
        pa = s1.grid_to_image(*graph.pos[a])
        pb = s1.grid_to_image(*graph.pos[b])
        cv2.line(img, (int(pa[0]), int(pa[1])),
                 (int(pb[0]), int(pb[1])), COR_ARESTA, 1, cv2.LINE_AA)
    for n in graph.nodes():
        p = s1.grid_to_image(*graph.pos[n])
        cv2.circle(img, (int(p[0]), int(p[1])), node_radius, COR_NO, -1, cv2.LINE_AA)


def draw_crossings(img: np.ndarray, crossings: Iterable[Any], ray_len: int = 28) -> None:
    """Cruzamentos: tipo, raios de direção e confiança."""
    for c in crossings:
        col = COR_TIPO.get(c.tipo, (255, 255, 255))
        x, y = int(round(c.x)), int(round(c.y))
        for a in c.heading_rays:
            q = (int(x + ray_len * np.cos(a)), int(y + ray_len * np.sin(a)))
            cv2.arrowedLine(img, (x, y), q, col, 2, cv2.LINE_AA, tipLength=0.25)
        cv2.circle(img, (x, y), 7, col, 2, cv2.LINE_AA)
        _text(img, f'{c.tipo} {c.confianca:.2f}', (x + 8, y - 8), col, 0.5)


def draw_lines(img: np.ndarray, lines: Iterable[Any]) -> None:
    """Linhas do campo (IV-B)."""
    for ln in lines:
        cv2.line(img, (int(ln.x1), int(ln.y1)), (int(ln.x2), int(ln.y2)), COR_LINHA, 3, cv2.LINE_AA)


def draw_ellipses(img: np.ndarray, ellipses: Iterable[Any]) -> None:
    """Elipses (círculo central)."""
    for e in ellipses:
        cv2.ellipse(img, ((float(e.cx), float(e.cy)), (float(e.eixo_maior), float(e.eixo_menor)),
                          float(e.angulo_graus)), (0, 255, 128), 2, cv2.LINE_AA)


def draw_detections(img: np.ndarray, detections: Iterable[Any]) -> None:
    """Caixas do YOLO; rejeitadas em cinza tracejado com o motivo."""
    for d in detections:
        x0, y0 = int(d.x - d.w / 2), int(d.y - d.h / 2)
        x1, y1 = int(d.x + d.w / 2), int(d.y + d.h / 2)
        col = COR_YOLO.get(d.classe, (255, 255, 255)) if not d.rejeitada else (128, 128, 128)
        cv2.rectangle(img, (x0, y0), (x1, y1), col, 1 if d.rejeitada else 2)
        tag = f'{d.classe} {d.conf:.2f}' + (f' [{d.motivo}]' if d.rejeitada else '')
        _text(img, tag, (x0, max(12, y0 - 4)), col, 0.45)


def render_result(frame: np.ndarray, r: Any, fps: float, view: int = 0) -> np.ndarray:
    """Overlay completo: fronteira, esqueleto, nós, cruzamentos, linhas, YOLO e FPS."""
    if view == 2:
        out = frame.copy()
    elif view == 1:
        out = draw_stage1(frame, r.stage1)
    else:
        out = draw_stage1(frame, r.stage1, masks=False)
        draw_graph(out, r.graph, r.stage1)
        draw_lines(out, r.lines)
        draw_ellipses(out, r.ellipses)
        draw_detections(out, r.detections)
        draw_crossings(out, r.crossings)
    n = {t: sum(c.tipo == t for c in r.crossings) for t in 'LTX'}
    draw_text_block(out, [
        f'FPS {fps:5.1f} | total {r.timings_ms.get("total", 0):.0f} ms (yolo {r.timings_ms.get("yolo", 0):.0f})',
        f'campo {"SIM" if r.stage1.field_detected else "NAO"} | L {n["L"]} T {n["T"]} X {n["X"]} | '
        f'linhas {len(r.lines)} | elipses {len(r.ellipses)} | yolo {len(r.detections)}'
        + (f' | verde aprendido {r.info["verde_aprendido"]}' if 'verde_aprendido' in r.info else ''),
    ], (10, 22), scale=0.6, dy=24)
    return out
