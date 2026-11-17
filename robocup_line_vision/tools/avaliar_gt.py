"""
Avalia o pipeline na verdade de terreno da usuária (4 frames do Webots).

Uso::

    python3 tools/avaliar_gt.py --kit <kit_visao> [--calib pasta] [--modelo best.pt|best.onnx]
        [--saida docs/metricas_gt] [--set cruzamentos.require_both=false ...]

Gera ``metricas_gt.json``, um resumo em texto e overlays (verde = verdade,
laranja/rosa/vermelho = detecção L/T/X, cinza = marca).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from robocup_line_vision import overlay  # noqa: E402
from robocup_line_vision.detector import make_detector  # noqa: E402
from robocup_line_vision.evaluation import (ellipse_metrics, is_mark, line_metrics, LineMetrics, load_gt,  # noqa: E402
                                            match_crossings, MatchResult)
from robocup_line_vision.params import load_params  # noqa: E402
from robocup_line_vision.pipeline import LineVisionPipeline  # noqa: E402

FRAMES = {'frame_webots.png': 'frame_webots.png', 'image.png': 'frames_gt/image.png',
          'image_1.png': 'frames_gt/image_1.png', 'image_2.png': 'frames_gt/image_2.png'}


def parse_sets(items):
    """``secao.chave=valor`` -> dict de overrides."""
    out = {}
    for it in items or []:
        k, v = it.split('=', 1)
        sec, key = k.split('.', 1)
        try:
            val = json.loads(v)
        except json.JSONDecodeError:
            val = v
        out.setdefault(sec, {})[key] = val
    return out


def draw_eval(img, r, gtimg, marks):
    """Overlay verdade x detecção."""
    out = overlay.draw_stage1(img, r.stage1, masks=False)
    overlay.draw_lines(out, r.lines)
    overlay.draw_ellipses(out, r.ellipses)
    overlay.draw_crossings(out, r.crossings)
    overlay.draw_detections(out, r.detections)
    for ln in gtimg['linhas']:
        cv2.line(out, (int(ln['x1']), int(ln['y1'])),
                 (int(ln['x2']), int(ln['y2'])), (0, 255, 0), 1, cv2.LINE_AA)
    for c in gtimg['cruzamentos']:
        col = (160, 160, 160) if c in marks else (0, 255, 0)
        cv2.drawMarker(out, (int(c['x']), int(c['y'])), col, cv2.MARKER_TILTED_CROSS, 16, 2)
        cv2.putText(out, c['tipo'], (int(c['x']) - 14, int(c['y']) + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 1)
    return out


def run(kit: Path, calib: str, modelo: str, saida: Path, overrides, label: str = '') -> dict:
    gt = load_gt(str(kit / 'gt_marcacoes.json'))
    p = load_params(overrides=overrides)
    det = make_detector(modelo or None, imgsz=p.detector.imgsz, conf=p.detector.conf,
                        iou=p.detector.iou, max_det=p.detector.max_det)
    pipe = (LineVisionPipeline.from_calibration_dir(calib, p, det) if calib
            else LineVisionPipeline(p, detector=det))
    saida.mkdir(parents=True, exist_ok=True)
    tot, tot_m, tot_l, tot_base = MatchResult(), MatchResult(), LineMetrics(), LineMetrics()
    per = {}
    times = []
    for name, rel in FRAMES.items():
        img = cv2.imread(str(kit / rel))
        r = pipe.process(img)
        times.append(r.timings_ms)
        g = gt[name]
        marks = [c for c in g['cruzamentos'] if is_mark(c, g)]
        real = [c for c in g['cruzamentos'] if not is_mark(c, g)]
        mm = match_crossings([c for c in r.crossings if c.tipo == 'X'], marks)
        xs = [c for c in r.crossings if c.tipo == 'X']
        on_marks = {id(xs[i]) for i, _, _ in mm.pares}
        # detecções que caem numa marca (centro/pênalti) não contam como FP de cruzamento
        m = match_crossings([c for c in r.crossings if id(c) not in on_marks], real)
        lm = line_metrics(r.lines, g)
        base = pipe.seg.vendor_segmenter._extrair_segmentos_conectados(
            r.stage1.skeleton.astype(np.uint8) * 255)
        from types import SimpleNamespace as NS
        bl = [NS(x1=s['p1'][0], y1=s['p1'][1], x2=s['p2'][0], y2=s['p2'][1])
              for s in base['segmentos_linhas']]
        bm = line_metrics(bl, g)
        em = ellipse_metrics(r.ellipses, g)
        tot.add(m)
        tot_m.add(mm)
        tot_l.add(lm)
        tot_base.add(bm)
        detect = [(c.tipo, round(c.x), round(c.y), c.confianca, c.fonte) for c in r.crossings]
        per[name] = {
            'cruzamentos': {'gt': len(real), 'det': len(r.crossings), 'tp': m.tp, 'tp_tipo': m.tp_tipo,
                            'fp': m.fp, 'fn': m.fn, 'por_tipo': m.por_tipo, 'detectados': detect},
            'marcas': {'gt': len(marks), 'tp': mm.tp},
            'linhas': lm.__dict__, 'linhas_baseline_etapa1': bm.__dict__, 'elipse': em,
            'tempos_ms': r.timings_ms,
        }
        cv2.imwrite(str(saida / f'eval_{Path(name).stem}{label}.jpg'), draw_eval(img, r, g, marks),
                    [cv2.IMWRITE_JPEG_QUALITY, 85])
    res = {
        'calibracao': calib or 'padrao_webots', 'modelo': modelo or 'sem_yolo', 'overrides': overrides,
        'cruzamentos': {'gt': tot.tp + tot.fn, 'det': tot.tp + tot.fp, 'tp': tot.tp, 'tp_tipo': tot.tp_tipo,
                        'fp': tot.fp, 'fn': tot.fn, 'precisao': round(tot.precisao, 3),
                        'recall': round(tot.recall, 3),
                        'precisao_tipo': round(tot.tp_tipo / (tot.tp + tot.fp), 3) if (tot.tp + tot.fp) else 0.0,
                        'recall_tipo': round(tot.tp_tipo / (tot.tp + tot.fn), 3) if (tot.tp + tot.fn) else 0.0,
                        'por_tipo': tot.por_tipo},
        'marcas_X': {'gt': tot_m.tp + tot_m.fn, 'tp': tot_m.tp},
        'linhas': {**tot_l.__dict__, 'recall_longas': round(tot_l.recall, 3), 'precisao': round(tot_l.precisao, 3)},
        'linhas_baseline_etapa1': {**tot_base.__dict__, 'recall_longas': round(tot_base.recall, 3),
                                   'precisao': round(tot_base.precisao, 3)},
        'tempo_medio_ms': {k: round(float(np.mean([t[k] for t in times])), 1) for k in times[0]},
        'por_imagem': per,
    }
    (saida / f'metricas_gt{label}.json').write_text(json.dumps(res, indent=2, ensure_ascii=False),
                                                    encoding='utf-8')
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--kit', required=True)
    ap.add_argument('--calib', default='')
    ap.add_argument('--modelo', default='')
    ap.add_argument('--saida', default='docs/metricas_gt')
    ap.add_argument('--rotulo', default='')
    ap.add_argument('--set', nargs='*', default=[])
    a = ap.parse_args()
    r = run(Path(a.kit), a.calib, a.modelo, Path(a.saida), parse_sets(a.set), a.rotulo)
    c = r['cruzamentos']
    print(f"cruzamentos: GT {c['gt']} det {c['det']} TP {c['tp']} (tipo certo {c['tp_tipo']}) "
          f"FP {c['fp']} FN {c['fn']} | P {c['precisao']:.2f} R {c['recall']:.2f} | "
          f"P_tipo {c['precisao_tipo']:.2f} R_tipo {c['recall_tipo']:.2f}")
    for t, d in c['por_tipo'].items():
        print(f'   {t}: {d}')
    print(f"marcas X: {r['marcas_X']}")
    ln, bl = r['linhas'], r['linhas_baseline_etapa1']
    print(f"linhas: longas {ln['gt_longas_cobertas']}/{ln['gt_longas']} (R {ln['recall_longas']:.2f}), "
          f"curtas {ln['gt_curtas_cobertas']}/{ln['gt_curtas']}, det {ln['det']} corretas {ln['det_corretas']} "
          f"(P {ln['precisao']:.2f})")
    print(f"  baseline etapa 1: longas {bl['gt_longas_cobertas']}/{bl['gt_longas']}, det {bl['det']} "
          f"corretas {bl['det_corretas']} (P {bl['precisao']:.2f})")
    for n, d in r['por_imagem'].items():
        cc = d['cruzamentos']
        print(f"  {n}: GT {cc['gt']} det {cc['det']} TP {cc['tp']} FP {cc['fp']} FN {cc['fn']} | "
              f"elipse {d['elipse']} | {cc['detectados']}")
    print('tempo medio ms', r['tempo_medio_ms'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
