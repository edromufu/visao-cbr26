"""
Interface do detector (YOLO) e implementações.

* :class:`NullDetector` — roda sem YOLO (``--sem-yolo``);
* :class:`UltralyticsDetector` — ``best.pt`` (ou ``.onnx``) pelo ``ultralytics``,
  com os mesmos parâmetros do nó finder (``imgsz=320, conf=0.45, iou=0.5,
  max_det=10``);
* :class:`OnnxDetector` — só ``onnxruntime`` + numpy (sem torch): útil no
  NUC. Lê os nomes das classes dos metadados do ONNX exportado pelo
  ultralytics.

As classes são sempre tratadas **pelo nome** (``Detection.classe``).
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, List, Optional, Protocol, Sequence

import cv2
import numpy as np

from .features import Detection

DEFAULT_NAMES = {0: 'ball', 1: 'goalpost', 2: 'robot', 3: 'L-Intersection',
                 4: 'T-Intersection', 5: 'X-Intersection', 6: 'crossbar'}


class Detector(Protocol):
    """Contrato: ``detect(frame_bgr) -> lista de Detection``."""

    names: Dict[int, str]

    def detect(self, frame_bgr: np.ndarray) -> List[Detection]:
        """Detecta objetos num frame BGR."""


class NullDetector:
    """Detector vazio (segmentação pura)."""

    names: Dict[int, str] = dict(DEFAULT_NAMES)

    def detect(self, frame_bgr: np.ndarray) -> List[Detection]:
        """Sempre vazio."""
        return []


class UltralyticsDetector:
    """YOLO via ``ultralytics`` (``.pt`` ou ``.onnx``)."""

    def __init__(self, model_path: str, imgsz: int = 320, conf: float = 0.45, iou: float = 0.5,
                 max_det: int = 10, device: Optional[str] = None) -> None:
        from ultralytics import YOLO  # importação tardia: só quem usa precisa
        self.model = YOLO(str(model_path))
        self.names = {int(k): str(v) for k, v in self.model.names.items()}
        self.imgsz, self.conf, self.iou, self.max_det, self.device = imgsz, conf, iou, max_det, device

    def detect(self, frame_bgr: np.ndarray) -> List[Detection]:
        """Inferência com os parâmetros do nó finder."""
        kw = {'source': frame_bgr, 'conf': self.conf, 'imgsz': self.imgsz, 'max_det': self.max_det,
              'iou': self.iou, 'verbose': False}
        if self.device:
            kw['device'] = self.device
        r = self.model.predict(**kw)[0]
        out = []
        for c, s, b in zip(r.boxes.cls.tolist(), r.boxes.conf.tolist(), r.boxes.xywh.tolist()):
            ci = int(c)
            out.append(Detection(self.names.get(ci, str(ci)), ci, float(s), *map(float, b)))
        return out


class OnnxDetector:
    """
    YOLOv8 exportado para ONNX, decodificado com numpy (sem torch).

    Saída esperada ``(1, 4 + nc, N)`` (ultralytics, ``nms=False``).
    Pré-processamento: letterbox para ``imgsz`` com cinza 114, RGB, /255.
    """

    def __init__(self, model_path: str, imgsz: Optional[int] = None, conf: float = 0.45,
                 iou: float = 0.5, max_det: int = 10, names: Optional[Dict[int, str]] = None) -> None:
        import onnxruntime as ort
        self.sess = ort.InferenceSession(str(model_path), providers=['CPUExecutionProvider'])
        meta = self.sess.get_modelmeta().custom_metadata_map
        self.names = names or ({int(k): v for k, v in ast.literal_eval(meta['names']).items()}
                               if 'names' in meta else dict(DEFAULT_NAMES))
        shape = self.sess.get_inputs()[0].shape
        self.imgsz = imgsz or (int(shape[2]) if isinstance(shape[2], int) else 320)
        self.input_name = self.sess.get_inputs()[0].name
        self.conf, self.iou, self.max_det = conf, iou, max_det

    def _letterbox(self, img: np.ndarray):
        h, w = img.shape[:2]
        s = min(self.imgsz / h, self.imgsz / w)
        nh, nw = int(round(h * s)), int(round(w * s))
        top = (self.imgsz - nh) // 2
        left = (self.imgsz - nw) // 2
        canvas = np.full((self.imgsz, self.imgsz, 3), 114, np.uint8)
        canvas[top:top + nh, left:left + nw] = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)
        return canvas, s, left, top

    def detect(self, frame_bgr: np.ndarray) -> List[Detection]:
        """Inferência + NMS por classe."""
        img, s, left, top = self._letterbox(frame_bgr)
        x = img[..., ::-1].transpose(2, 0, 1)[None].astype(np.float32) / 255.0
        y = self.sess.run(None, {self.input_name: np.ascontiguousarray(x)})[0][0]  # (4+nc, N)
        boxes, scores = y[:4].T, y[4:].T
        cls = scores.argmax(1)
        conf = scores[np.arange(len(cls)), cls]
        keep = conf >= self.conf
        boxes, cls, conf = boxes[keep], cls[keep], conf[keep]
        if not len(conf):
            return []
        b = boxes.copy()
        b[:, 0] = (b[:, 0] - left) / s
        b[:, 1] = (b[:, 1] - top) / s
        b[:, 2] /= s
        b[:, 3] /= s
        out: List[Detection] = []
        for c in np.unique(cls):
            idx = np.nonzero(cls == c)[0]
            rects = [[float(b[i, 0] - b[i, 2] / 2), float(b[i, 1] - b[i, 3] / 2), float(b[i, 2]), float(b[i, 3])]
                     for i in idx]
            kept = cv2.dnn.NMSBoxes(rects, conf[idx].astype(float).tolist(), self.conf, self.iou)
            for k in np.array(kept).reshape(-1):
                i = idx[int(k)]
                out.append(Detection(self.names.get(int(c), str(int(c))), int(c), float(conf[i]),
                                     float(b[i, 0]), float(b[i, 1]), float(b[i, 2]), float(b[i, 3])))
        out.sort(key=lambda d: -d.conf)
        return out[:self.max_det]


def make_detector(model_path: Optional[str], backend: str = 'auto', **kw) -> 'Detector':
    """Fábrica: ``None``/'' -> :class:`NullDetector`; ``.onnx`` sem ultralytics -> ONNX."""
    if not model_path:
        return NullDetector()
    p = Path(model_path)
    if not p.is_file():
        raise FileNotFoundError(f'modelo não encontrado: {p}')
    if backend == 'onnx' or (backend == 'auto' and p.suffix == '.onnx' and not _has_ultralytics()):
        return OnnxDetector(str(p), **{k: v for k, v in kw.items() if k in ('imgsz', 'conf', 'iou', 'max_det')})
    return UltralyticsDetector(str(p), **kw)


def _has_ultralytics() -> bool:
    try:
        import ultralytics  # noqa: F401
        return True
    except ImportError:
        return False


def classes_by_name(dets: Sequence[Detection], name: str) -> List[Detection]:
    """Filtra por nome de classe."""
    return [d for d in dets if d.classe == name]
