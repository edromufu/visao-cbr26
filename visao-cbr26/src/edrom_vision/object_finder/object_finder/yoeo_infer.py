"""Inferência do YOEO-26n com OpenVINO. Depende só de numpy, opencv e openvino, para rodar no robô.

    from yoeo_infer import YOEOInfer
    net = YOEOInfer("yoeo26n_416x320_int8.xml", device="GPU")
    out = net(frame_bgr)        # out.boxes, out.scores, out.classes (pixels do frame), out.mask (1/4 da entrada)

Este arquivo é copiado como está para o pacote ROS e para o pacote de benchmark do N100.
"""
import time
from dataclasses import dataclass, field

import cv2
import numpy as np

DET_NAMES = ("ball", "goalpost", "robot", "L-Intersection", "T-Intersection", "X-Intersection")
DET_NAMES_V1 = DET_NAMES[:3]     # modelos exportados antes dos cruzamentos não guardam os nomes no .xml
COLORS = {0: (0, 140, 255), 1: (0, 230, 255), 2: (255, 120, 0), 3: (0, 0, 255), 4: (255, 255, 0), 5: (255, 0, 180)}
SEG_NAMES = ("background", "field", "lines")
PAD = 114


@dataclass
class Result:
    boxes: np.ndarray        # [N,4] x1 y1 x2 y2 em pixels do frame original
    scores: np.ndarray       # [N]
    classes: np.ndarray      # [N] int: 0 ball, 1 goalpost, 2 robot, 3 L, 4 T, 5 X (ver YOEOInfer.names)
    mask: np.ndarray         # [H/4, W/4] uint8 da entrada da rede: 0 background, 1 field, 2 lines, 255 borda
    scale: float             # entrada da rede = frame * scale + (dx, dy)
    pad: tuple
    times_ms: dict = field(default_factory=dict)

    def mask_on_frame(self, frame_shape):
        """Máscara reamostrada para o tamanho do frame original (vizinho mais próximo)."""
        h, w = frame_shape[:2]
        dx, dy = self.pad
        k = self.scale / 4
        x0, y0 = int(round(dx / 4)), int(round(dy / 4))
        crop = self.mask[y0:y0 + int(round(h * k)), x0:x0 + int(round(w * k))]
        return cv2.resize(crop, (w, h), interpolation=cv2.INTER_NEAREST)


class YOEOInfer:
    def __init__(self, model_xml, device="CPU", threads=0, conf=0.25, class_conf=None, max_det=50, cache_dir=None):
        import openvino as ov
        core = ov.Core()
        if cache_dir:
            core.set_property({"CACHE_DIR": str(cache_dir)})     # compila a iGPU uma vez só
        config = {"PERFORMANCE_HINT": "LATENCY"}
        if threads and device == "CPU":
            config["INFERENCE_NUM_THREADS"] = int(threads)
        model = core.read_model(str(model_xml))
        _, _, self.h, self.w = model.inputs[0].get_partial_shape().to_shape()
        self.compiled = core.compile_model(model, device, config)
        self.request = self.compiled.create_infer_request()
        self.out_boxes = self.compiled.output("boxes")
        self.out_seg = self.compiled.output("seg_logits")
        self.names = model_names(model)
        self.conf = np.array([(class_conf or {}).get(n, conf) for n in self.names], np.float32)
        self.max_det = max_det
        self.device = device

    def preprocess(self, frame):
        """Letterbox para a entrada da rede. Igual ao usado no treino (scripts/train.py)."""
        h, w = frame.shape[:2]
        k = min(self.w / w, self.h / h)
        nw, nh = round(w * k), round(h * k)
        dx, dy = (self.w - nw) // 2, (self.h - nh) // 2
        canvas = np.full((self.h, self.w, 3), PAD, np.uint8)
        canvas[dy:dy + nh, dx:dx + nw] = cv2.resize(frame, (nw, nh),
                                                    interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_LINEAR)
        blob = canvas[..., ::-1].transpose(2, 0, 1)[None].astype(np.float32) * (1 / 255)
        return np.ascontiguousarray(blob), k, (dx, dy)

    def postprocess(self, det, seg, k, pad, frame_shape):
        det = det[0]
        keep = det[:, 4] >= self.conf[det[:, 5].astype(np.int64)]
        det = det[keep][: self.max_det]
        boxes = (det[:, :4] - np.array([pad[0], pad[1], pad[0], pad[1]], np.float32)) / k
        h, w = frame_shape[:2]
        boxes[:, [0, 2]] = boxes[:, [0, 2]].clip(0, w)
        boxes[:, [1, 3]] = boxes[:, [1, 3]].clip(0, h)
        mask = seg[0].argmax(0).astype(np.uint8)
        dx, dy = pad
        x0, y0 = dx // 4, dy // 4
        x1, y1 = (self.w - dx) // 4, (self.h - dy) // 4
        border = np.full_like(mask, 255)
        border[y0:y1, x0:x1] = mask[y0:y1, x0:x1]
        return Result(boxes, det[:, 4].copy(), det[:, 5].astype(np.int64), border, k, pad)

    def __call__(self, frame):
        t0 = time.perf_counter()
        blob, k, pad = self.preprocess(frame)
        t1 = time.perf_counter()
        self.request.infer({0: blob})
        det = self.request.get_tensor(self.out_boxes).data
        seg = self.request.get_tensor(self.out_seg).data
        t2 = time.perf_counter()
        res = self.postprocess(det, seg, k, pad, frame.shape)
        t3 = time.perf_counter()
        res.times_ms = {"pre": (t1 - t0) * 1e3, "infer": (t2 - t1) * 1e3, "post": (t3 - t2) * 1e3,
                        "total": (t3 - t0) * 1e3}
        return res


def model_names(model):
    """Nomes das classes gravados no .xml pelo export (rt_info yoeo/det_names)."""
    if model.has_rt_info(["yoeo", "det_names"]):
        return tuple(model.get_rt_info(["yoeo", "det_names"]).astype(str).split(","))
    return DET_NAMES_V1


def draw(frame, res, alpha=0.35, names=DET_NAMES):
    """Desenha máscara (campo verde, linhas magenta) e caixas no frame. Para depuração."""
    colors = COLORS
    vis = frame.copy()
    m = res.mask_on_frame(frame.shape)
    vis[m == 1] = ((1 - alpha) * vis[m == 1] + alpha * np.array((60, 180, 60))).astype(np.uint8)
    vis[m == 2] = (255, 0, 255)
    for (x0, y0, x1, y1), s, c in zip(res.boxes, res.scores, res.classes):
        cv2.rectangle(vis, (int(x0), int(y0)), (int(x1), int(y1)), colors[int(c)], 2)
        cv2.putText(vis, f"{names[int(c)]} {s:.2f}", (int(x0), max(12, int(y0) - 4)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[int(c)], 1)
    return vis
