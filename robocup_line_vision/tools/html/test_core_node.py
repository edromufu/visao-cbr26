"""
Compara o núcleo JS do calibrador HTML com o Python (precisa de node).

Uso: python3 tools/html/test_core_node.py <pasta_trabalho> img1 img2 ...
Grava os dados de entrada/referência, roda ``compare_core.js`` no node e
imprime a concordância (HSV em todas as 16,7 M cores, máscaras, campo,
esqueleto, proposta das faixas e CSV do branco lido pela fórmula original).
"""

import json
from pathlib import Path
import subprocess
import sys

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from robocup_line_vision.calibration import core  # noqa: E402
from robocup_line_vision.stage1_adapter import Stage1Segmenter, white_thresholds_from_csv  # noqa: E402

BOXES = [
    ({'lower': [52, 133, 102], 'upper': [62, 255, 172]},
     {'lower': [0, 0, 213], 'upper': [179, 49, 255]}),
    ({'lower': [48, 124, 106], 'upper': [65, 255, 191]},
     {'lower': [0, 0, 191], 'upper': [179, 49, 255]}),
    ({'lower': [55, 89, 15], 'upper': [75, 255, 109]},
     {'lower': [0, 0, 176], 'upper': [179, 41, 255]}),
]


def main() -> int:
    work = Path(sys.argv[1])
    work.mkdir(parents=True, exist_ok=True)
    # 1) cubo de cores completo
    allc = np.arange(1 << 24, dtype=np.uint32)
    bgr = np.stack([(allc >> 16) & 255, (allc >> 8) & 255, allc & 255], -
                   1).astype(np.uint8).reshape(4096, 4096, 3)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    rgba = np.concatenate([bgr[..., ::-1], np.full((4096, 4096, 1), 255, np.uint8)], -1)
    rgba.tofile(work / 'cube_rgba.bin')
    hsv.tofile(work / 'cube_hsv.bin')
    cases = []
    seg = Stage1Segmenter()
    rng = np.random.default_rng(0)
    for k, path in enumerate(sys.argv[2:]):
        img = cv2.imread(path)
        h, w = img.shape[:2]
        rgba = np.concatenate([img[..., ::-1], np.full((h, w, 1), 255, np.uint8)], -1)
        rgba.tofile(work / f'img{k}.bin')
        for b, (g, wt) in enumerate(BOXES):
            seg.set_green_box(g['lower'], g['upper'])
            seg.set_white_range(wt['lower'], wt['upper'])
            r = seg.process(img)
            tag = f'img{k}_b{b}'
            r.field_mask.astype(np.uint8).tofile(work / f'{tag}_field.bin')
            r.skeleton.astype(np.uint8).tofile(work / f'{tag}_skel.bin')
            r.relief.astype(np.uint8).tofile(work / f'{tag}_relief.bin')
            np.round(r.white_resized).astype(np.uint8).tofile(work / f'{tag}_wr.bin')
            m = core.sanity_metrics(r)
            keys = ('verde_no_campo', 'branco_cobre_campo', 'branco_na_fronteira', 'pixels_esqueleto')
            cases.append({'tag': tag, 'img': f'img{k}.bin', 'w': w, 'h': h, 'green': g, 'white': wt,
                          'detected': r.field_detected, 'metricas': {kk: m[kk] for kk in keys},
                          'vmin': core.suggest_white_vmin(r, cv2.cvtColor(img, cv2.COLOR_BGR2HSV))})
        # amostras para a proposta
        hsvi = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).reshape(-1, 3)
        idx = rng.choice(len(hsvi), 3000, replace=False)
        gs = hsvi[idx[:2000]]
        ws = hsvi[idx[2000:]]
        gr = core.propose_green_range(gs)
        wr = core.propose_white_range(ws, gr)
        cases.append({'tag': f'img{k}_prop', 'green_samples': gs.tolist(), 'white_samples': ws.tolist(),
                      'green': gr.to_dict(), 'white': wr.to_dict()})
    (work / 'cases.json').write_text(json.dumps(cases))
    out = subprocess.run(['node', str(Path(__file__).parent / 'compare_core.js'), str(work)],
                         capture_output=True, text=True)
    print(out.stdout)
    if out.returncode != 0:
        print(out.stderr)
        return 1
    # CSV do branco gerado pelo JS, lido pela fórmula original
    bad = 0
    for f in sorted(work.glob('white_js_*.csv')):
        exp = json.loads((f.with_suffix('.json')).read_text())
        lo, up = white_thresholds_from_csv(f)
        ok = lo.tolist() == exp['lower'] and up.tolist() == exp['upper']
        bad += not ok
    print(
        f'CSV branco do JS pela formula original: {len(list(work.glob("white_js_*.csv"))) - bad} ok, {bad} errados')
    return 0


if __name__ == '__main__':
    sys.exit(main())
