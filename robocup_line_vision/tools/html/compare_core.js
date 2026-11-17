// Usado por test_core_node.py: compara o núcleo JS com as referências do Python.
const fs = require('fs');
const path = require('path');
const RLV = require('./calibrador_core.js');
const dir = process.argv[2];
function rd(f) { return new Uint8Array(fs.readFileSync(path.join(dir, f))); }

// 1) HSV no cubo inteiro
const cube = rd('cube_rgba.bin'), ref = rd('cube_hsv.bin');
const n = cube.length / 4;
const hsv = RLV.rgbaToHsv(cube, n);
let bad = 0;
for (let p = 0; p < n; p++) if (hsv.H[p] !== ref[3 * p] || hsv.S[p] !== ref[3 * p + 1] || hsv.V[p] !== ref[3 * p + 2]) bad++;
console.log(`HSV: ${n - bad} de ${n} cores iguais ao OpenCV (${bad} diferentes)`);

const cases = JSON.parse(fs.readFileSync(path.join(dir, 'cases.json')));
const imgs = {};
for (const c of cases) {
  if (c.green_samples) {
    const g = RLV.proposeGreen(c.green_samples), w = RLV.proposeWhite(c.white_samples, g);
    const same = JSON.stringify([g, w]) === JSON.stringify([c.green, c.white]);
    console.log(`${c.tag}: proposta ${same ? 'IGUAL' : 'DIFERENTE'} ${same ? '' : JSON.stringify([g, w, c.green, c.white])}`);
    continue;
  }
  if (!imgs[c.img]) imgs[c.img] = rd(c.img);
  const r = RLV.stage1(imgs[c.img], c.w, c.h, c.green, c.white);
  const F = rd(`${c.tag}_field.bin`), S = rd(`${c.tag}_skel.bin`), R = rd(`${c.tag}_relief.bin`), WR = rd(`${c.tag}_wr.bin`);
  let fd = 0, sd = 0, rdf = 0, wd = 0, sp = 0, ss = 0;
  for (let i = 0; i < F.length; i++) {
    if ((F[i] > 0) !== (r.field[i] > 0)) fd++;
    if (S[i] !== r.skeleton[i]) sd++;
    if (R[i] !== r.relief[i]) rdf++;
    if (WR[i] !== r.whiteResized[i]) wd++;
    sp += S[i]; ss += r.skeleton[i];
  }
  const m = RLV.sanity(r), v = RLV.suggestVmin(r);
  console.log(`${c.tag}: campo ${r.fieldDetected === c.detected ? 'igual' : 'DIFERENTE'} | celulas campo diferentes ${fd}/${F.length}` +
    ` | branco grade dif ${wd} | relevo dif ${rdf} | esqueleto dif ${sd} (py ${sp}, js ${ss})` +
    ` | metricas py ${JSON.stringify(c.metricas)} js ${JSON.stringify({ v: +m.verde_no_campo.toFixed(4), b: +m.branco_cobre_campo.toFixed(4), f: +m.branco_na_fronteira.toFixed(4), e: m.pixels_esqueleto })}` +
    ` | vmin py ${c.vmin} js ${v}`);
}
// CSV do branco para conferir no Python
const boxes = [[[0, 0, 213], [179, 43, 255]], [[45, 0, 213], [164, 43, 255]], [[0, 0, 150], [179, 80, 255]], [[10, 5, 100], [20, 9, 101]], [[3, 0, 254], [177, 1, 255]], [[0, 0, 241], [179, 37, 255]]];
boxes.forEach((b, i) => {
  const box = RLV.mkBox(b[0], b[1]);
  fs.writeFileSync(path.join(dir, `white_js_${i}.csv`), RLV.whiteCsv(box));
  fs.writeFileSync(path.join(dir, `white_js_${i}.json`), JSON.stringify(box));
});
const gp = RLV.greenCsvParts(RLV.mkBox([50, 140, 120], [52, 142, 121])).join('');
console.log(`CSV verde denso (3x3x2): ${gp.trim().split('\n').length - 1} linhas`);
