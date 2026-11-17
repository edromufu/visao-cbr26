"""
Núcleo da calibração de cor (sem interface gráfica).

Modelo de cor
-------------
* **Verde (carpete):** uma caixa HSV ``[lower, upper]``. O ``green_pixels.csv``
  gerado é **denso**: todas as tríades ``H,S,V`` dentro da caixa, porque a
  etapa 1 usa uma LUT exata (só as tríades listadas são verde).
* **Branco (linha):** outra caixa HSV. A etapa 1 calcula o limiar a partir do
  ``white_pixels.csv`` com média ± 2·desvio por canal. Para que o CSV
  reproduza exatamente a caixa escolhida (inclusive após ajuste fino nos
  deslizadores), as linhas do CSV são *amostras equivalentes* sintetizadas
  (ver :func:`white_rows_for_range`); as amostras reais ficam no JSON.

Os limites propostos saem das amostras por percentis com margem; o branco é
filtrado antes (exclui pixels que caem na caixa do verde e separa claro/escuro
por Otsu no canal V), porque pinceladas sobre linhas finas pegam carpete.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import datetime as _dt
import json
from pathlib import Path
import shutil
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import cv2
import numpy as np

H_MAX = 179
SV_MAX = 255
CHANNEL_MAX = (H_MAX, SV_MAX, SV_MAX)


@dataclass
class HSVRange:
    """Caixa HSV fechada ``lower <= pixel <= upper`` (convenção do OpenCV)."""

    lower: Tuple[int, int, int]
    upper: Tuple[int, int, int]

    def __post_init__(self) -> None:
        lo = tuple(int(np.clip(v, 0, m)) for v, m in zip(self.lower, CHANNEL_MAX))
        up = tuple(int(np.clip(v, 0, m)) for v, m in zip(self.upper, CHANNEL_MAX))
        lo = tuple(min(a, b) for a, b in zip(lo, up))
        self.lower = lo  # type: ignore[assignment]
        self.upper = up  # type: ignore[assignment]

    def mask(self, hsv: np.ndarray) -> np.ndarray:
        """Máscara uint8 0/255 dos pixels dentro da caixa."""
        return cv2.inRange(hsv, np.array(self.lower, dtype=np.uint8),
                           np.array(self.upper, dtype=np.uint8))

    def contains(self, hsv_pixels: np.ndarray) -> np.ndarray:
        """Vetor booleano para pixels ``(N, 3)``."""
        p = np.asarray(hsv_pixels).reshape(-1, 3)
        lo = np.array(self.lower)
        up = np.array(self.upper)
        return np.all((p >= lo) & (p <= up), axis=1)

    def n_triads(self) -> int:
        """Quantidade de tríades inteiras dentro da caixa."""
        return int(np.prod([u - lo + 1 for lo, u in zip(self.lower, self.upper)]))

    def to_dict(self) -> Dict[str, List[int]]:
        """Representação JSON."""
        return {'lower': list(self.lower), 'upper': list(self.upper)}

    @staticmethod
    def from_dict(d: Dict[str, Sequence[int]]) -> 'HSVRange':
        """Inverso de :meth:`to_dict`."""
        return HSVRange(tuple(d['lower']), tuple(d['upper']))  # type: ignore[arg-type]


@dataclass
class ProposalParams:
    """Percentis e margens usados para propor as caixas a partir de amostras."""

    green_pct: Tuple[float, float] = (1.0, 99.0)
    green_margin: Tuple[int, int, int] = (4, 25, 30)
    green_s_upper_full: bool = True     # S do verde vai até 255
    green_mad_k: float = 3.5             # rejeição robusta (mediana ± k·MAD)
    green_floor: Tuple[int, int, int] = (0, 30, 15)  # S e V mínimos do verde
    white_pct: Tuple[float, float] = (5.0, 95.0)
    white_margin: Tuple[int, int, int] = (0, 8, 8)
    white_h_full: bool = True            # matiz do branco é indefinida: H 0..179
    white_v_upper_full: bool = True      # V do branco vai até 255
    white_min_kept: int = 8              # mínimo de pixels após a filtragem


def robust_inliers(p: np.ndarray, k: float) -> np.ndarray:
    """Máscara dos pixels dentro de mediana ± k·1,4826·MAD em todos os canais."""
    p = np.asarray(p, dtype=float)
    med = np.median(p, axis=0)
    mad = 1.4826 * np.median(np.abs(p - med), axis=0)
    mad = np.maximum(mad, 2.0)
    return np.all(np.abs(p - med) <= k * mad, axis=1)


def propose_green_range(samples_hsv: np.ndarray,
                        params: ProposalParams = ProposalParams()) -> HSVRange:
    """
    Caixa do verde a partir de amostras do carpete.

    Descarta pixels quase pretos (V < piso), rejeita outliers por MAD (cantos
    escuros, robôs, linhas pegos sem querer) e usa percentis com margem.
    """
    p = np.asarray(samples_hsv).reshape(-1, 3).astype(float)
    if len(p) == 0:
        raise ValueError('sem amostras de verde')
    keep = p[:, 2] >= params.green_floor[2]
    if keep.sum() >= 8:
        p = p[keep]
    inl = robust_inliers(p, params.green_mad_k)
    if inl.sum() >= max(8, 0.5 * len(p)):
        p = p[inl]
    lo = np.percentile(p, params.green_pct[0], axis=0) - np.array(params.green_margin)
    up = np.percentile(p, params.green_pct[1], axis=0) + np.array(params.green_margin)
    lo = np.maximum(lo, np.array(params.green_floor, dtype=float))
    if params.green_s_upper_full:
        up[1] = SV_MAX
    return HSVRange(tuple(int(np.floor(v)) for v in lo), tuple(int(np.ceil(v)) for v in up))


def filter_white_candidates(samples_hsv: np.ndarray,
                            green: Optional[HSVRange] = None) -> np.ndarray:
    """
    Remove das amostras de branco o que é carpete ou borda escura.

    1. descarta pixels dentro da caixa do verde (se houver);
    2. se o canal V for bimodal, aplica Otsu e fica só com a parte clara.
    """
    p = np.asarray(samples_hsv).reshape(-1, 3)
    if len(p) == 0:
        return p
    if green is not None:
        p = p[~green.contains(p)]
    if len(p) >= 8:
        v = p[:, 2].astype(np.uint8).reshape(-1, 1)
        if int(v.max()) - int(v.min()) > 30:
            thr, _ = cv2.threshold(v, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            p = p[p[:, 2] > thr]
    return p


def propose_white_range(samples_hsv: np.ndarray, green: Optional[HSVRange] = None,
                        params: ProposalParams = ProposalParams()) -> HSVRange:
    """Caixa do branco a partir de amostras de linha (já filtradas aqui)."""
    p = filter_white_candidates(samples_hsv, green)
    if len(p) < params.white_min_kept:
        p = np.asarray(samples_hsv).reshape(-1, 3)
    if len(p) == 0:
        raise ValueError('sem amostras de branco')
    p = p.astype(float)
    lo = np.percentile(p, params.white_pct[0], axis=0) - np.array(params.white_margin)
    up = np.percentile(p, params.white_pct[1], axis=0) + np.array(params.white_margin)
    if params.white_h_full:
        lo[0], up[0] = 0, H_MAX
    lo[1] = 0  # menos saturado que as amostras continua sendo branco
    if params.white_v_upper_full:
        up[2] = SV_MAX
    return HSVRange(tuple(int(np.floor(v)) for v in lo), tuple(int(np.ceil(v)) for v in up))


# --------------------------------------------------------------------------
# CSVs no formato que a etapa 1 lê
# --------------------------------------------------------------------------

def dense_green_triads(rng: HSVRange) -> np.ndarray:
    """Todas as tríades ``(H, S, V)`` inteiras dentro da caixa, ``(N, 3)``."""
    axes = [np.arange(lo, up + 1, dtype=np.int32) for lo, up in zip(rng.lower, rng.upper)]
    grid = np.stack(np.meshgrid(*axes, indexing='ij'), axis=-1)
    return grid.reshape(-1, 3)


def _write_int_csv(path: Path, header: str, rows: np.ndarray,
                   suffix: str = '') -> None:
    """Grava CSV de inteiros rápido (sem pandas)."""
    rows = np.asarray(rows, dtype=np.int64)
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(header + '\n')
        if len(rows):
            lines = (','.join(map(str, r)) + suffix for r in rows.tolist())
            fh.write('\n'.join(lines))
            fh.write('\n')


def write_green_csv(path: Path, rng: HSVRange) -> int:
    """Grava ``green_pixels.csv`` denso (colunas ``H,S,V``). Devolve N."""
    rows = dense_green_triads(rng)
    _write_int_csv(Path(path), 'H,S,V', rows)
    return len(rows)


def _vendor_bound(mean: float, std: float, cmax: int) -> Tuple[int, int]:
    """Mesma conta do ``def_white_threshold.py`` (fator 2, clip, int)."""
    lo = int(np.array([np.clip(mean - 2 * std, 0, cmax)], int)[0])
    up = int(np.array([np.clip(mean + 2 * std, 0, cmax)], int)[0])
    return lo, up


def _solve_channel(lo: int, up: int, cmax: int, n: int) -> Optional[np.ndarray]:
    """Procura n inteiros cuja média ± 2·desvio (ddof=1) dê ``[lo, up]``."""
    if lo == up:
        return np.full(n, lo, dtype=np.int64)
    m_target = (lo + up + 1) / 2.0
    s_target = (up - lo) / 4.0
    cands_a = range(max(0, int(m_target - s_target) - 3),
                    min(cmax, int(m_target - s_target) + 4) + 1)
    cands_b = range(max(0, int(m_target + s_target) - 3),
                    min(cmax, int(m_target + s_target) + 4) + 1)
    na = np.arange(1, n)
    for a in cands_a:
        for b in cands_b:
            if b <= a:
                continue
            nb = n - na
            mean = (na * a + nb * b) / n
            var = (na * (a - mean) ** 2 + nb * (b - mean) ** 2) / (n - 1)
            std = np.sqrt(var)
            for k in np.argsort(np.abs(mean - m_target) + np.abs(std - s_target)):
                if _vendor_bound(float(mean[k]), float(std[k]), cmax) == (lo, up):
                    vals = np.concatenate([np.full(na[k], a), np.full(nb[k], b)])
                    return vals.astype(np.int64)
                break  # só o melhor candidato deste par
    # Caso degenerado (limites no extremo): espalha uniformemente e confere.
    for spread in range(0, cmax + 1):
        vals = np.linspace(max(0, lo - spread), min(cmax, up + spread), n).round().astype(np.int64)
        m, s = float(vals.mean()), float(vals.std(ddof=1))
        if _vendor_bound(m, s, cmax) == (lo, up):
            return vals
    return None


def white_rows_for_range(rng: HSVRange, n_start: int = 400) -> np.ndarray:
    """
    Linhas ``(N, 3)`` cujo limiar pela fórmula original é exatamente ``rng``.

    A fórmula original é ``int(clip(média ± 2·desvio))`` por canal. Cada
    canal é resolvido separadamente com dois níveis inteiros ``a < b`` e
    contagens ajustadas; as colunas são embaralhadas de forma determinística.
    """
    for n in range(n_start, n_start + 400, 7):
        cols = []
        for lo, up, cmax in zip(rng.lower, rng.upper, CHANNEL_MAX):
            col = _solve_channel(int(lo), int(up), cmax, n)
            if col is None:
                break
            cols.append(col)
        if len(cols) == 3:
            gen = np.random.default_rng(12345)
            cols = [c[gen.permutation(n)] for c in cols]
            return np.stack(cols, axis=1)
    raise RuntimeError(f'não consegui sintetizar amostras para {rng}')


def write_white_csv(path: Path, rng: HSVRange) -> int:
    """Grava ``white_pixels.csv`` (``H,S,V,class``) que reproduz ``rng``."""
    rows = white_rows_for_range(rng)
    _write_int_csv(Path(path), 'H,S,V,class', rows, suffix=',branco')
    return len(rows)


# --------------------------------------------------------------------------
# Amostras
# --------------------------------------------------------------------------

@dataclass
class Sample:
    """Uma marcação da usuária sobre uma imagem."""

    classe: str                 # 'verde' ou 'branco'
    tipo: str                   # 'pincel', 'retangulo' ou 'clique'
    imagem: str                 # nome da imagem de origem
    pontos: List[Tuple[int, int]] = field(default_factory=list)  # pincel/clique
    raio: int = 0
    retangulo: Optional[Tuple[int, int, int, int]] = None        # x0, y0, x1, y1

    def mask(self, shape: Tuple[int, int]) -> np.ndarray:
        """Máscara uint8 da região marcada numa imagem ``shape = (h, w)``."""
        m = np.zeros(shape, dtype=np.uint8)
        if self.tipo == 'retangulo' and self.retangulo is not None:
            x0, y0, x1, y1 = self.retangulo
            x0, x1 = sorted((int(x0), int(x1)))
            y0, y1 = sorted((int(y0), int(y1)))
            m[max(0, y0):y1 + 1, max(0, x0):x1 + 1] = 255
        else:
            r = max(1, int(self.raio))
            pts = [(int(x), int(y)) for x, y in self.pontos]
            for p in pts:
                cv2.circle(m, p, r, 255, -1)
            for p, q in zip(pts[:-1], pts[1:]):
                cv2.line(m, p, q, 255, 2 * r + 1)
        return m

    def pixels(self, hsv: np.ndarray) -> np.ndarray:
        """Pixels HSV ``(N, 3)`` cobertos pela marcação."""
        return hsv[self.mask(hsv.shape[:2]) > 0]

    def to_dict(self) -> Dict[str, Any]:
        """Representação JSON."""
        d = asdict(self)
        d['pontos'] = [list(p) for p in self.pontos]
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Sample':
        """Inverso de :meth:`to_dict`."""
        return Sample(classe=d['classe'], tipo=d['tipo'], imagem=d.get('imagem', ''),
                      pontos=[tuple(p) for p in d.get('pontos', [])],  # type: ignore[misc]
                      raio=int(d.get('raio', 0)),
                      retangulo=tuple(d['retangulo']) if d.get('retangulo') else None)  # type: ignore[arg-type]


def gather(samples: Iterable[Sample], images_hsv: Dict[str, np.ndarray],
           classe: str) -> np.ndarray:
    """Junta os pixels HSV de todas as amostras de uma classe."""
    chunks = [s.pixels(images_hsv[s.imagem]) for s in samples
              if s.classe == classe and s.imagem in images_hsv]
    chunks = [c for c in chunks if len(c)]
    if not chunks:
        return np.empty((0, 3), dtype=np.uint8)
    return np.concatenate(chunks, axis=0)


def quick_click_radius(image_width: int, classe: str) -> int:
    """Raio padrão do clique da recalibração rápida, proporcional à largura."""
    if classe == 'verde':
        return max(6, int(round(0.025 * image_width)))
    return max(3, int(round(0.008 * image_width)))


# --------------------------------------------------------------------------
# Calibração completa e salvamento versionado
# --------------------------------------------------------------------------

@dataclass
class Calibration:
    """Calibração completa (o que vai para ``calib_<data>.json``)."""

    green: HSVRange
    white: HSVRange
    samples: List[Sample] = field(default_factory=list)
    imagens: List[str] = field(default_factory=list)
    criada_em: str = ''
    resolucao: Optional[Tuple[int, int]] = None   # (largura, altura)
    metricas: Dict[str, Any] = field(default_factory=dict)
    ajuste_manual: bool = False
    observacoes: str = ''

    def to_dict(self) -> Dict[str, Any]:
        """Representação JSON (versão 1)."""
        return {
            'versao': 1,
            'formato': 'robocup_line_vision.calib',
            'criada_em': self.criada_em,
            'imagens': list(self.imagens),
            'resolucao': list(self.resolucao) if self.resolucao else None,
            'verde': self.green.to_dict(),
            'branco': self.white.to_dict(),
            'ajuste_manual': bool(self.ajuste_manual),
            'amostras': [s.to_dict() for s in self.samples],
            'metricas': self.metricas,
            'observacoes': self.observacoes,
            'arquivos': {'verde': 'green_pixels.csv', 'branco': 'white_pixels.csv'},
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Calibration':
        """Inverso de :meth:`to_dict`."""
        return Calibration(
            green=HSVRange.from_dict(d['verde']), white=HSVRange.from_dict(d['branco']),
            samples=[Sample.from_dict(s) for s in d.get('amostras', [])],
            imagens=list(d.get('imagens', [])), criada_em=d.get('criada_em', ''),
            resolucao=tuple(d['resolucao']) if d.get(
                'resolucao') else None,  # type: ignore[arg-type]
            metricas=d.get('metricas', {}), ajuste_manual=bool(d.get('ajuste_manual', False)),
            observacoes=d.get('observacoes', ''))


def calibration_from_samples(samples: Sequence[Sample], images_bgr: Dict[str, np.ndarray],
                             params: ProposalParams = ProposalParams()) -> Calibration:
    """Propõe a calibração completa a partir das amostras marcadas."""
    hsv = {k: cv2.cvtColor(v, cv2.COLOR_BGR2HSV) for k, v in images_bgr.items()}
    g = gather(samples, hsv, 'verde')
    w = gather(samples, hsv, 'branco')
    green = propose_green_range(g, params)
    white = propose_white_range(w, green, params)
    any_img = next(iter(images_bgr.values()))
    return Calibration(green=green, white=white, samples=list(samples),
                       imagens=sorted({s.imagem for s in samples}),
                       resolucao=(int(any_img.shape[1]), int(any_img.shape[0])))


def save_calibration(calib: Calibration, out_root: Path,
                     source_frames: Optional[Dict[str, np.ndarray]] = None,
                     now: Optional[_dt.datetime] = None) -> Path:
    """
    Salva em ``out_root/calib_<AAAAMMDD_HHMMSS>/`` e atualiza ``ultima/``.

    Nunca sobrescreve uma calibração anterior: se a pasta já existir, acrescenta
    um sufixo ``_2``, ``_3``... A pasta ``ultima/`` é uma cópia da mais recente
    (cópia, não link, para funcionar no Windows/WSL).
    """
    out_root = Path(out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    now = now or _dt.datetime.now()
    stamp = now.strftime('%Y%m%d_%H%M%S')
    target = out_root / f'calib_{stamp}'
    k = 2
    while target.exists():
        target = out_root / f'calib_{stamp}_{k}'
        k += 1
    target.mkdir(parents=True)
    calib.criada_em = now.isoformat(timespec='seconds')
    n_green = write_green_csv(target / 'green_pixels.csv', calib.green)
    n_white = write_white_csv(target / 'white_pixels.csv', calib.white)
    d = calib.to_dict()
    d['n_triades_verde'] = n_green
    d['n_linhas_branco'] = n_white
    d['pasta'] = target.name
    if source_frames:
        frames_dir = target / 'frames'
        frames_dir.mkdir()
        for name, img in source_frames.items():
            safe = Path(name).stem + '.png'
            cv2.imwrite(str(frames_dir / safe), img)
        d['frames_salvos'] = sorted(p.name for p in frames_dir.iterdir())
    with open(target / f'calib_{stamp}.json', 'w', encoding='utf-8') as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2)
    latest = out_root / 'ultima'
    tmp = out_root / '.ultima_tmp'
    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(target, tmp)
    with open(tmp / 'calib.json', 'w', encoding='utf-8') as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2)
    if latest.exists():
        shutil.rmtree(latest)
    tmp.rename(latest)
    return target


def load_calibration_dir(path: Path) -> Tuple[Calibration, Path, Path]:
    """
    Lê uma pasta de calibração (``ultima/`` ou ``calib_*``).

    Devolve ``(calibração, green_csv, white_csv)``.
    """
    path = Path(path)
    jsons = sorted(path.glob('calib*.json'))
    if not jsons:
        raise FileNotFoundError(f'nenhum calib*.json em {path}')
    with open(jsons[0], encoding='utf-8') as fh:
        calib = Calibration.from_dict(json.load(fh))
    return calib, path / 'green_pixels.csv', path / 'white_pixels.csv'


# --------------------------------------------------------------------------
# Métricas de sanidade
# --------------------------------------------------------------------------

@dataclass
class SanityThresholds:
    """Limiares das métricas de sanidade (heurísticos, documentados)."""

    min_green_in_field: float = 0.55   # verde / área do campo
    max_white_cover: float = 0.20      # branco dentro do campo / área do campo
    min_white_in_field: float = 0.30   # branco dentro / branco total
    min_skeleton_px: int = 15
    max_white_at_boundary: float = 0.25  # células brancas logo abaixo da fronteira
    band_rows: int = 2                   # altura (células) da faixa da fronteira


def boundary_band(stage1: Any, rows: int = 2) -> np.ndarray:
    """
    Máscara (grade) das ``rows`` primeiras células do campo em cada coluna.

    Se essa faixa é branca, o "branco" é fundo (placas, parede, gol) que puxou
    a fronteira do campo para cima, e não linha do campo.
    """
    fm = stage1.field_mask > 0
    band = np.zeros_like(fm)
    if not stage1.field_detected:
        return band
    gh, gw = fm.shape
    for x in range(gw):
        ys = np.flatnonzero(fm[:, x])
        if len(ys):
            band[ys[0]:min(gh, ys[0] + rows), x] = True
    return band


def suggest_white_vmin(stage1: Any, hsv: np.ndarray, rows: int = 2) -> Optional[int]:
    """
    Sugere um V mínimo do branco que tira o fundo branco da fronteira.

    "Fundo" = componentes conexos de branco (na grade, dentro do campo) que
    tocam a faixa da fronteira (placas, parede, gol). "Linhas" = o resto do
    branco do campo. Propõe ``mediana(V do fundo) + 1``, só se pelo menos
    40 % do branco das linhas continuar acima disso (senão as linhas sumiriam
    junto). A mediana ignora a minoria muito clara do fundo (pés das traves).
    """
    band = boundary_band(stage1, rows)
    if not band.any():
        return None
    wgrid = ((stage1.white_resized >= 64) & (stage1.field_mask > 0)).astype(np.uint8)
    n, lab = cv2.connectedComponents(wgrid, connectivity=8)
    touching = set(np.unique(lab[band & (wgrid > 0)]).tolist()) - {0}
    if not touching:
        return None
    bg = np.isin(lab, list(touching))
    h, w = stage1.white_mask.shape
    bg_full = cv2.resize(bg.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST) > 0
    white = stage1.white_mask > 0
    inner = white & (stage1.field_mask_full > 0) & ~bg_full
    vb = hsv[..., 2][white & bg_full]
    vi = hsv[..., 2][inner]
    if len(vb) < 20 or len(vi) < 20:
        return None
    cand = int(min(255, np.median(vb) + 1))
    if np.mean(vi >= cand) < 0.4:
        return None
    return cand


def sanity_metrics(stage1: Any, thr: SanityThresholds = SanityThresholds()) -> Dict[str, Any]:
    """
    Métricas para validar a calibração na hora (resolução cheia).

    * ``verde_no_campo``: fração da área do campo detectado que é verde;
    * ``branco_cobre_campo``: fração da área do campo que é branca (alto demais
      = faixa do branco larga, pegando carpete);
    * ``branco_dentro_campo``: fração do branco total que está dentro do campo
      (baixo = céu/parede/placas entrando como branco; informativo);
    * ``verde_fora_campo``: fração do verde total fora do campo (informativo).
    """
    field_m = stage1.field_mask_full > 0
    area = int(field_m.sum())
    green = stage1.green_mask > 0
    white = stage1.white_mask > 0
    n_green = int(green.sum())
    n_white = int(white.sum())
    out: Dict[str, Any] = {
        'campo_detectado': bool(stage1.field_detected),
        'area_campo_frac': area / float(field_m.size),
        'verde_no_campo': (int((green & field_m).sum()) / area) if area else 0.0,
        'branco_cobre_campo': (int((white & field_m).sum()) / area) if area else 0.0,
        'branco_dentro_campo': (int((white & field_m).sum()) / n_white) if n_white else 0.0,
        'verde_fora_campo': (int((green & ~field_m).sum()) / n_green) if n_green else 0.0,
        'pixels_esqueleto': int(np.count_nonzero(stage1.skeleton)),
    }
    band = boundary_band(stage1, thr.band_rows)
    nb = int(band.sum())
    out['branco_na_fronteira'] = (float((stage1.white_resized[band] >= 64).mean()) if nb else 0.0)
    avisos = []
    if not out['campo_detectado']:
        avisos.append('campo NAO detectado: amostre mais verde (sombras e claros)')
    else:
        if out['verde_no_campo'] < thr.min_green_in_field:
            avisos.append('pouco verde no campo: faixa do verde estreita')
        if out['branco_cobre_campo'] > thr.max_white_cover:
            avisos.append('branco demais no campo: faixa do branco larga (suba V min / baixe S max)')
        if n_white and out['branco_dentro_campo'] < thr.min_white_in_field:
            avisos.append('muito branco fora do campo (ok se for parede/ceu; confira o esqueleto)')
        if out['branco_na_fronteira'] > thr.max_white_at_boundary:
            avisos.append(
                'branco encostado na fronteira (placas/parede viraram campo): tecle A ou suba V min')
        if out['pixels_esqueleto'] < thr.min_skeleton_px:
            avisos.append('quase sem esqueleto: faixa do branco estreita?')
    out['avisos'] = avisos
    out['ok'] = bool(out['campo_detectado'] and not [
                     a for a in avisos if 'muito branco fora' not in a])
    return out
