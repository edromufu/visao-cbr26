"""Vista de cima do que o IPM projetou, para testar o pipeline sem RViz."""
import math

import cv2
import numpy as np

from .projection import pixels_to_ground

COLORS = {
    'ball': (0, 140, 255), 'goalpost': (0, 230, 255), 'robot': (255, 120, 0),
    'L': (255, 0, 255), 'T': (255, 0, 255), 'X': (255, 0, 255), 'line': (235, 235, 235),
}


class BirdsEye:

    def __init__(self, max_x=4.0, half_y=2.5, scale=100):
        self.max_x, self.half_y, self.scale = max_x, half_y, scale
        self.w = int(2 * half_y * scale)
        self.h = int((max_x + 0.3) * scale)

    def px(self, x, y):
        return int(round(self.w / 2 - y * self.scale)), int(round(self.h - 0.3 * self.scale - x * self.scale))

    def background(self):
        img = np.full((self.h, self.w, 3), (40, 90, 40), np.uint8)
        step = 0.5
        for i in range(0, int(self.max_x / step) + 1):
            x = i * step
            major = abs(x - round(x)) < 1e-6
            cv2.line(img, self.px(x, self.half_y), self.px(x, -self.half_y),
                     (90, 150, 90) if major else (60, 115, 60), 1)
            if major and x > 0:
                cv2.putText(img, f'{x:.0f} m', (self.px(x, 0)[0] + 4, self.px(x, 0)[1] - 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 210, 150), 1, cv2.LINE_AA)
        for j in range(-int(self.half_y / step), int(self.half_y / step) + 1):
            y = j * step
            cv2.line(img, self.px(0, y), self.px(self.max_x, y), (60, 115, 60), 1)
        return img

    def draw(self, pose, intr, img_size, objects, line_points, header_lines):
        img = self.background()
        self.draw_fov(img, pose.footprint_camera, intr, img_size)
        for x, y in line_points:
            cv2.circle(img, self.px(x, y), 2, COLORS['line'], -1)
        cv2.circle(img, self.px(0, 0), 6, (255, 255, 255), 2)
        cv2.arrowedLine(img, self.px(0, 0), self.px(0.25, 0), (255, 255, 255), 2, tipLength=0.3)
        for label, (x, y) in objects:
            p = self.px(x, y)
            color = COLORS.get(label, (200, 200, 200))
            if label == 'ball':
                cv2.circle(img, p, max(3, int(0.07 * self.scale)), color, -1)
                cv2.putText(img, f'({x:.2f}, {y:.2f}) d={math.hypot(x, y):.2f}', (p[0] + 8, p[1] + 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
            elif label in ('goalpost', 'robot'):
                cv2.rectangle(img, (p[0] - 5, p[1] - 5), (p[0] + 5, p[1] + 5), color, -1)
                cv2.putText(img, f'd={math.hypot(x, y):.2f}', (p[0] + 8, p[1] + 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA)
            else:
                cv2.putText(img, label, (p[0] - 5, p[1] + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2, cv2.LINE_AA)
        for i, text in enumerate(header_lines):
            cv2.putText(img, text, (8, 18 + 18 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(img, text, (8, 18 + 18 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        return img

    def draw_fov(self, img, footprint_camera, intr, img_size):
        """Contorno da área do chão vista pela câmera (borda da imagem projetada)."""
        w, h = img_size
        n = 20
        u = np.concatenate([np.linspace(0, w, n), np.full(n, w), np.linspace(w, 0, n), np.zeros(n)])
        v = np.concatenate([np.full(n, h), np.linspace(h, 0, n), np.zeros(n), np.linspace(0, h, n)])
        pts = pixels_to_ground(footprint_camera, intr, u, v)
        pts = pts[~np.isnan(pts[:, 0])]
        far = 2 * self.max_x
        pts = pts[np.hypot(pts[:, 0], pts[:, 1]) < far]
        if len(pts) >= 3:
            poly = np.array([self.px(x, y) for x, y in pts], np.int32)
            hull = cv2.convexHull(poly)
            overlay = img.copy()
            cv2.fillPoly(overlay, [hull], (70, 130, 70))
            cv2.addWeighted(overlay, 0.5, img, 0.5, 0, img)
            cv2.polylines(img, [hull], True, (120, 200, 120), 1, cv2.LINE_AA)
