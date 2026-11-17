"""
Utilidades de teste: esqueletos construídos à mão, pelo mesmo caminho real.

As linhas são desenhadas em resolução cheia, reduzidas à grade 1/8 com
INTER_AREA (como o ``white_mask_resized`` original), suavizadas com o mesmo
GaussianBlur 5x5 e esqueletizadas pelo mesmo operador de ranking.
"""

from types import SimpleNamespace

import cv2
import numpy as np

from robocup_line_vision.stage1_adapter import ranking_count


def grid_from_strokes(strokes, grid_shape=(60, 80), width_px=6, circles=(), blobs=(), scale=8):
    """
    Monta um ``Stage1Result`` mínimo a partir de traços em coordenadas da grade.

    ``strokes``: lista de ((x0, y0), (x1, y1)) em células; ``circles``: lista de
    ((cx, cy), raio) em células; ``blobs``: lista de ((cx, cy), raio_px).
    """
    gh, gw = grid_shape
    H, W = gh * scale, gw * scale
    full = np.zeros((H, W), np.uint8)
    for (p, q) in strokes:
        cv2.line(full, (int((p[0] + 0.5) * scale), int((p[1] + 0.5) * scale)),
                 (int((q[0] + 0.5) * scale), int((q[1] + 0.5) * scale)), 255, width_px)
    for (c, r) in circles:
        cv2.circle(full, (int((c[0] + 0.5) * scale),
                   int((c[1] + 0.5) * scale)), int(r * scale), 255, width_px)
    for (c, r) in blobs:
        cv2.circle(full, (int((c[0] + 0.5) * scale), int((c[1] + 0.5) * scale)), int(r), 255, -1)
    white_resized = cv2.resize(full, (gw, gh), interpolation=cv2.INTER_AREA).astype(np.float32)
    green_resized = (255.0 - white_resized).astype(np.float32)
    field = np.full((gh, gw), 255, np.uint8)
    flm = cv2.bitwise_and(white_resized.astype(np.uint8), field)
    relief = cv2.GaussianBlur(flm, (5, 5), 0)
    c = ranking_count(relief)
    skel = (relief > 0) & (c < 3)
    skel[0, :] = skel[-1, :] = skel[:, 0] = skel[:, -1] = False
    return SimpleNamespace(
        image_shape=(H, W), grid_shape=(gh, gw), scale=(float(scale), float(scale)),
        white_mask=full, green_mask=255 - full, white_resized=white_resized,
        green_resized=green_resized, field_mask=field, field_mask_full=np.full(
            (H, W), 255, np.uint8),
        field_detected=True, relief=relief, skeleton=skel,
        grid_to_image=lambda gx, gy: ((gx + 0.5) * scale, (gy + 0.5) * scale),
        image_to_grid=lambda x, y: (x / scale - 0.5, y / scale - 0.5))


def angle_close(a, b, tol_deg):
    """Ângulos (rad) próximos módulo 2π."""
    d = (a - b + np.pi) % (2 * np.pi) - np.pi
    return abs(d) <= np.deg2rad(tol_deg)
