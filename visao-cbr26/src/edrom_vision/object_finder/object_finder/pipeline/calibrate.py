r"""
calibrar  (= python3 -m object_finder.pipeline.calibrate)

Calibração de cor feita COM A CÂMERA DO ROBÔ, antes da partida. Sem ROS e sem detector: só numpy, OpenCV e
pandas. (Os intrínsecos da câmera são calibrados com o `camera_calibrator` e lidos pelo `usb_cam`.)

  hsv         faixas HSV do campo (verde), do branco (linhas), do vermelho e do azul
  snapshot    uma foto com grade, para escolher as regiões do `hsv` quando o robô não tem tela

Exemplos (--source: índice N de /dev/videoN, o próprio /dev/videoN, um vídeo ou uma imagem):
  calibrar hsv --source 2                      # interativo (precisa de tela): arraste sobre cada cor
  calibrar snapshot --source 2                 # sem tela: foto com grade para escolher as regiões
  calibrar hsv --source 2 --sample field=0.40,0.80,0.20,0.15 --sample white=0.1,0.7,0.1,0.02

Saídas (pasta --out, padrão `calibracao/`):
  hsv_params.yaml   parâmetros do nó `vision` (só as classes calibradas): vision.launch.py params_file:=<arquivo>
  hsv.csv           para `segmentar --hsv-csv`
  hsv_preview.png   máscaras e segmentação com as faixas novas: CONFIRA A OLHO antes de usar

A câmera abre com os padrões do `usb_cam.yaml` (640x480). Calibre com a MESMA resolução e as mesmas condições
(iluminação, exposição) da partida, e com a visão parada (a câmera USB só abre em um programa por vez).
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

import cv2
import numpy as np

from .color_common import DEFAULT_COLOR_SPACES, ColorSpaceHSV, build_color_detector, load_color_spaces_from_csv
from .main_pipeline import VisionPipeline, draw_pipeline_overlay

NODE_NAME = 'vision'                  # nome do nó no vision.launch.py: o YAML só vale se bater
CLASSES = ('field', 'white', 'red', 'blue')
DEFAULT_MARGIN = (6, 30, 40)          # folga (H, S, V) somada ao intervalo medido
DEFAULT_QUANTILES = (2.0, 98.0)       # percentis que descartam pixels fora da curva
PIXELS_PER_ADD = 4000                 # pixels sorteados de cada região/quadro (limita memória)
MIN_PIXELS = 2000                     # abaixo disso o resultado é pouco confiável
TINT_BGR = {'field': (0, 200, 0), 'white': (255, 255, 0), 'red': (0, 0, 255), 'blue': (255, 0, 0)}
GUI_WINDOW = 'calibracao HSV'

Roi = Tuple[float, float, float, float]   # x, y, largura, altura, em fração da imagem (0 a 1)


# --------------------------------------------------------------------------------------------------
# Cálculo das faixas (puro: sem câmera, sem janela)
# --------------------------------------------------------------------------------------------------

def hue_range(hues: Sequence[int], low_q: float, high_q: float, margin: int) -> Tuple[int, int]:
    """Faixa de matiz [h_min, h_max] (OpenCV, 0-179). Se for menor atravessando o 0/179, h_min > h_max."""
    h = np.asarray(hues, dtype=np.int32).ravel()
    d_lo, d_hi = np.percentile(h, [low_q, high_q])
    r_lo, r_hi = np.percentile((h + 90) % 180, [low_q, high_q])      # mesma conta com o círculo girado
    if (r_hi - r_lo) < (d_hi - d_lo):
        lo, hi = r_lo - margin, r_hi + margin
        if hi - lo >= 179:
            return 0, 179
        return int(round(lo - 90)) % 180, int(round(hi - 90)) % 180
    lo, hi = d_lo - margin, d_hi + margin
    return int(np.clip(round(lo), 0, 179)), int(np.clip(round(hi), 0, 179))


def space_from_pixels(pixels_hsv: np.ndarray, margin: Sequence[int] = DEFAULT_MARGIN,
                      quantiles: Sequence[float] = DEFAULT_QUANTILES, hue_free: bool = False) -> ColorSpaceHSV:
    """Faixa HSV que cobre os pixels amostrados (percentis + folga). `hue_free`: ignora o matiz (branco)."""
    px = np.asarray(pixels_hsv).reshape(-1, 3)
    if len(px) == 0:
        raise ValueError('nenhum pixel amostrado')
    lo_q, hi_q = quantiles
    h_min, h_max = (0, 179) if hue_free else hue_range(px[:, 0], lo_q, hi_q, int(margin[0]))
    s_lo, s_hi = np.percentile(px[:, 1], [lo_q, hi_q])
    v_lo, v_hi = np.percentile(px[:, 2], [lo_q, hi_q])

    def clip(value):
        return int(np.clip(round(float(value)), 0, 255))

    return ColorSpaceHSV(h_min, h_max, clip(s_lo - margin[1]), clip(s_hi + margin[1]),
                         clip(v_lo - margin[2]), clip(v_hi + margin[2]))


def coverage(space: ColorSpaceHSV, pixels_hsv: np.ndarray) -> float:
    """Fração dos pixels amostrados que cai dentro da faixa."""
    px = np.asarray(pixels_hsv, dtype=np.uint8).reshape(-1, 1, 3)
    return float(np.count_nonzero(space.mask_hsv(px))) / max(len(px), 1)


def check_samples(name: str, pixels_hsv: np.ndarray, space: ColorSpaceHSV) -> List[str]:
    """Avisos (texto) sobre amostras que provavelmente não representam a classe."""
    px = np.asarray(pixels_hsv).reshape(-1, 3)
    warnings = []
    if len(px) < MIN_PIXELS:
        warnings.append(f'{name}: só {len(px)} pixels amostrados (recomendado >= {MIN_PIXELS}); '
                        'aumente a região ou use mais quadros')
    median_h, median_s = np.median(px[:, 0]), np.median(px[:, 1])
    if name == 'field' and not 25 <= median_h <= 95:
        warnings.append(f'field: matiz mediano H={median_h:.0f} fora de 25-95; a região parece não ser grama')
    if name == 'white' and median_s > 80:
        warnings.append(f'white: saturação mediana S={median_s:.0f} alta; a região parece não ser branca')
    if name != 'white' and (space.s_max - space.s_min) > 200:
        warnings.append(f'{name}: saturação muito variada ({space.s_min}-{space.s_max}); '
                        'a região mistura cores ou tem reflexo')
    cov = coverage(space, px)
    if cov < 0.9:
        warnings.append(f'{name}: a faixa cobre só {cov:.0%} dos pixels amostrados; região heterogênea')
    return warnings


def parse_sample(text: str) -> Tuple[str, Roi]:
    """'field=0.4,0.8,0.2,0.15' -> ('field', (x, y, largura, altura)), frações da imagem."""
    try:
        name, numbers = text.split('=', 1)
        x, y, w, h = (float(v) for v in numbers.split(','))
    except ValueError:
        raise ValueError(f"--sample inválido: '{text}' (use CLASSE=x,y,largura,altura)") from None
    if name not in CLASSES:
        raise ValueError(f"classe '{name}' inválida; use uma de {', '.join(CLASSES)}")
    if not (0 <= x < 1 and 0 <= y < 1 and w > 0 and h > 0 and x + w <= 1.0001 and y + h <= 1.0001):
        raise ValueError(f"--sample '{text}': x, y, largura e altura devem ser frações da imagem (0 a 1) e a "
                         'região deve caber nela')
    return name, (x, y, w, h)


def roi_box(frame: np.ndarray, roi: Roi) -> Tuple[int, int, int, int]:
    """(x0, y0, x1, y1) em pixels, sempre com pelo menos 1 pixel."""
    height, width = frame.shape[:2]
    x0, y0 = int(roi[0] * width), int(roi[1] * height)
    x1 = min(width, max(x0 + 1, int((roi[0] + roi[2]) * width)))
    y1 = min(height, max(y0 + 1, int((roi[1] + roi[3]) * height)))
    return x0, y0, x1, y1


class Samples:
    """Pixels HSV acumulados por classe."""

    def __init__(self, seed: int = 0):
        self._data: Dict[str, List[np.ndarray]] = {c: [] for c in CLASSES}
        self._rng = np.random.default_rng(seed)

    def add_box(self, name: str, frame_bgr: np.ndarray, box: Tuple[int, int, int, int]) -> int:
        x0, y0, x1, y1 = box
        patch = cv2.cvtColor(frame_bgr[y0:y1, x0:x1], cv2.COLOR_BGR2HSV).reshape(-1, 3)
        if len(patch) > PIXELS_PER_ADD:
            patch = patch[self._rng.choice(len(patch), PIXELS_PER_ADD, replace=False)]
        self._data[name].append(patch)
        return len(patch)

    def get(self, name: str) -> np.ndarray:
        parts = self._data[name]
        return np.concatenate(parts) if parts else np.empty((0, 3), np.uint8)

    def count(self, name: str) -> int:
        return sum(len(p) for p in self._data[name])

    def clear(self, name: str) -> None:
        self._data[name] = []


def fit_spaces(samples: Samples, base: Dict[str, ColorSpaceHSV], margin: Sequence[int] = DEFAULT_MARGIN,
               quantiles: Sequence[float] = DEFAULT_QUANTILES) -> Tuple[Dict[str, ColorSpaceHSV], List[str], List[str]]:
    """(faixas, classes calibradas, avisos). Classes sem amostra mantêm a faixa de `base`."""
    spaces = dict(base)
    calibrated, warnings = [], []
    for name in CLASSES:
        pixels = samples.get(name)
        if len(pixels) == 0:
            continue
        spaces[name] = space_from_pixels(pixels, margin, quantiles, hue_free=(name == 'white'))
        calibrated.append(name)
        warnings += check_samples(name, pixels, spaces[name])
    spaces['marking'] = spaces['white']
    return spaces, calibrated, warnings


# --------------------------------------------------------------------------------------------------
# Saídas
# --------------------------------------------------------------------------------------------------

def spaces_to_csv(spaces: Dict[str, ColorSpaceHSV]) -> str:
    """CSV no formato de `load_color_spaces_from_csv` (`marking` = `white`)."""
    rows = ['classe,h_min,h_max,s_min,s_max,v_min,v_max']
    for name in ('field', 'marking', 'red', 'blue', 'white'):
        s = spaces['white' if name == 'marking' else name]
        rows.append(f'{name},{s.h_min},{s.h_max},{s.s_min},{s.s_max},{s.v_min},{s.v_max}')
    return '\n'.join(rows) + '\n'


def spaces_to_ros_yaml(spaces: Dict[str, ColorSpaceHSV], calibrated: Iterable[str]) -> str:
    """Arquivo de parâmetros do nó `vision` só com as classes calibradas (valores sempre inteiros)."""
    lines = ['# Gerado por `calibrar hsv`. Use: ros2 launch object_finder vision.launch.py params_file:=<este arquivo>',
             f'{NODE_NAME}:', '  ros__parameters:', '    hsv:']
    for name in calibrated:
        low, high = spaces[name].as_min_max()
        lines += [f'      {name}_min: {low}', f'      {name}_max: {high}']
    return '\n'.join(lines) + '\n'


def tint_mask(image: np.ndarray, mask: np.ndarray, color: Tuple[int, int, int], alpha: float = 0.55) -> None:
    painted = image.copy()
    painted[mask > 0] = color
    cv2.addWeighted(painted, alpha, image, 1 - alpha, 0, dst=image)


def make_preview(frame: np.ndarray, spaces: Dict[str, ColorSpaceHSV], calibrated: Sequence[str],
                 boxes: Sequence[Tuple[str, Tuple[int, int, int, int]]] = (), max_width: int = 1600) -> np.ndarray:
    """Esquerda: máscaras das classes calibradas e regiões amostradas. Direita: segmentação completa."""
    left = frame.copy()
    for name in calibrated:
        tint_mask(left, spaces[name].mask(frame), TINT_BGR[name])
    for name, (x0, y0, x1, y1) in boxes:
        cv2.rectangle(left, (x0, y0), (x1 - 1, y1 - 1), (0, 255, 255), 2)
        cv2.putText(left, name, (x0 + 4, max(14, y0 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    pipeline = VisionPipeline(build_color_detector(spaces), seed=0)
    right = draw_pipeline_overlay(frame, pipeline.run(frame))
    out = np.hstack([left, right])
    if out.shape[1] > max_width:
        out = cv2.resize(out, (max_width, int(out.shape[0] * max_width / out.shape[1])), interpolation=cv2.INTER_AREA)
    return out


def write_hsv_outputs(out_dir: Path, spaces: Dict[str, ColorSpaceHSV], calibrated: Sequence[str],
                      preview: Optional[np.ndarray]) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    files = [(out_dir / 'hsv.csv', spaces_to_csv(spaces)),
             (out_dir / 'hsv_params.yaml', spaces_to_ros_yaml(spaces, calibrated))]
    for path, text in files:
        path.write_text(text, encoding='utf-8')
    written = [p for p, _ in files]
    if preview is not None:
        cv2.imwrite(str(out_dir / 'hsv_preview.png'), preview)
        written.append(out_dir / 'hsv_preview.png')
    return written


def print_spaces(spaces: Dict[str, ColorSpaceHSV], calibrated: Sequence[str]) -> None:
    for name in CLASSES:
        s = spaces[name]
        origin = 'calibrado' if name in calibrated else 'NÃO calibrado; no ROS vale o padrão do nó'
        print(f'  {name:5s} H {s.h_min:3d}-{s.h_max:3d}  S {s.s_min:3d}-{s.s_max:3d}  '
              f'V {s.v_min:3d}-{s.v_max:3d}  [{origin}]')


# --------------------------------------------------------------------------------------------------
# Câmera
# --------------------------------------------------------------------------------------------------

def is_image(source: str) -> bool:
    return Path(source).suffix.lower() in {'.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'}


def camera_index(source: str) -> Optional[int]:
    """'2' ou '/dev/video2' -> 2; vídeo ou outro caminho -> None."""
    name = source[len('/dev/video'):] if source.startswith('/dev/video') else source
    return int(name) if name.isdigit() else None


def open_camera(source: str, width: int = 640, height: int = 480, fourcc: str = '') -> cv2.VideoCapture:
    """Abre /dev/video<N> (ou um arquivo de vídeo) com os padrões do `usb_cam.yaml`."""
    index = camera_index(source)
    if index is not None:
        cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
        if not cap.isOpened():
            cap = cv2.VideoCapture(index)
    else:
        cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"não foi possível abrir a fonte '{source}' (câmera inexistente, sem permissão no grupo "
                           "'video' ou em uso por outro programa, como o vision.launch rodando?)")
    if index is not None:
        if len(fourcc) == 4:
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap


def grab_frames(source: str, count: int, skip: int, args: argparse.Namespace) -> Iterator[np.ndarray]:
    """`count` quadros BGR depois de descartar `skip` (a exposição automática precisa estabilizar)."""
    if is_image(source):
        image = cv2.imread(source)
        if image is None:
            raise RuntimeError(f"não foi possível ler a imagem '{source}'")
        yield image
        return
    cap = open_camera(source, args.width, args.height, args.fourcc)
    try:
        delivered, failures = 0, 0
        total = skip + count
        for index in range(total):
            ok, frame = cap.read()
            if not ok:
                failures += 1
                if failures > 30:
                    raise RuntimeError('a câmera parou de entregar quadros')
                continue
            if index >= skip:
                delivered += 1
                yield frame
        if delivered == 0:
            raise RuntimeError('nenhum quadro recebido da câmera')
    finally:
        cap.release()


def draw_grid(frame: np.ndarray) -> np.ndarray:
    """Grade de 10% com as frações escritas (para escolher --sample sem tela)."""
    out = frame.copy()
    height, width = out.shape[:2]
    for i in range(1, 10):
        x, y = int(width * i / 10), int(height * i / 10)
        cv2.line(out, (x, 0), (x, height), (0, 255, 255), 1)
        cv2.line(out, (0, y), (width, y), (0, 255, 255), 1)
        cv2.putText(out, f'{i / 10:.1f}', (x + 3, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        cv2.putText(out, f'{i / 10:.1f}', (3, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    return out


# --------------------------------------------------------------------------------------------------
# Comandos
# --------------------------------------------------------------------------------------------------

def load_base(args: argparse.Namespace) -> Dict[str, ColorSpaceHSV]:
    base = load_color_spaces_from_csv(str(args.base)) if args.base else dict(DEFAULT_COLOR_SPACES)
    base['marking'] = base.get('marking', base['white'])
    return base


def cmd_snapshot(args: argparse.Namespace) -> int:
    frame = next(grab_frames(args.source, 1, args.skip, args))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out / 'snapshot.png'), frame)
    cv2.imwrite(str(out / 'snapshot_grade.png'), draw_grid(frame))
    print(f'gravado: {out / "snapshot_grade.png"} (grade em frações) e {out / "snapshot.png"}')
    print('Escolha as regiões olhando a grade e use: --sample CLASSE=x,y,largura,altura')
    return 0


def cmd_hsv(args: argparse.Namespace) -> int:
    rois: List[Tuple[str, Roi]] = [parse_sample(text) for text in args.sample]
    if not rois:
        return run_hsv_gui(args)
    samples, boxes, last = Samples(), [], None
    for frame in grab_frames(args.source, args.frames, args.skip, args):
        last = frame
        boxes = []
        for name, roi in rois:
            box = roi_box(frame, roi)
            samples.add_box(name, frame, box)
            boxes.append((name, box))
    base = load_base(args)
    spaces, calibrated, warnings = fit_spaces(samples, base, args.margin, args.quantiles)
    return finish_hsv(args, spaces, calibrated, warnings, last, boxes)


def finish_hsv(args, spaces, calibrated, warnings, frame, boxes) -> int:
    if not calibrated:
        print('ERRO: nenhuma classe calibrada.', file=sys.stderr)
        return 2
    preview = make_preview(frame, spaces, calibrated, boxes) if frame is not None else None
    written = write_hsv_outputs(Path(args.out), spaces, calibrated, preview)
    print('Faixas HSV:')
    print_spaces(spaces, calibrated)
    for text in warnings:
        print('AVISO:', text)
    missing = [c for c in CLASSES if c not in calibrated]
    if missing:
        print(f'AVISO: não calibrado (usa o padrão): {", ".join(missing)}. O arquivo .yaml só traz as calibradas.')
    print('Gravado:', ', '.join(str(p) for p in written))
    print('CONFIRA hsv_preview.png: o campo deve ficar tingido de verde e as linhas e a fronteira devem estar certas.')
    return 0


def screen_available() -> bool:
    if sys.platform.startswith('linux'):
        return bool(os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'))
    return True


def run_hsv_gui(args: argparse.Namespace) -> int:
    """Interativo: arraste um retângulo sobre a classe escolhida; as faixas se recalculam na hora."""
    if not screen_available():
        print('ERRO: sem tela (DISPLAY ausente). Use o modo sem tela: `snapshot` para ver a grade e '
              '`hsv --sample CLASSE=x,y,l,a`.', file=sys.stderr)
        return 2
    samples, base = Samples(), load_base(args)
    spaces, calibrated = dict(base), []
    state = {'cls': 'field', 'drag': None, 'rect': None, 'frame': None, 'pipeline': False, 'saved': True, 'scale': 1.0}
    boxes: List[Tuple[str, Tuple[int, int, int, int]]] = []

    def refit() -> None:
        nonlocal spaces, calibrated
        spaces, calibrated, _ = fit_spaces(samples, base, args.margin, args.quantiles)

    def on_mouse(event, x, y, _flags, _param) -> None:
        scale = state['scale']
        if event == cv2.EVENT_LBUTTONDOWN:
            state['drag'], state['rect'] = (x, y), (x, y, x, y)
        elif event == cv2.EVENT_MOUSEMOVE and state['drag']:
            state['rect'] = (state['drag'][0], state['drag'][1], x, y)
        elif event == cv2.EVENT_LBUTTONUP and state['drag'] and state['frame'] is not None:
            x0, y0 = state['drag']
            state['drag'], state['rect'] = None, None
            frame = state['frame']
            height, width = frame.shape[:2]
            box = (int(max(0, min(x0, x) / scale)), int(max(0, min(y0, y) / scale)),
                   int(min(width, max(x0, x) / scale)), int(min(height, max(y0, y) / scale)))
            if (box[2] - box[0]) * (box[3] - box[1]) >= 16:
                samples.add_box(state['cls'], frame, box)
                boxes.append((state['cls'], box))
                state['saved'] = False
                refit()

    source_is_image = is_image(args.source)
    cap = None
    paused = False
    try:
        if source_is_image:
            state['frame'] = cv2.imread(args.source)
            if state['frame'] is None:
                raise RuntimeError(f"não foi possível ler a imagem '{args.source}'")
        else:
            cap = open_camera(args.source, args.width, args.height, args.fourcc)
        cv2.namedWindow(GUI_WINDOW, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(GUI_WINDOW, on_mouse)
        while True:
            if cap is not None and not paused:
                ok, frame = cap.read()
                if ok:
                    state['frame'] = frame
            if state['frame'] is None:
                time.sleep(0.02)
                continue
            frame = state['frame']
            canvas = draw_gui(frame, spaces, calibrated, state, samples)
            state['scale'] = min(1.0, 1280.0 / canvas.shape[1])
            if state['scale'] < 1.0:
                canvas = cv2.resize(canvas, None, fx=state['scale'], fy=state['scale'], interpolation=cv2.INTER_AREA)
            cv2.imshow(GUI_WINDOW, canvas)
            key = cv2.waitKey(20) & 0xFF
            if key in (ord('q'), 27):
                break
            if key in (ord('1'), ord('2'), ord('3'), ord('4')):
                state['cls'] = CLASSES[key - ord('1')]
            elif key == ord(' '):
                paused = not paused
            elif key == ord('x'):
                samples.clear(state['cls'])
                boxes[:] = [b for b in boxes if b[0] != state['cls']]
                state['saved'] = False
                refit()
            elif key == ord('p'):
                state['pipeline'] = not state['pipeline']
            elif key == ord('s') and calibrated:
                _, _, warnings = fit_spaces(samples, base, args.margin, args.quantiles)
                finish_hsv(args, spaces, calibrated, warnings, frame, boxes)
                state['saved'] = True
    except cv2.error as error:
        print(f'ERRO do OpenCV ({error}). Seu OpenCV pode não ter janelas (opencv-python-headless?).', file=sys.stderr)
        return 2
    finally:
        if cap is not None:
            cap.release()
        try:
            cv2.destroyAllWindows()
        except cv2.error:
            pass
    if not state['saved']:
        print('AVISO: saiu sem salvar (tecla s). Nada foi gravado.')
    return 0


def draw_gui(frame, spaces, calibrated, state, samples) -> np.ndarray:
    """Texto só em ASCII: as fontes do OpenCV não têm acentos."""
    name = state['cls']
    if state['pipeline'] and calibrated:
        canvas = draw_pipeline_overlay(frame, VisionPipeline(build_color_detector(spaces), seed=0).run(frame))
    else:
        canvas = frame.copy()
        if name in calibrated:
            tint_mask(canvas, spaces[name].mask(frame), TINT_BGR[name])
    if state['rect']:
        x0, y0, x1, y1 = (int(v / state['scale']) for v in state['rect'])
        cv2.rectangle(canvas, (x0, y0), (x1, y1), (0, 255, 255), 2)
    s = spaces[name]
    lines = [f'[1]field [2]white [3]red [4]blue   classe: {name.upper()}   amostras: {samples.count(name)}',
             f'H {s.h_min}-{s.h_max}  S {s.s_min}-{s.s_max}  V {s.v_min}-{s.v_max}'
             + ('' if name in calibrated else '  (padrao, nao calibrado)'),
             'arraste=amostrar  espaco=pausa  x=limpa classe  p=pipeline  s=salvar  q=sair']
    for i, text in enumerate(lines):
        cv2.putText(canvas, text, (10, 24 + 24 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 4)
        cv2.putText(canvas, text, (10, 24 + 24 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    return canvas


# --------------------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------------------

def add_camera_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('--source', default='0',
                        help='câmera (N ou /dev/videoN), vídeo ou imagem (padrão: %(default)s)')
    parser.add_argument('--width', type=int, default=640, help='largura pedida à câmera (padrão: %(default)s)')
    parser.add_argument('--height', type=int, default=480, help='altura pedida à câmera (padrão: %(default)s)')
    parser.add_argument('--fourcc', default='', help='formato de captura, ex.: MJPG (padrão: o da câmera)')
    parser.add_argument('--out', default='calibracao', help='pasta de saída (padrão: %(default)s)')


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog='calibrar', description=__doc__.split('\n\n')[1].strip())
    sub = parser.add_subparsers(dest='command', required=True)

    snap = sub.add_parser('snapshot', help='foto com grade para escolher regiões sem tela')
    add_camera_options(snap)
    snap.add_argument('--skip', type=int, default=15, help='quadros descartados antes da foto (padrão: %(default)s)')

    hsv = sub.add_parser('hsv', help='calibra as faixas HSV (sem --sample: interativo)')
    add_camera_options(hsv)
    hsv.add_argument('--sample', action='append', default=[], metavar='CLASSE=x,y,l,a',
                     help='região amostrada, em frações da imagem; repita para várias (classes: %s)'
                     % ', '.join(CLASSES))
    hsv.add_argument('--frames', type=int, default=30, help='quadros amostrados no modo sem tela (padrão: %(default)s)')
    hsv.add_argument('--skip', type=int, default=15, help='quadros descartados no início (padrão: %(default)s)')
    hsv.add_argument('--base', type=Path, help='CSV de partida; as classes não calibradas mantêm esses valores')
    hsv.add_argument('--margin', type=int, nargs=3, default=DEFAULT_MARGIN, metavar=('H', 'S', 'V'),
                     help='folga somada à faixa medida (padrão: %(default)s)')
    hsv.add_argument('--quantiles', type=float, nargs=2, default=DEFAULT_QUANTILES, metavar=('BAIXO', 'ALTO'),
                     help='percentis que definem a faixa (padrão: %(default)s)')

    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        handler = {'snapshot': cmd_snapshot, 'hsv': cmd_hsv}[args.command]
        return handler(args)
    except (ValueError, RuntimeError) as error:
        print(f'ERRO: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
