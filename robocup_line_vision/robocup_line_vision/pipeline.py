"""Pipeline completo: etapa 1 -> (máscara YOLO) -> III-C -> IV-A -> IV-B -> fusão."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

import numpy as np

from .camera_model import CameraModel
from .crossings import combine_crossings, crossings_from_lines, detect_crossings, keynode_graph
from .detector import Detector, NullDetector
from .features import CrossingFeature, Detection, EllipseFeature, LineFeature
from .fusion import fuse, mask_boxes
from .graph_nodes import build_graph, NodeGraph
from .lines import extract_lines, point_on_ellipses
from .params import Params
from .stage1_adapter import DEFAULT_GREEN_CSV, DEFAULT_WHITE_CSV, ranking_count, Stage1Result, Stage1Segmenter


@dataclass
class FrameResult:
    """Tudo o que sai de um frame."""

    stage1: Stage1Result
    graph: NodeGraph
    keygraph: Any
    crossings: List[CrossingFeature]
    lines: List[LineFeature]
    ellipses: List[EllipseFeature]
    detections: List[Detection]
    timings_ms: Dict[str, float] = field(default_factory=dict)
    info: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> Dict[str, Any]:
        """Resumo serializável (JSON)."""
        return {
            'campo_detectado': self.stage1.field_detected,
            'cruzamentos': [c.to_dict() for c in self.crossings],
            'linhas': [ln.to_dict() for ln in self.lines],
            'elipses': [e.to_dict() for e in self.ellipses],
            'deteccoes': [d.to_dict() for d in self.detections],
            'tempos_ms': self.timings_ms,
            'info': self.info,
        }


def camera_from_params(p: Params, image_size: Optional[tuple] = None) -> Optional[CameraModel]:
    """Modelo de câmera conforme ``camera.modelo``."""
    c = p.camera
    if c.modelo == 'fov':
        if image_size is None:
            return None
        return CameraModel.from_fov(image_size[0], image_size[1], c.hfov_rad, c.altura_m, c.pitch_rad)
    if c.modelo == 'edrom':
        if not c.camera_matrix:
            return None
        return CameraModel.from_edrom(Path(c.camera_matrix), Path(c.dist_coeffs) if c.dist_coeffs else None,
                                      Path(c.homography) if c.homography else None, c.altura_m, c.pitch_rad,
                                      scale_to=image_size, calib_size=(c.calib_largura, c.calib_altura))
    return None


class LineVisionPipeline:
    """Orquestra as etapas. Sem ROS; o nó ROS só chama :meth:`process`."""

    def __init__(self, params: Optional[Params] = None, green_csv: Optional[str] = None,
                 white_csv: Optional[str] = None, detector: Optional[Detector] = None,
                 camera: Optional[CameraModel] = None) -> None:
        self.p = params or Params()
        e1 = self.p.etapa1
        self.seg = Stage1Segmenter(green_csv or DEFAULT_GREEN_CSV, white_csv or DEFAULT_WHITE_CSV,
                                   tpix=e1.tpix, trow=e1.trow, twin=e1.twin)
        self.detector = detector or NullDetector()
        self.camera = camera
        self._camera_auto = camera is None

    @staticmethod
    def from_calibration_dir(calib_dir: str, params: Optional[Params] = None,
                             detector: Optional[Detector] = None,
                             camera: Optional[CameraModel] = None) -> 'LineVisionPipeline':
        """Usa ``green_pixels.csv`` e ``white_pixels.csv`` de uma pasta de calibração."""
        d = Path(calib_dir)
        return LineVisionPipeline(params, str(d / 'green_pixels.csv'), str(d / 'white_pixels.csv'),
                                  detector, camera)

    def process(self, frame_bgr: np.ndarray) -> FrameResult:
        """Processa um frame BGR."""
        t = {}
        t0 = time.perf_counter()
        dets = self.detector.detect(frame_bgr)
        t['yolo'] = (time.perf_counter() - t0) * 1e3
        if self._camera_auto and self.camera is None:
            self.camera = camera_from_params(self.p, (frame_bgr.shape[1], frame_bgr.shape[0]))
        t1 = time.perf_counter()
        # a fronteira do campo sai sem máscara; depois mascara o branco das caixas aceitas
        s1 = self.seg.process(frame_bgr)
        if dets:
            from .fusion import check_field
            checked = check_field(dets, s1, self.p.fusao)
            boxes = mask_boxes(checked, self.p.fusao)
            if boxes:
                s1 = self.seg.process(frame_bgr, mask_boxes=boxes)
        t['etapa1'] = (time.perf_counter() - t1) * 1e3
        t2 = time.perf_counter()
        c_xy = ranking_count(s1.relief)
        g = build_graph(s1.relief, s1.skeleton, self.p.grafo, c_xy)
        t['III-C'] = (time.perf_counter() - t2) * 1e3
        t3 = time.perf_counter()
        lines, ellipses = extract_lines(g, s1, self.p.linhas, self.camera)
        t['IV-B'] = (time.perf_counter() - t3) * 1e3
        t4 = time.perf_counter()
        kg = keynode_graph(g, s1, self.p.cruzamentos)
        on_e = point_on_ellipses(ellipses, self.p.saida.ellipse_tol_px) if ellipses else None
        crossings = detect_crossings(g, s1, self.p.cruzamentos, keygraph=kg, on_ellipse=on_e)
        if self.p.saida.cruzamentos_de_retas:
            from_lines = crossings_from_lines(
                lines, ellipses, s1, self.p.cruzamentos, self.p.cruzamentos_retas)
            crossings = combine_crossings(crossings, from_lines, s1, self.p.cruzamentos_retas)
        t['IV-A'] = (time.perf_counter() - t4) * 1e3
        t5 = time.perf_counter()
        fr = fuse(crossings, dets, s1, self.p.fusao)
        out = [c for c in fr.crossings if c.confianca >= self.p.saida.min_conf_cruzamento]
        if self.camera is not None and self.camera.can_project:
            for c in out:
                gp = self.camera.image_to_ground(c.x, c.y)
                if gp is not None:
                    c.distancia_m, c.angulo_rad = (round(v, 4) for v in CameraModel.polar(*gp))
        t['fusao'] = (time.perf_counter() - t5) * 1e3
        t['total'] = (time.perf_counter() - t0) * 1e3
        return FrameResult(s1, g, kg, out, lines, ellipses, fr.detections,
                           {k: round(v, 2) for k, v in t.items()}, fr.info)
