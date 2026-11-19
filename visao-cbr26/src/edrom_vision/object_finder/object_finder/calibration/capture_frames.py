"""
Captura N frames de uma câmera a cada T segundos (sem ROS).

Roda no Windows (Python com OpenCV) ou no Linux/WSL::

    python3 -m object_finder.calibration.capture_frames --camera 0 -n 20 -t 1.0 \
        --largura 640 --altura 480 --saida frames_dia13

Mostra uma janela de prévia se houver tela (``--sem-janela`` para desligar).
Na janela: ESPAÇO salva um frame na hora, ESC encerra.
"""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
import sys
import time
from typing import Callable, Optional, Sequence

import cv2


def capture(read: Callable[[], Optional['cv2.Mat']], n: int, interval: float, out_dir: Path,
            prefix: str = 'frame', show: bool = False,
            clock: Callable[[], float] = time.monotonic,
            sleep: Callable[[float], None] = time.sleep) -> list:
    """Laço de captura testável (``read`` devolve um frame BGR ou ``None``)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    saved: list = []
    next_t = clock()
    fails = 0
    while len(saved) < n:
        frame = read()
        if frame is None:
            fails += 1
            if fails > 50:
                raise RuntimeError('a camera parou de entregar frames')
            sleep(0.05)
            continue
        fails = 0
        now = clock()
        force = False
        if show:
            cv2.imshow('captura (ESPACO salva, ESC sai)', frame)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break
            force = k == 32
        if now >= next_t or force:
            stamp = dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            path = out_dir / f'{prefix}_{stamp}_{len(saved):03d}.png'
            cv2.imwrite(str(path), frame)
            saved.append(path)
            print(f'[{len(saved)}/{n}] {path}', flush=True)
            next_t = now + interval
        elif not show:
            sleep(min(0.02, max(0.0, next_t - now)))
    if show:
        cv2.destroyAllWindows()
    return saved


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Ponto de entrada."""
    ap = argparse.ArgumentParser(description='Salva N frames da camera a cada T segundos.')
    ap.add_argument('--camera', type=int, default=0)
    ap.add_argument('-n', type=int, default=20, help='quantidade de frames')
    ap.add_argument('-t', type=float, default=1.0, help='intervalo em segundos')
    ap.add_argument('--largura', type=int, default=0)
    ap.add_argument('--altura', type=int, default=0)
    ap.add_argument('--saida', default='frames')
    ap.add_argument('--prefixo', default='frame')
    ap.add_argument('--sem-janela', action='store_true')
    a = ap.parse_args(argv)
    cap = cv2.VideoCapture(a.camera)
    if a.largura:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, a.largura)
    if a.altura:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, a.altura)
    if not cap.isOpened():
        print(f'nao abriu a camera {a.camera}. No WSL a camera USB precisa do usbipd; '
              'alternativa: rode este script no Windows.', file=sys.stderr)
        return 2
    ok, fr = cap.read()
    if ok:
        print(f'camera {a.camera}: {fr.shape[1]}x{fr.shape[0]}')

    def read() -> Optional['cv2.Mat']:
        ok, f = cap.read()
        return f if ok else None

    try:
        capture(read, a.n, a.t, Path(a.saida), a.prefixo, show=not a.sem_janela)
    finally:
        cap.release()
    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
