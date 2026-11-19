"""
Avalia o pipeline no campo sintético (verdade de terreno automática).

Uso::

    python3 tools/avaliar_sintetico.py -n 40 --seed 7 --saida docs/metricas_sintetico [--variantes]
        [--set cruzamentos.require_both=false ...]

A calibração é feita uma vez pela recalibração rápida (2 cliques simulados:
um no carpete e um sobre uma linha da verdade de terreno), como no dia do
teste. Saída: métricas por tipo, linhas longas, tempo e alguns overlays.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile

from avaliar_gt import draw_eval, parse_sets  # noqa: I100
import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from object_finder.calibration.calibrator_cv import Calibrador  # noqa: E402
from object_finder.evaluation import line_metrics, LineMetrics, match_crossings, MatchResult  # noqa: E402
from object_finder.params import load_params  # noqa: E402
from object_finder.pipeline import LineVisionPipeline  # noqa: E402
from object_finder.synthetic import dataset  # noqa: E402


def load_or_make(n: int, seed: int, variants: bool, cache: str):
    """Gera os frames (ou lê do cache, que acelera experimentos)."""
    import pickle
    if cache:
        f = Path(cache) / f'sint_n{n}_s{seed}_v{int(variants)}.pkl'
        if f.is_file():
            with open(f, 'rb') as fh:
                return pickle.load(fh)
    frames = dataset(n, seed=seed, min_crossings=1, variants=variants)
    if cache:
        Path(cache).mkdir(parents=True, exist_ok=True)
        with open(f, 'wb') as fh:
            pickle.dump(frames, fh)
    return frames


def calibrate(frame, out_root: Path) -> Path:
    """Recalibração rápida simulada: clique no carpete e numa linha."""
    img = frame.image
    gt = frame.gt
    ln = max(gt['linhas'], key=lambda s: abs(s['x2'] - s['x1']) + abs(s['y2'] - s['y1']))
    xw, yw = int((ln['x1'] + ln['x2']) / 2), int((ln['y1'] + ln['y2']) / 2)
    h, w = img.shape[:2]
    cal = Calibrador({'f.png': img}, out_root)
    cal.start_quick()
    # carpete: ponto perto do pé da imagem longe da linha
    gy = h - 20
    gx = 40 if abs(xw - 40) > 100 else w - 40
    cal.on_mouse(cv2.EVENT_LBUTTONDOWN, gx, gy)
    cal.on_mouse(cv2.EVENT_LBUTTONDOWN, xw, yw)
    return cal.save()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('-n', type=int, default=40)
    ap.add_argument('--seed', type=int, default=7)
    ap.add_argument('--variantes', action='store_true', help='ruído de brilho e borrão')
    ap.add_argument('--saida', default='docs/metricas_sintetico')
    ap.add_argument('--set', nargs='*', default=[])
    ap.add_argument('--overlays', type=int, default=4)
    ap.add_argument('--cache', default='', help='pasta para guardar/reusar os frames gerados')
    a = ap.parse_args()
    out = Path(a.saida)
    out.mkdir(parents=True, exist_ok=True)
    frames = load_or_make(a.n, a.seed, a.variantes, a.cache)
    with tempfile.TemporaryDirectory() as td:
        calib = calibrate(frames[0], Path(td))
        p = load_params(overrides=parse_sets(a.set))
        pipe = LineVisionPipeline.from_calibration_dir(str(calib), p)
        tot, lm_tot = MatchResult(), LineMetrics()
        bands = {'<2m': [0, 0], '2-4m': [0, 0], '>=4m': [0, 0]}
        marks_gt = marks_tp = 0
        fails = 0
        times = []
        for k, fr in enumerate(frames):
            r = pipe.process(fr.image)
            times.append(r.timings_ms['total'] - r.timings_ms.get('yolo', 0))
            if not r.stage1.field_detected:
                fails += 1
            real = [c for c in fr.gt['cruzamentos'] if not c['marca']]
            marks = [c for c in fr.gt['cruzamentos'] if c['marca']]
            mr = match_crossings(r.crossings, real)
            tot.add(mr)
            hit = {j for _, j, _ in mr.pares}
            for j, c in enumerate(real):
                d = c.get('dist_m') or 99
                b = '<2m' if d < 2 else ('2-4m' if d < 4 else '>=4m')
                bands[b][0] += 1
                bands[b][1] += j in hit
            mm = match_crossings([c for c in r.crossings if c.tipo == 'X'], marks)
            marks_gt += len(marks)
            marks_tp += mm.tp
            lm_tot.add(line_metrics(r.lines, fr.gt))
            if k < a.overlays:
                cv2.imwrite(str(out / f'sintetico_{k:02d}.jpg'),
                            draw_eval(fr.image, r, fr.gt, [
                                      c for c in fr.gt['cruzamentos'] if c['marca']]),
                            [cv2.IMWRITE_JPEG_QUALITY, 80])
    res = {
        'n_frames': len(frames), 'seed': a.seed, 'variantes': a.variantes, 'overrides': parse_sets(a.set),
        'campo_nao_detectado': fails,
        'cruzamentos': {'gt': tot.tp + tot.fn, 'det': tot.tp + tot.fp, 'tp': tot.tp, 'tp_tipo': tot.tp_tipo,
                        'fp': tot.fp, 'fn': tot.fn, 'precisao': round(tot.precisao, 3),
                        'recall': round(tot.recall, 3), 'por_tipo': tot.por_tipo},
        'marcas': {'gt': marks_gt, 'tp': marks_tp},
        'recall_por_distancia': {k: {'gt': v[0], 'tp': v[1], 'recall': round(v[1] / v[0], 3) if v[0] else None}
                                 for k, v in bands.items()},
        'linhas': {**lm_tot.__dict__, 'recall_longas': round(lm_tot.recall, 3), 'precisao': round(lm_tot.precisao, 3)},
        'tempo_ms_mediana': round(float(np.median(times)), 1),
    }
    tag = '_variantes' if a.variantes else ''
    (out / f'metricas_sintetico{tag}.json').write_text(json.dumps(res,
                                                                  indent=2, ensure_ascii=False), encoding='utf-8')
    c = res['cruzamentos']
    print(f"[{len(frames)} frames{' +ruido' if a.variantes else ''}] campo nao detectado: {fails}")
    print(f"cruzamentos: GT {c['gt']} det {c['det']} TP {c['tp']} (tipo {c['tp_tipo']}) FP {c['fp']} FN {c['fn']} "
          f"| P {c['precisao']:.2f} R {c['recall']:.2f}")
    for t, d in c['por_tipo'].items():
        print(f'   {t}: {d}')
    print('   recall por distancia:', res['recall_por_distancia'])
    ln = res['linhas']
    print(f"linhas longas {ln['gt_longas_cobertas']}/{ln['gt_longas']} (R {ln['recall_longas']:.2f}), det {ln['det']} "
          f"corretas {ln['det_corretas']} (P {ln['precisao']:.2f}) | marcas {marks_tp}/{marks_gt} | "
          f"tempo mediano {res['tempo_ms_mediana']} ms")
    return 0


if __name__ == '__main__':
    sys.exit(main())
