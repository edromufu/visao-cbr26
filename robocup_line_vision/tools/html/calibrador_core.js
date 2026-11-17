/*
 * Núcleo do calibrador HTML (sem interface): cópia em JavaScript da etapa 1
 * original (III-A fronteira e III-B esqueleto) e da proposta de faixas do
 * Python (robocup_line_vision/calibration/core.py).
 *
 * Fidelidade: a conversão BGR->HSV reproduz a aritmética inteira do OpenCV;
 * resize INTER_AREA, GaussianBlur 5x5 (binomial, ponto fixo), medfilt e
 * gaussian_filter1d seguem o OpenCV/SciPy. A equivalência com o Python é
 * medida em tools/html/test_core_node.py (ver docs/metricas.md).
 */
(function (root) {
  'use strict';

  // ------------------------------------------------------------------ HSV
  var SDIV = new Int32Array(256), HDIV = new Int32Array(256);
  for (var i = 1; i < 256; i++) {
    SDIV[i] = Math.round((255 << 12) / i);
    HDIV[i] = Math.round((180 << 12) / (6 * i));
  }

  /** RGBA (canvas) -> H, S, V (Uint8Array cada), igual ao cv2.COLOR_BGR2HSV. */
  function rgbaToHsv(rgba, n) {
    var H = new Uint8Array(n), S = new Uint8Array(n), V = new Uint8Array(n);
    for (var p = 0, q = 0; p < n; p++, q += 4) {
      var r = rgba[q], g = rgba[q + 1], b = rgba[q + 2];
      var v = b, vmin = b;
      if (g > v) v = g; if (r > v) v = r;
      if (g < vmin) vmin = g; if (r < vmin) vmin = r;
      var diff = v - vmin;
      var vr = v === r ? -1 : 0, vg = v === g ? -1 : 0;
      var s = (diff * SDIV[v] + 2048) >> 12;
      var h = (vr & (g - b)) + (~vr & ((vg & (b - r + 2 * diff)) + ((~vg) & (r - g + 4 * diff))));
      h = (h * HDIV[diff] + 2048) >> 12;
      if (h < 0) h += 180;
      H[p] = h; S[p] = s; V[p] = v;
    }
    return { H: H, S: S, V: V };
  }

  function inBox(hsv, n, box) {
    var m = new Uint8Array(n), lo = box.lower, up = box.upper;
    for (var p = 0; p < n; p++) {
      var h = hsv.H[p], s = hsv.S[p], v = hsv.V[p];
      if (h >= lo[0] && h <= up[0] && s >= lo[1] && s <= up[1] && v >= lo[2] && v <= up[2]) m[p] = 255;
    }
    return m;
  }

  // ------------------------------------------------- resize INTER_AREA
  function areaTab(ssize, dsize, scale) {
    var tab = [];
    for (var dx = 0; dx < dsize; dx++) {
      var fsx1 = dx * scale, fsx2 = fsx1 + scale;
      var cellWidth = Math.min(scale, ssize - fsx1);
      var sx1 = Math.ceil(fsx1), sx2 = Math.floor(fsx2);
      sx2 = Math.min(sx2, ssize - 1);
      sx1 = Math.min(sx1, sx2);
      var w = [];
      if (sx1 - fsx1 > 1e-3) w.push([sx1 - 1, Math.fround((sx1 - fsx1) / cellWidth)]);
      for (var sx = sx1; sx < sx2; sx++) w.push([sx, Math.fround(1.0 / cellWidth)]);
      if (fsx2 - sx2 > 1e-3) w.push([sx2, Math.fround(Math.min(Math.min(fsx2 - sx2, 1.0), cellWidth) / cellWidth)]);
      tab.push(w);
    }
    return tab;
  }

  /** cv2.resize(mask, (gw, gh), INTER_AREA) para uint8 (Uint8Array). */
  function resizeArea(src, w, h, gw, gh) {
    var out = new Float32Array(gw * gh);
    var sx = w / gw, sy = h / gh;
    if (Math.floor(sx) === sx && Math.floor(sy) === sy) {
      var area = sx * sy;
      for (var y = 0; y < gh; y++) for (var x = 0; x < gw; x++) {
        var sum = 0;
        for (var j = 0; j < sy; j++) {
          var row = (y * sy + j) * w + x * sx;
          for (var k = 0; k < sx; k++) sum += src[row + k];
        }
        out[y * gw + x] = Math.round(sum / area);
      }
      return out;
    }
    var tx = areaTab(w, gw, sx), ty = areaTab(h, gh, sy);
    for (var yy = 0; yy < gh; yy++) {
      var acc = new Float64Array(gw);
      for (var a = 0; a < ty[yy].length; a++) {
        var srow = ty[yy][a][0] * w, beta = ty[yy][a][1];
        for (var xx = 0; xx < gw; xx++) {
          var s = 0, wx = tx[xx];
          for (var b = 0; b < wx.length; b++) s += src[srow + wx[b][0]] * wx[b][1];
          acc[xx] += Math.fround(s) * beta;
        }
      }
      for (var x2 = 0; x2 < gw; x2++) out[yy * gw + x2] = Math.min(255, Math.max(0, Math.round(acc[x2])));
    }
    return out;
  }

  // ------------------------------------------------------- utilidades
  function reflect101(i, n) {
    if (n === 1) return 0;
    while (i < 0 || i >= n) { if (i < 0) i = -i; if (i >= n) i = 2 * n - 2 - i; }
    return i;
  }

  function median3(a, b, c) { return Math.max(Math.min(a, b), Math.min(Math.max(a, b), c)); }

  function medfilt3(y) {  // scipy.signal.medfilt, kernel 3, bordas com zero
    var n = y.length, o = new Float64Array(n);
    for (var i = 0; i < n; i++) o[i] = median3(i > 0 ? y[i - 1] : 0, y[i], i < n - 1 ? y[i + 1] : 0);
    return o;
  }

  function gaussian1d(y, sigma) {  // scipy.ndimage.gaussian_filter1d, mode reflect, truncate 4
    var r = Math.floor(4 * sigma + 0.5), wts = [], s = 0, k;
    for (k = -r; k <= r; k++) { var e = Math.exp(-0.5 * k * k / (sigma * sigma)); wts.push(e); s += e; }
    for (k = 0; k < wts.length; k++) wts[k] /= s;
    var n = y.length, o = new Float64Array(n);
    for (var i = 0; i < n; i++) {
      var acc = 0;
      for (k = -r; k <= r; k++) {
        var j = i + k;
        while (j < 0 || j >= n) { if (j < 0) j = -j - 1; if (j >= n) j = 2 * n - j - 1; }
        acc += wts[k + r] * y[j];
      }
      o[i] = Math.fround(acc);
    }
    return o;
  }

  function fillPolygon(mask, gw, gh, pts) {  // pontos inteiros; preenchimento par-ímpar por linha
    for (var y = 0; y < gh; y++) {
      var xs = [];
      for (var i = 0, j = pts.length - 1; i < pts.length; j = i++) {
        var yi = pts[i][1], yj = pts[j][1];
        if ((yi > y) !== (yj > y)) xs.push(pts[i][0] + (y - yi) * (pts[j][0] - pts[i][0]) / (yj - yi));
      }
      xs.sort(function (a, b) { return a - b; });
      for (var k = 0; k + 1 < xs.length; k += 2) {
        var x0 = Math.max(0, Math.ceil(xs[k] - 1e-9)), x1 = Math.min(gw - 1, Math.floor(xs[k + 1] + 1e-9));
        for (var x = x0; x <= x1; x++) mask[y * gw + x] = 255;
      }
    }
    // contorno (cv2.fillPoly também pinta as arestas)
    for (var a = 0, b2 = pts.length - 1; a < pts.length; b2 = a++) drawLine(mask, gw, gh, pts[b2], pts[a]);
  }

  function drawLine(mask, gw, gh, p, q) {
    var x0 = p[0], y0 = p[1], x1 = q[0], y1 = q[1];
    var dx = Math.abs(x1 - x0), dy = -Math.abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1, err = dx + dy;
    for (;;) {
      if (x0 >= 0 && x0 < gw && y0 >= 0 && y0 < gh) mask[y0 * gw + x0] = 255;
      if (x0 === x1 && y0 === y1) break;
      var e2 = 2 * err;
      if (e2 >= dy) { err += dy; x0 += sx; }
      if (e2 <= dx) { err += dx; y0 += sy; }
    }
  }

  // ------------------------------------------------------------ etapa 1
  /**
   * Etapa 1 original. imgRGBA: Uint8ClampedArray (canvas), w, h; caixas
   * {lower:[h,s,v], upper:[...]}. Retorna máscaras e esqueleto.
   */
  function stage1(rgba, w, h, green, white, opts) {
    opts = opts || {};
    var tpix = opts.tpix || 20, trow = opts.trow || 10000, twin = opts.twin || 3000;
    var n = w * h, gw = Math.floor(w / 8), gh = Math.floor(h / 8);
    var hsv = opts.hsv || rgbaToHsv(rgba, n);
    var wm = inBox(hsv, n, white), gm = inBox(hsv, n, green);
    var wr = resizeArea(wm, w, h, gw, gh), gr = resizeArea(gm, w, h, gw, gh);
    var G = gw * gh, uniq = new Uint8Array(G), x, y, i;
    for (i = 0; i < G; i++) {
      var u = Math.fround(Math.fround(wr[i] * 0.5) + gr[i]);
      uniq[i] = Math.min(255, Math.max(0, u)) | 0;
    }
    var rowSum = new Float64Array(gh);
    for (y = 0; y < gh; y++) { var s = 0; for (x = 0; x < gw; x++) s += uniq[y * gw + x]; rowSum[y] = s; }
    var rows1 = new Float64Array(gh);
    for (y = 0; y < gh; y++) rows1[y] = rowSum[y] + rowSum[(y - 1 + gh) % gh];
    rows1[0] = rowSum[0];
    var trowEf = trow * gw / 94;
    var borda = new Uint8Array(G);
    for (y = 0; y < gh; y++) for (x = 0; x < gw; x++) {
      var idx = y * gw + x;
      if (uniq[idx] < tpix) continue;
      var pass = rows1[y] >= trowEf;
      if (!pass) {
        var ws = 0;
        for (var dy = 0; dy < 4; dy++) {
          var yy = reflect101(y + dy, gh);
          for (var dx = -4; dx < 4; dx++) ws += uniq[yy * gw + reflect101(x + dx, gw)];
        }
        pass = ws >= twin;
      }
      if (pass) borda[idx] = 255;
    }
    var yDet = new Float64Array(gw).fill(NaN);
    for (x = 0; x < gw; x++) {
      var found = false, zeros = 0;
      for (y = gh - 1; y >= 0; y--) {
        if (borda[y * gw + x] === 255) { found = true; zeros = 0; yDet[x] = y; }
        else if (found) { zeros++; if (zeros >= 4) break; }
      }
    }
    var valid = [], nValid = 0;
    for (x = 0; x < gw; x++) if (!isNaN(yDet[x])) { valid.push(x); nValid++; }
    var minValid = Math.max(2, Math.floor(0.10 * gw));
    var detected = nValid >= minValid, yv = new Float64Array(gw);
    if (detected) {
      for (x = 0; x < gw; x++) {
        if (!isNaN(yDet[x])) { yv[x] = yDet[x]; continue; }
        if (x <= valid[0]) { yv[x] = yDet[valid[0]]; continue; }
        if (x >= valid[valid.length - 1]) { yv[x] = yDet[valid[valid.length - 1]]; continue; }
        var k2 = 0; while (valid[k2 + 1] < x) k2++;
        var xa = valid[k2], xb = valid[k2 + 1];
        yv[x] = Math.fround(yDet[xa] + (yDet[xb] - yDet[xa]) * (x - xa) / (xb - xa));
      }
    } else { for (x = 0; x < gw; x++) yv[x] = gh - 1; }
    var yg = gaussian1d(medfilt3(yv), 1.0);
    for (x = 0; x < gw; x++) yg[x] = Math.fround(Math.min(gh - 1, Math.max(0, yg[x])));
    var field = new Uint8Array(G), contour = [];
    if (detected) {
      var keep = new Array(gw).fill(true);
      for (i = 1; i < gw - 1; i++) {
        var v = (2) * (yg[i] - yg[i - 1]) - (1) * (yg[i + 1] - yg[i - 1]);
        if (v < 0) keep[i] = false;
      }
      for (x = 0; x < gw; x++) if (keep[x]) contour.push([x, Math.trunc(yg[x])]);
      contour.push([gw - 1, gh - 1]); contour.push([0, gh - 1]);
      if (contour.length >= 3) fillPolygon(field, gw, gh, contour);
    }
    // III-B: esqueleto
    var flm = new Uint8Array(G);
    for (i = 0; i < G; i++) flm[i] = (wr[i] & field[i]);
    var relief = gaussBlur5(flm, gw, gh);
    var skel = new Uint8Array(G), cxy = new Uint8Array(G);
    for (y = 0; y < gh; y++) for (x = 0; x < gw; x++) {
      var c = relief[y * gw + x], cnt = 0;
      for (var ny = -1; ny <= 1; ny++) for (var nx = -1; nx <= 1; nx++) {
        if (!nx && !ny) continue;
        var X = x + nx, Y = y + ny;
        var val = (X < 0 || Y < 0 || X >= gw || Y >= gh) ? 0 : relief[Y * gw + X];
        if (val >= c) cnt++;
      }
      cxy[y * gw + x] = cnt;
      if (c > 0 && cnt < 3 && x > 0 && y > 0 && x < gw - 1 && y < gh - 1) skel[y * gw + x] = 1;
    }
    return { w: w, h: h, gw: gw, gh: gh, hsv: hsv, whiteMask: wm, greenMask: gm, whiteResized: wr,
      greenResized: gr, uniq: uniq, borda: borda, fieldDetected: detected, contour: contour,
      field: field, relief: relief, skeleton: skel, yGauss: yg };
  }

  function gaussBlur5(src, gw, gh) {  // GaussianBlur 5x5, sigma 0 => [1 4 6 4 1]/16, reflect101, ponto fixo
    var k = [1, 4, 6, 4, 1], tmp = new Int32Array(gw * gh), out = new Uint8Array(gw * gh), x, y, j;
    for (y = 0; y < gh; y++) for (x = 0; x < gw; x++) {
      var s = 0;
      for (j = -2; j <= 2; j++) s += k[j + 2] * src[y * gw + reflect101(x + j, gw)];
      tmp[y * gw + x] = s;
    }
    for (y = 0; y < gh; y++) for (x = 0; x < gw; x++) {
      var t = 0;
      for (j = -2; j <= 2; j++) t += k[j + 2] * tmp[reflect101(y + j, gh) * gw + x];
      out[y * gw + x] = Math.min(255, (t + 128) >> 8);
    }
    return out;
  }

  // --------------------------------------------------------- estatística
  function percentile(sorted, q) {  // numpy, interpolação linear
    var n = sorted.length; if (!n) return NaN;
    var pos = (n - 1) * q / 100, lo = Math.floor(pos), hi = Math.ceil(pos);
    return sorted[lo] + (sorted[hi] - sorted[lo]) * (pos - lo);
  }
  function sortedCol(px, c) { var a = px.map(function (p) { return p[c]; }); a.sort(function (x, y) { return x - y; }); return a; }
  function median(a) { var s = a.slice().sort(function (x, y) { return x - y; }); return percentile(s, 50); }

  function otsu(values) {  // cv2.threshold(..., THRESH_OTSU) em uint8
    var hist = new Float64Array(256), N = values.length, i;
    for (i = 0; i < N; i++) hist[values[i]]++;
    var mu = 0; for (i = 0; i < 256; i++) mu += i * hist[i] / N;
    var q1 = 0, mu1 = 0, maxS = 0, maxV = 0, EPS = 1.1920929e-7;
    for (i = 0; i < 256; i++) {
      var p = hist[i] / N;
      mu1 *= q1; q1 += p; var q2 = 1 - q1;
      if (Math.min(q1, q2) < EPS || Math.max(q1, q2) > 1 - EPS) continue;
      mu1 = (mu1 + i * p) / q1;
      var mu2 = (mu - q1 * mu1) / q2, sg = q1 * q2 * (mu1 - mu2) * (mu1 - mu2);
      if (sg > maxS) { maxS = sg; maxV = i; }
    }
    return maxV;
  }

  var CMAX = [179, 255, 255];
  function mkBox(lo, up) {
    var L = [], U = [];
    for (var c = 0; c < 3; c++) {
      var a = Math.max(0, Math.min(CMAX[c], lo[c])), b = Math.max(0, Math.min(CMAX[c], up[c]));
      L.push(Math.min(a, b)); U.push(b);
    }
    return { lower: L, upper: U };
  }
  function boxContains(box, p) {
    return p[0] >= box.lower[0] && p[0] <= box.upper[0] && p[1] >= box.lower[1] && p[1] <= box.upper[1] && p[2] >= box.lower[2] && p[2] <= box.upper[2];
  }

  var PARAMS = { greenPct: [1, 99], greenMargin: [4, 25, 30], greenMadK: 3.5, greenFloor: [0, 30, 15],
    whitePct: [5, 95], whiteMargin: [0, 8, 8], whiteMinKept: 8 };

  function proposeGreen(px) {
    if (!px.length) throw new Error('sem amostras de verde');
    var p = px.filter(function (q) { return q[2] >= PARAMS.greenFloor[2]; });
    if (p.length < 8) p = px;
    var med = [], mad = [], c;
    for (c = 0; c < 3; c++) {
      var col = p.map(function (q) { return q[c]; });
      med.push(median(col));
      mad.push(Math.max(2.0, 1.4826 * median(col.map(function (v) { return Math.abs(v - med[c]); }))));
    }
    var inl = p.filter(function (q) { for (var k = 0; k < 3; k++) if (Math.abs(q[k] - med[k]) > PARAMS.greenMadK * mad[k]) return false; return true; });
    if (inl.length >= Math.max(8, 0.5 * p.length)) p = inl;
    var lo = [], up = [];
    for (c = 0; c < 3; c++) {
      var s = sortedCol(p, c);
      lo.push(Math.floor(Math.max(percentile(s, PARAMS.greenPct[0]) - PARAMS.greenMargin[c], PARAMS.greenFloor[c])));
      up.push(Math.ceil(percentile(s, PARAMS.greenPct[1]) + PARAMS.greenMargin[c]));
    }
    up[1] = 255;
    return mkBox(lo, up);
  }

  function filterWhite(px, green) {
    var p = green ? px.filter(function (q) { return !boxContains(green, q); }) : px.slice();
    if (p.length >= 8) {
      var vs = p.map(function (q) { return q[2]; });
      var mx = Math.max.apply(null, vs), mn = Math.min.apply(null, vs);
      if (mx - mn > 30) { var thr = otsu(vs); p = p.filter(function (q) { return q[2] > thr; }); }
    }
    return p;
  }

  function proposeWhite(px, green) {
    var p = filterWhite(px, green);
    if (p.length < PARAMS.whiteMinKept) p = px;
    if (!p.length) throw new Error('sem amostras de branco');
    var lo = [], up = [];
    for (var c = 0; c < 3; c++) {
      var s = sortedCol(p, c);
      lo.push(Math.floor(percentile(s, PARAMS.whitePct[0]) - PARAMS.whiteMargin[c]));
      up.push(Math.ceil(percentile(s, PARAMS.whitePct[1]) + PARAMS.whiteMargin[c]));
    }
    lo[0] = 0; up[0] = 179; lo[1] = 0; up[2] = 255;
    return mkBox(lo, up);
  }

  // ------------------------------------------------------------ CSVs
  function vendorBound(mean, std, cmax) {
    var a = Math.max(0, Math.min(cmax, mean - 2 * std)), b = Math.max(0, Math.min(cmax, mean + 2 * std));
    return [Math.trunc(a), Math.trunc(b)];
  }

  function solveChannel(lo, up, cmax, n) {
    var arr;
    if (lo === up) { arr = new Array(n).fill(lo); return arr; }
    var mT = (lo + up + 1) / 2, sT = (up - lo) / 4;
    for (var a = Math.max(0, Math.trunc(mT - sT) - 3); a <= Math.min(cmax, Math.trunc(mT - sT) + 3); a++) {
      for (var b = Math.max(0, Math.trunc(mT + sT) - 3); b <= Math.min(cmax, Math.trunc(mT + sT) + 3); b++) {
        if (b <= a) continue;
        var best = -1, bestErr = Infinity, bm = 0, bs = 0;
        for (var na = 1; na < n; na++) {
          var nb = n - na, mean = (na * a + nb * b) / n;
          var std = Math.sqrt((na * (a - mean) * (a - mean) + nb * (b - mean) * (b - mean)) / (n - 1));
          var err = Math.abs(mean - mT) + Math.abs(std - sT);
          if (err < bestErr) { bestErr = err; best = na; bm = mean; bs = std; }
        }
        var vb = vendorBound(bm, bs, cmax);
        if (vb[0] === lo && vb[1] === up) {
          arr = []; for (var i = 0; i < n; i++) arr.push(i < best ? a : b); return arr;
        }
      }
    }
    for (var spread = 0; spread <= cmax; spread++) {
      var l = Math.max(0, lo - spread), u = Math.min(cmax, up + spread);
      arr = []; var sum = 0;
      for (var j = 0; j < n; j++) { var vv = Math.round(l + (u - l) * j / (n - 1)); arr.push(vv); sum += vv; }
      var m = sum / n, ss = 0; for (j = 0; j < n; j++) ss += (arr[j] - m) * (arr[j] - m);
      var bb = vendorBound(m, Math.sqrt(ss / (n - 1)), cmax);
      if (bb[0] === lo && bb[1] === up) return arr;
    }
    return null;
  }

  function whiteRows(box) {
    for (var n = 400; n < 800; n += 7) {
      var cols = [];
      for (var c = 0; c < 3; c++) { var col = solveChannel(box.lower[c], box.upper[c], CMAX[c], n); if (!col) break; cols.push(col); }
      if (cols.length === 3) {
        var seed = 12345;  // embaralhamento determinístico (LCG)
        var rnd = function () { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
        cols.forEach(function (cl) { for (var i = cl.length - 1; i > 0; i--) { var j = Math.floor(rnd() * (i + 1)); var t = cl[i]; cl[i] = cl[j]; cl[j] = t; } });
        var rows = []; for (var r = 0; r < n; r++) rows.push([cols[0][r], cols[1][r], cols[2][r]]);
        return rows;
      }
    }
    throw new Error('nao consegui sintetizar o branco');
  }

  function whiteCsv(box) {
    return 'H,S,V,class\n' + whiteRows(box).map(function (r) { return r.join(',') + ',branco'; }).join('\n') + '\n';
  }

  function greenCsvParts(box) {  // lista de pedaços de texto (para Blob), todas as tríades
    var parts = ['H,S,V\n'];
    for (var h = box.lower[0]; h <= box.upper[0]; h++) for (var s = box.lower[1]; s <= box.upper[1]; s++) {
      var buf = [];
      for (var v = box.lower[2]; v <= box.upper[2]; v++) buf.push(h + ',' + s + ',' + v);
      parts.push(buf.join('\n') + '\n');
    }
    return parts;
  }

  // ------------------------------------------------------ métricas
  function boundaryBand(r, rows) {
    var band = new Uint8Array(r.gw * r.gh);
    if (!r.fieldDetected) return band;
    for (var x = 0; x < r.gw; x++) {
      for (var y = 0; y < r.gh; y++) if (r.field[y * r.gw + x]) {
        for (var k = y; k < Math.min(r.gh, y + rows); k++) band[k * r.gw + x] = 1;
        break;
      }
    }
    return band;
  }

  function fullFromGrid(r, gridMask) {  // INTER_NEAREST para a resolução cheia
    var out = new Uint8Array(r.w * r.h), sx = r.gw / r.w, sy = r.gh / r.h;
    for (var y = 0; y < r.h; y++) {
      var gy = Math.min(r.gh - 1, Math.floor(y * sy));
      for (var x = 0; x < r.w; x++) out[y * r.w + x] = gridMask[gy * r.gw + Math.min(r.gw - 1, Math.floor(x * sx))] ? 1 : 0;
    }
    return out;
  }

  function sanity(r) {
    var ff = fullFromGrid(r, r.field), area = 0, gin = 0, win = 0, nw = 0, n = r.w * r.h, i;
    for (i = 0; i < n; i++) {
      var f = ff[i]; if (f) area++;
      if (r.greenMask[i] && f) gin++;
      if (r.whiteMask[i]) { nw++; if (f) win++; }
    }
    var band = boundaryBand(r, 2), nb = 0, wb = 0;
    for (i = 0; i < band.length; i++) if (band[i]) { nb++; if (r.whiteResized[i] >= 64) wb++; }
    var nsk = 0; for (i = 0; i < r.skeleton.length; i++) nsk += r.skeleton[i];
    var m = { campo_detectado: r.fieldDetected, verde_no_campo: area ? gin / area : 0,
      branco_cobre_campo: area ? win / area : 0, branco_dentro_campo: nw ? win / nw : 0,
      branco_na_fronteira: nb ? wb / nb : 0, pixels_esqueleto: nsk, avisos: [] };
    if (!m.campo_detectado) m.avisos.push('campo NAO detectado: amostre mais verde (sombras e claros)');
    else {
      if (m.verde_no_campo < 0.55) m.avisos.push('pouco verde no campo: faixa do verde estreita');
      if (m.branco_cobre_campo > 0.20) m.avisos.push('branco demais no campo: suba V min / baixe S max');
      if (m.branco_na_fronteira > 0.25) m.avisos.push('branco encostado na fronteira (placas/parede): botao "Sugerir V min" (A)');
      if (nsk < 15) m.avisos.push('quase sem esqueleto: faixa do branco estreita?');
    }
    m.ok = m.campo_detectado && m.avisos.length === 0;
    return m;
  }

  function suggestVmin(r) {
    var band = boundaryBand(r, 2), G = r.gw * r.gh, lab = new Int32Array(G), i, nl = 0;
    var wg = new Uint8Array(G);
    for (i = 0; i < G; i++) wg[i] = (r.whiteResized[i] >= 64 && r.field[i]) ? 1 : 0;
    var touching = {};
    for (i = 0; i < G; i++) if (wg[i] && !lab[i]) {
      nl++; var st = [i]; lab[i] = nl;
      while (st.length) {
        var p = st.pop(), px = p % r.gw, py = (p - px) / r.gw;
        if (band[p]) touching[nl] = true;
        for (var dy = -1; dy <= 1; dy++) for (var dx = -1; dx <= 1; dx++) {
          var X = px + dx, Y = py + dy;
          if (X < 0 || Y < 0 || X >= r.gw || Y >= r.gh) continue;
          var q = Y * r.gw + X;
          if (wg[q] && !lab[q]) { lab[q] = nl; st.push(q); }
        }
      }
    }
    var bg = new Uint8Array(G), any = false;
    for (i = 0; i < G; i++) if (lab[i] && touching[lab[i]]) { bg[i] = 1; any = true; }
    if (!any) return null;
    var bgF = fullFromGrid(r, bg), fF = fullFromGrid(r, r.field), vb = [], vi = [];
    for (i = 0; i < r.w * r.h; i++) if (r.whiteMask[i]) {
      if (bgF[i]) vb.push(r.hsv.V[i]); else if (fF[i]) vi.push(r.hsv.V[i]);
    }
    if (vb.length < 20 || vi.length < 20) return null;
    var cand = Math.min(255, Math.trunc(median(vb) + 1)), above = 0;
    for (i = 0; i < vi.length; i++) if (vi[i] >= cand) above++;
    if (above / vi.length < 0.4) return null;
    return cand;
  }

  var api = { rgbaToHsv: rgbaToHsv, inBox: inBox, resizeArea: resizeArea, stage1: stage1, gaussBlur5: gaussBlur5,
    medfilt3: medfilt3, gaussian1d: gaussian1d, proposeGreen: proposeGreen, proposeWhite: proposeWhite,
    filterWhite: filterWhite, otsu: otsu, whiteRows: whiteRows, whiteCsv: whiteCsv, greenCsvParts: greenCsvParts,
    sanity: sanity, suggestVmin: suggestVmin, mkBox: mkBox, PARAMS: PARAMS };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.RLV = api;
})(this);
