"""
Validação da calibração (P0) com os frames disponíveis.

(i)   4 frames do Webots: amostras manuais simuladas (pinceladas sobre as
      linhas da verdade de terreno e retângulos no carpete);
(ii)  2 fotos reais (NAO/SPL): amostras manuais escolhidas olhando as fotos;
(iii) frames do Webots perturbados (brilho, contraste, balanço de branco,
      gama): calibração original x recalibração rápida (2 cliques).

Uso::

    python3 tools/validar_calibracao.py --kit <pasta kit_visao> --seg <repo original da etapa 1> \
        --saida docs/validacao_p0
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from robocup_line_vision import overlay  # noqa: E402
from robocup_line_vision.calibration import core  # noqa: E402
from robocup_line_vision.calibration.calibrator_cv import Calibrador  # noqa: E402
from robocup_line_vision.stage1_adapter import Stage1Segmenter  # noqa: E402

# Amostras escolhidas olhando as fotos reais (coordenadas da imagem 640x640).
REAIS = {
    'bitbots': {
        'verde_ret': [(40, 500, 260, 600), (500, 560, 620, 630), (420, 300, 520, 360),
                      (150, 300, 250, 340)],
        'branco_pincel': [[(80, 350), (270, 450)], [(300, 445), (480, 270)],
                          [(100, 315), (250, 255)]],
        'clique_verde': (150, 560), 'clique_branco': (180, 400),
    },
    'eliza': {
        'verde_ret': [(40, 500, 300, 620), (400, 450, 620, 600), (210, 350, 270, 400)],
        'branco_pincel': [[(20, 330), (220, 430)], [(260, 430), (370, 360)],
                          [(420, 350), (600, 400)]],
        'clique_verde': (200, 560), 'clique_branco': (120, 380),
    },
}


def skeleton_f1(a: np.ndarray, b: np.ndarray, tol: int = 1) -> float:
    """F1 entre dois esqueletos na grade, com tolerância de ``tol`` células."""
    if a.sum() == 0 and b.sum() == 0:
        return 1.0
    if a.sum() == 0 or b.sum() == 0:
        return 0.0
    k = np.ones((2 * tol + 1, 2 * tol + 1), np.uint8)
    da = cv2.dilate(a.astype(np.uint8), k) > 0
    db = cv2.dilate(b.astype(np.uint8), k) > 0
    p = (a & db).sum() / a.sum()
    r = (b & da).sum() / b.sum()
    return float(2 * p * r / (p + r)) if p + r else 0.0


def iou(a: np.ndarray, b: np.ndarray) -> float:
    """Calcula a interseção sobre união (IoU) de duas máscaras."""
    a, b = a > 0, b > 0
    u = (a | b).sum()
    return float((a & b).sum() / u) if u else 1.0


def gt_grid(gt_img: dict, grid_shape, image_shape, long_only: bool = False) -> np.ndarray:
    """Verdade de terreno (linhas + círculos) rasterizada na grade 1/8."""
    h, w = image_shape
    canvas = np.zeros((h, w), np.uint8)
    for ln in gt_img['linhas']:
        if long_only and np.hypot(ln['x2'] - ln['x1'], ln['y2'] - ln['y1']) < 30:
            continue
        cv2.line(canvas, (int(ln['x1']), int(ln['y1'])), (int(ln['x2']), int(ln['y2'])), 255, 3)
    for c in gt_img.get('circulos', []):
        pts = np.array([[p['x'], p['y']] if isinstance(p, dict)
                       else p for p in c['pontos']], np.int32)
        cv2.polylines(canvas, [pts.reshape(-1, 1, 2)], bool(c.get('fechado')), 255, 3)
    gh, gw = grid_shape
    return cv2.resize(canvas, (gw, gh), interpolation=cv2.INTER_AREA) > 0


def skel_vs_gt(skel: np.ndarray, gt_all: np.ndarray, gt_long: np.ndarray) -> dict:
    """Precisão/recall do esqueleto contra a verdade de terreno (tolerância 1 célula)."""
    k = np.ones((3, 3), np.uint8)
    gd = cv2.dilate(gt_all.astype(np.uint8), k) > 0
    sd = cv2.dilate(skel.astype(np.uint8), k) > 0
    prec = float((skel & gd).sum() / skel.sum()) if skel.sum() else 0.0
    rec = float((gt_long & sd).sum() / gt_long.sum()) if gt_long.sum() else 0.0
    return {'precisao': round(prec, 3), 'recall': round(rec, 3)}


def perturb(img: np.ndarray, kind: str) -> np.ndarray:
    """Perturbações de iluminação."""
    f = img.astype(np.float32)
    if kind == 'escuro_0.55':
        f = f * 0.55
    elif kind == 'claro_1.35':
        f = f * 1.35
    elif kind == 'contraste_0.6':
        f = (f - 128) * 0.6 + 128
    elif kind == 'contraste_1.5':
        f = (f - 128) * 1.5 + 128
    elif kind == 'quente':
        f = f * np.array([0.78, 1.0, 1.22], np.float32)
    elif kind == 'frio':
        f = f * np.array([1.25, 1.0, 0.82], np.float32)
    elif kind == 'gama_1.8':
        f = 255.0 * (f / 255.0) ** 1.8
    elif kind == 'escuro_quente':
        f = f * 0.65 * np.array([0.8, 1.0, 1.2], np.float32)
    return np.clip(f, 0, 255).astype(np.uint8)


PERTURB = ['escuro_0.55', 'claro_1.35', 'contraste_0.6', 'contraste_1.5', 'quente',
           'frio', 'gama_1.8', 'escuro_quente']


def gt_line_strokes(gt_img: dict, min_len: float = 30.0):
    """Pinceladas sobre as linhas longas da verdade de terreno."""
    out = []
    for ln in gt_img['linhas']:
        p, q = (ln['x1'], ln['y1']), (ln['x2'], ln['y2'])
        if np.hypot(q[0] - p[0], q[1] - p[1]) >= min_len:
            out.append([(int(round(p[0])), int(round(p[1]))),
                       (int(round(q[0])), int(round(q[1])))])
    return out


def webots_green_rects(img: np.ndarray):
    """Retângulos de carpete na faixa de baixo do frame (sem linhas)."""
    h, w = img.shape[:2]
    y0, y1 = int(h * 0.88), int(h * 0.97)
    return [(int(w * 0.05), y0, int(w * 0.30), y1), (int(w * 0.70), y0, int(w * 0.95), y1)]


def run(kit: Path, seg_repo: Path, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    gt = json.loads((kit / 'gt_marcacoes.json').read_text(encoding='utf-8'))['imagens']
    webots = {'frame_webots.png': cv2.imread(str(kit / 'frame_webots.png'))}
    for n in ('image.png', 'image_1.png', 'image_2.png'):
        webots[n] = cv2.imread(str(kit / 'frames_gt' / n))
    reais = {}
    for key in REAIS:
        f = next((seg_repo / 'images').glob(f'{key}*'))
        reais[key] = cv2.imread(str(f))
    ref = Stage1Segmenter()  # calibração original
    report: dict = {'webots': {}, 'reais': {}, 'perturbacoes': {}}

    # (i) Webots: calibração manual simulada (todas as 4 imagens juntas)
    t0 = time.perf_counter()
    cal = Calibrador(webots, out / 'calib_webots')
    for name, img in webots.items():
        cal.idx = cal.names.index(name)
        for r in webots_green_rects(img):
            cal.add_sample(core.Sample('verde', 'retangulo', name, retangulo=r))
        for st in gt_line_strokes(gt[name]):
            cal.add_sample(core.Sample('branco', 'pincel', name, pontos=st, raio=3))
    report['webots']['faixas_proposta'] = {
        'verde': cal.green.to_dict(), 'branco': cal.white.to_dict()}
    prop_seg = Stage1Segmenter()
    prop_seg.set_green_box(cal.green.lower, cal.green.upper)
    prop_seg.set_white_range(cal.white.lower, cal.white.upper)
    # a usuária segue o aviso e tecla A no frame com o aviso (frame_webots)
    cal.idx = cal.names.index('frame_webots.png')
    report['webots']['tecla_A'] = cal.apply_vmin_suggestion()
    dir_web = cal.save()
    t_cal = time.perf_counter() - t0
    report['webots']['faixas'] = {'verde': cal.green.to_dict(), 'branco': cal.white.to_dict()}
    report['webots']['pasta'] = dir_web.name
    report['webots']['tempo_cpu_s'] = round(t_cal, 2)
    seg_new = Stage1Segmenter(dir_web / 'green_pixels.csv', dir_web / 'white_pixels.csv')
    for name, img in webots.items():
        a = ref.process(img)
        b = seg_new.process(img)
        c = prop_seg.process(img)
        m = core.sanity_metrics(b)
        g_all = gt_grid(gt[name], a.grid_shape, a.image_shape)
        g_long = gt_grid(gt[name], a.grid_shape, a.image_shape, long_only=True)
        report['webots'][name] = {
            'esqueleto_vs_gt': {'original': skel_vs_gt(a.skeleton, g_all, g_long),
                                'proposta_auto': skel_vs_gt(c.skeleton, g_all, g_long),
                                'apos_A': skel_vs_gt(b.skeleton, g_all, g_long)},
            'campo_original': a.field_detected, 'campo_nova': b.field_detected,
            'iou_campo_vs_original': round(iou(a.field_mask, b.field_mask), 3),
            'f1_esqueleto_vs_original': round(skeleton_f1(a.skeleton, b.skeleton), 3),
            'esqueleto_px_original': int(a.skeleton.sum()), 'esqueleto_px_nova': int(b.skeleton.sum()),
            'metricas': {k: (round(v, 3) if isinstance(v, float) else v) for k, v in m.items()},
        }
        cv2.imwrite(str(out / f'webots_{Path(name).stem}.jpg'),
                    np.hstack([overlay.draw_stage1(img, a), overlay.draw_stage1(img, b)]))

    # (ii) fotos reais: amostras manuais e recalibração rápida
    for key, img in reais.items():
        spec = REAIS[key]
        name = f'{key}.png'
        before = ref.process(img)
        cal = Calibrador({name: img}, out / f'calib_{key}')
        for r in spec['verde_ret']:
            cal.add_sample(core.Sample('verde', 'retangulo', name, retangulo=r))
        for st in spec['branco_pincel']:
            cal.add_sample(core.Sample('branco', 'pincel', name, pontos=st, raio=4))
        d = cal.save()
        seg_r = Stage1Segmenter(d / 'green_pixels.csv', d / 'white_pixels.csv')
        after = seg_r.process(img)
        quick = Calibrador({name: img}, out / f'calib_{key}_rapida')
        quick.start_quick()
        quick.on_mouse(cv2.EVENT_LBUTTONDOWN, *spec['clique_verde'])
        quick.on_mouse(cv2.EVENT_LBUTTONDOWN, *spec['clique_branco'])
        qs1, qm = quick.evaluate(img)
        report['reais'][key] = {
            'campo_original': before.field_detected,
            'manual': {'campo': after.field_detected, 'faixas': {'verde': cal.green.to_dict(),
                                                                 'branco': cal.white.to_dict()},
                       'metricas': {k: (round(v, 3) if isinstance(v, float) else v)
                                    for k, v in core.sanity_metrics(after).items()},
                       'n_triades_verde': cal.green.n_triads()},
            'rapida': {'campo': qs1.field_detected, 'faixas': {'verde': quick.green.to_dict(),
                                                               'branco': quick.white.to_dict()},
                       'metricas': {k: (round(v, 3) if isinstance(v, float) else v) for k, v in qm.items()},
                       'f1_esqueleto_vs_manual': round(skeleton_f1(qs1.skeleton, after.skeleton), 3)},
        }
        cv2.imwrite(str(out / f'real_{key}.jpg'),
                    np.hstack([overlay.draw_stage1(img, before), overlay.draw_stage1(img, after),
                               overlay.draw_stage1(img, qs1)]))

    # (iii) perturbações nos frames do Webots
    for name, img in webots.items():
        base = ref.process(img)
        g_all = gt_grid(gt[name], base.grid_shape, base.image_shape)
        g_long = gt_grid(gt[name], base.grid_shape, base.image_shape, long_only=True)
        report['perturbacoes'].setdefault('_sem_perturbacao', {})[
            name] = skel_vs_gt(base.skeleton, g_all, g_long)
        lines = gt_line_strokes(gt[name])
        p, q = lines[0][0], lines[0][1]
        click_w = (int((p[0] + q[0]) / 2), int((p[1] + q[1]) / 2))
        h, w = img.shape[:2]
        click_g = (int(w * 0.15), int(h * 0.93))
        rows = {}
        for kind in PERTURB:
            pim = perturb(img, kind)
            a = ref.process(pim)
            qc = Calibrador({name: pim}, out / 'descartar')
            qc.start_quick()
            qc.on_mouse(cv2.EVENT_LBUTTONDOWN, *click_g)
            qc.on_mouse(cv2.EVENT_LBUTTONDOWN, *click_w)
            b, mb = qc.evaluate(pim)
            sug = qc.apply_vmin_suggestion() if not mb['ok'] else None
            if sug is not None:
                b, mb = qc.evaluate(pim)
            g_all = gt_grid(gt[name], a.grid_shape, a.image_shape)
            g_long = gt_grid(gt[name], a.grid_shape, a.image_shape, long_only=True)
            rows[kind] = {
                'gt_original': skel_vs_gt(a.skeleton, g_all, g_long),
                'gt_rapida': skel_vs_gt(b.skeleton, g_all, g_long),
                'tecla_A': sug,
                'original': {'campo': a.field_detected,
                             'iou_campo': round(iou(a.field_mask, base.field_mask), 3),
                             'f1_esqueleto': round(skeleton_f1(a.skeleton, base.skeleton), 3)},
                'rapida': {'campo': b.field_detected,
                           'iou_campo': round(iou(b.field_mask, base.field_mask), 3),
                           'f1_esqueleto': round(skeleton_f1(b.skeleton, base.skeleton), 3),
                           'ok': mb['ok']},
            }
            if name == 'image_1.png' and kind in ('escuro_quente', 'contraste_0.6'):
                cv2.imwrite(str(out / f'perturb_{Path(name).stem}_{kind}.jpg'),
                            np.hstack([overlay.draw_stage1(pim, a), overlay.draw_stage1(pim, b)]))
        report['perturbacoes'][name] = rows
    with open(out / 'validacao_p0.json', 'w', encoding='utf-8') as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    return report


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--kit', required=True)
    ap.add_argument('--seg', required=True)
    ap.add_argument('--saida', default='docs/validacao_p0')
    a = ap.parse_args()
    r = run(Path(a.kit), Path(a.seg), Path(a.saida))
    print(json.dumps(r, indent=1, ensure_ascii=False)[:6000])
