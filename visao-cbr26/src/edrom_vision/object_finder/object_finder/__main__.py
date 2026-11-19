"""
Modo sem ROS: ``python3 -m object_finder``.

Exemplos::

    python3 -m object_finder --camera 2 --calib calibracoes/ultima
    python3 -m object_finder --image frame.png --sem-yolo
    python3 -m object_finder --video jogo.mp4 --modelo modelo/best.pt
    python3 -m object_finder --image frames/ --sem-janela --saida resultados/   # lote, sem tela

Na janela: S salva frame + overlay + JSON, ESPAÇO pausa, V troca a
visualização (tudo / só etapa 1 / imagem), ESC ou Q sai.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Any, List, Optional, Sequence

import cv2

from .detector import make_detector
from .overlay import render_result as render
from .params import default_params_file, load_params
from .pipeline import LineVisionPipeline


def _sources(a: argparse.Namespace):
    """Gera (nome, frame) de câmera, vídeo ou imagens."""
    if a.camera is not None:
        cap = cv2.VideoCapture(a.camera)
        if a.largura:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, a.largura)
        if a.altura:
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, a.altura)
        if not cap.isOpened():
            raise SystemExit(
                f'nao abriu a camera {a.camera} (WSL: usbipd; ou rode no Windows/NUC)')
        k = 0
        while True:
            ok, fr = cap.read()
            if not ok:
                break
            yield f'camera_{k:06d}', fr
            k += 1
    elif a.video:
        cap = cv2.VideoCapture(a.video)
        k = 0
        while True:
            ok, fr = cap.read()
            if not ok:
                break
            yield f'{Path(a.video).stem}_{k:06d}', fr
            k += 1
    else:
        files: List[Path] = []
        for p in a.image:
            pp = Path(p)
            files += sorted(f for f in pp.iterdir() if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.bmp')) \
                if pp.is_dir() else [pp]
        for f in files:
            fr = cv2.imread(str(f))
            if fr is None:
                print(f'aviso: nao li {f}', file=sys.stderr)
                continue
            yield f.stem, fr


def build_pipeline(a: argparse.Namespace) -> LineVisionPipeline:
    """Monta o pipeline a partir dos argumentos."""
    pfile = a.params or default_params_file()
    p = load_params(str(pfile) if pfile else None)
    det = None
    if not a.sem_yolo and a.modelo:
        det = make_detector(a.modelo, imgsz=p.detector.imgsz, conf=p.detector.conf, iou=p.detector.iou,
                            max_det=p.detector.max_det)
    calib = a.calib or _calib_do_config()
    if calib:
        return LineVisionPipeline.from_calibration_dir(calib, p, det)
    return LineVisionPipeline(p, detector=det)


def _calib_do_config() -> str:
    """Pasta config/ do object_finder instalado, se tiver a calibração de cor ('' se não)."""
    try:
        from ament_index_python.packages import get_package_share_directory
        d = Path(get_package_share_directory('object_finder')) / 'config'
    except Exception:  # noqa: BLE001 - sem ROS: usa a calibração padrão do vendor
        return ''
    return str(d) if (d / 'green_pixels.csv').is_file() and (d / 'white_pixels.csv').is_file() else ''


JANELA = 'object_finder'


def _esperar_tecla(bloquear: bool) -> Optional[int]:
    """
    Lê uma tecla sem travar o processo.

    ``cv2.waitKey(0)`` não volta se a janela for fechada no X e não deixa o
    Ctrl+C funcionar. Aqui a espera é feita em fatias de 50 ms. Devolve
    ``None`` se a janela foi fechada (quando o OpenCV sabe informar isso; no
    Docker/WSLg ele devolve -1 e só ESC/Q fecham).
    """
    visto = False
    while True:
        k = cv2.waitKey(50 if bloquear else 1)
        if k != -1:
            return k & 0xFF
        vis = cv2.getWindowProperty(JANELA, cv2.WND_PROP_VISIBLE)
        if vis >= 1:
            visto = True
        elif visto:
            return None
        if not bloquear:
            return 0xFF


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Ponto de entrada."""
    ap = argparse.ArgumentParser(prog='python3 -m object_finder',
                                 description='Visao por estrutura de linhas + YOLO (sem ROS).')
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument('--camera', type=int, help='indice da camera')
    src.add_argument('--image', nargs='+', help='imagem(ns) ou pasta(s)')
    src.add_argument('--video', help='arquivo de video')
    ap.add_argument('--largura', type=int, default=0)
    ap.add_argument('--altura', type=int, default=0)
    ap.add_argument('--calib', default='', help='pasta de calibracao (padrao: object_finder/config, se instalado)')
    ap.add_argument('--modelo', default='', help='best.pt ou best.onnx')
    ap.add_argument('--sem-yolo', action='store_true', help='so a segmentacao (sem detector)')
    ap.add_argument('--params', default='', help='YAML de parametros (padrao: config/params.yaml)')
    ap.add_argument('--saida', default='saida_rlv',
                    help='pasta para S (salvar) e para --sem-janela')
    ap.add_argument('--sem-janela', action='store_true',
                    help='nao abre janela; grava overlays e JSON')
    a = ap.parse_args(argv)
    if not a.modelo and not a.sem_yolo:
        default_model = Path(__file__).resolve().parent.parent / 'modelo' / 'best.pt'
        a.modelo = str(default_model) if default_model.is_file() else ''
    pipe = build_pipeline(a)
    out_dir = Path(a.saida)
    show = not a.sem_janela
    view, paused = 0, False
    fps, t_last = 0.0, time.perf_counter()
    last: Any = None
    for name, frame in _sources(a):
        if paused and show:
            frame, name = last if last else (frame, name)
        r = pipe.process(frame)
        now = time.perf_counter()
        fps = 0.9 * fps + 0.1 * (1.0 / max(1e-6, now - t_last)
                                 ) if fps else 1.0 / max(1e-6, now - t_last)
        t_last = now
        img = render(frame, r, fps, view)
        if not show:
            out_dir.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_dir / f'{name}_overlay.jpg'), img)
            (out_dir / f'{name}.json').write_text(json.dumps(r.summary(), ensure_ascii=False, indent=1),
                                                  encoding='utf-8')
            cr = [(c.tipo, round(c.x), round(c.y)) for c in r.crossings]
            print(f'{name}: campo={r.stage1.field_detected} cruzamentos={cr} '
                  f'linhas={len(r.lines)} {r.timings_ms["total"]:.0f} ms')
            continue
        cv2.imshow(JANELA, img)
        k = _esperar_tecla(bloquear=bool(a.image))
        if k is None:  # janela fechada no X
            break
        last = (frame, name)
        if k in (27, ord('q')):
            break
        if k == ord('s'):
            out_dir.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_dir / f'{name}.png'), frame)
            cv2.imwrite(str(out_dir / f'{name}_overlay.png'), img)
            (out_dir / f'{name}.json').write_text(json.dumps(r.summary(), ensure_ascii=False, indent=1),
                                                  encoding='utf-8')
            print(f'salvo em {out_dir}/{name}*')
        elif k == ord('v'):
            view = (view + 1) % 3
        elif k == ord(' '):
            paused = not paused
    if show:
        cv2.destroyAllWindows()
    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
