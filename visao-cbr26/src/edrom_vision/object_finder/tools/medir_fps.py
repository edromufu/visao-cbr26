"""
Mede o tempo por frame do pipeline (sem e com YOLO) em 1080x720 e 640x480.

Uso: python3 tools/medir_fps.py --kit <kit_visao> [--modelo modelo/best.pt] [-n 20]
"""

import argparse
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from object_finder.detector import make_detector  # noqa: E402
from object_finder.pipeline import LineVisionPipeline  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--kit', required=True)
    ap.add_argument('--modelo', default='')
    ap.add_argument('-n', type=int, default=20)
    a = ap.parse_args()
    imgs = {}
    for nome, rel in (('frame_webots', 'frame_webots.png'), ('image_2', 'frames_gt/image_2.png')):
        src = cv2.imread(str(Path(a.kit) / rel))
        for w, h in ((1080, 720), (640, 480)):
            imgs[f'{nome}@{w}x{h}'] = cv2.resize(src, (w, h), interpolation=cv2.INTER_AREA)
    det = make_detector(a.modelo) if a.modelo else None
    out = {}
    for name, img in imgs.items():
        pipe = LineVisionPipeline(detector=det)
        pipe.process(img)  # aquecimento
        ts = []
        parts = []
        for _ in range(a.n):
            t = time.perf_counter()
            r = pipe.process(img)
            ts.append((time.perf_counter() - t) * 1e3)
            parts.append(r.timings_ms)
        med = float(np.median(ts))
        out[name] = {'mediana_ms': round(med, 1), 'fps': round(1000.0 / med, 1),
                     'etapas_ms': {k: round(float(np.median([p[k] for p in parts])), 1) for k in parts[0]}}
    print(json.dumps({'modelo': a.modelo or 'sem_yolo', **out}, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
