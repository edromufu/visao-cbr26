"""
Calibrador de cor ao vivo (HighGUI do OpenCV).

Uso (na pasta do pacote ou com ele instalado)::

    # com o object_finder instalado (ros2 run object_finder calibrar_cores ...)
    ros2 run object_finder calibrar_cores --camera 0 --saida ~/calibracoes
    ros2 run object_finder aplicar_calibracao_cores ~/calibracoes/ultima

    # imagens salvas
    python3 -m object_finder.calibracao_cores.calibrator_cv --imagens frames/*.png
    # câmera ao vivo (índice 2, 640x480)
    python3 -m object_finder.calibracao_cores.calibrator_cv --camera 2 --largura 640 --altura 480
    # tópico ROS (opcional; precisa de ROS 2)
    python3 -m object_finder.calibracao_cores.calibrator_cv --ros-topico /AUREA/camera_optical_frame/image_color
    # sem janela: avalia uma calibração e grava overlays
    python3 -m object_finder.calibracao_cores.calibrator_cv --avaliar --calib calibracoes/ultima --imagens a.png

Teclas (também na tela com H):

    R  recalibração rápida: 1 clique no verde + 1 clique numa linha branca
    G  amostrar VERDE (carpete)        B  amostrar BRANCO (linha)
    T  trocar pincel / retângulo       [ ]  diminuir / aumentar o pincel
    U  desfazer última amostra         C  limpar amostras
    F  congelar / usar o frame atual (câmera)
    N P  próxima / anterior imagem     V  trocar visualização
    A  sugere V min do branco (tira placas/parede da borda do campo)
    S  SALVAR                          ESC ou Q  sair (2x se não salvou)

Arrastar com o botão esquerdo marca amostras; botão direito desfaz.
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
from pathlib import Path
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np

from . import core
from . import overlay
from .stage1_adapter import Stage1Segmenter

VIEWS = ('geral', 'mascara verde', 'mascara branca', 'esqueleto', 'imagem')
EVENT_LDOWN, EVENT_MOVE, EVENT_LUP, EVENT_RDOWN = (
    cv2.EVENT_LBUTTONDOWN, cv2.EVENT_MOUSEMOVE, cv2.EVENT_LBUTTONUP, cv2.EVENT_RBUTTONDOWN)
PANEL_H = 118
HELP_LINES = [
    'R  recalibracao rapida: 1 clique no verde + 1 clique numa linha branca',
    'G  amostrar VERDE (carpete)     B  amostrar BRANCO (linha)',
    'T  pincel / retangulo           [ ]  pincel menor / maior',
    'U  desfazer (ou botao direito)  C  limpar amostras',
    'F  congelar / usar o frame atual (camera)',
    'N P  proxima / anterior imagem  V  trocar visualizacao',
    'A  sugere V min do branco (tira placas/parede da fronteira)',
    'S  SALVAR                       ESC ou Q  sair',
    'janela "ajustes": deslizadores de ajuste fino (VD = verde, BR = branco)',
]


class Calibrador:
    """
    Estado e lógica do calibrador, sem janela (testável).

    A janela (``run_gui``) só repassa eventos de mouse/teclado e mostra
    :meth:`render`. Toda a regra de negócio fica aqui.
    """

    def __init__(self, frames: Optional[Dict[str, np.ndarray]] = None,
                 out_root: Path = Path('calibracoes'),
                 initial: Optional[core.Calibration] = None,
                 params: core.ProposalParams = core.ProposalParams(),
                 clock: Callable[[], float] = time.time) -> None:
        self.frames: Dict[str, np.ndarray] = dict(frames or {})
        self.names: List[str] = list(self.frames)
        self.idx = 0
        self.out_root = Path(out_root)
        self.params = params
        self.clock = clock
        self.samples: List[core.Sample] = []
        self.mode = 'verde'
        self.tool = 'pincel'
        self.radius = {'verde': 12, 'branco': 4}
        self.quick_step: Optional[str] = None
        self.view = 0
        self.live: Optional[np.ndarray] = None
        self.frozen = False
        self.show_help = False
        self.message = 'R = recalibracao rapida | G/B = amostrar verde/branco | S = salvar'
        self.saved_dir: Optional[Path] = None
        self.dirty = False
        self.quit_armed = False
        self.manual = False
        self._stroke: Optional[List[Tuple[int, int]]] = None
        self._rect0: Optional[Tuple[int, int]] = None
        self._rect1: Optional[Tuple[int, int]] = None
        self._snap_name: Optional[str] = None
        self.seg = Stage1Segmenter()
        if initial is not None:
            self.green, self.white = initial.green, initial.white
            self.samples = list(initial.samples)
        else:
            self.green = core.HSVRange((0, 0, 0), (0, 0, 0))
            self.white = core.HSVRange.from_dict(
                {'lower': [int(v) for v in self.seg.white_lower],
                 'upper': [int(v) for v in self.seg.white_up]})
            self._green_from_vendor_csv()
        self.apply_ranges()
        self.last_s1: Any = None
        self.last_metrics: Dict[str, Any] = {}
        self.history: List[Tuple[float, str]] = []

    # ------------------------------------------------------------------ util
    def _green_from_vendor_csv(self) -> None:
        """Caixa envolvente do CSV original (só para começar com algo)."""
        import pandas as pd
        df = pd.read_csv(self.seg.green_csv)
        lo = df[['H', 'S', 'V']].min().astype(int).tolist()
        up = df[['H', 'S', 'V']].max().astype(int).tolist()
        self.green = core.HSVRange(tuple(lo), tuple(up))  # type: ignore[arg-type]

    def _log(self, what: str) -> None:
        self.history.append((self.clock(), what))

    @property
    def current_name(self) -> Optional[str]:
        """Nome da imagem mostrada (``None`` se só houver câmera ao vivo)."""
        if not self.names:
            return None
        return self.names[self.idx % len(self.names)]

    def display_frame(self) -> Optional[np.ndarray]:
        """Frame que está na tela (ao vivo ou congelado/salvo)."""
        if self.live is not None and not self.frozen:
            return self.live
        name = self.current_name
        return None if name is None else self.frames[name]

    def set_live_frame(self, frame: np.ndarray) -> None:
        """Novo frame da câmera/tópico."""
        self.live = frame

    def _frame_for_sample(self) -> Optional[str]:
        """Garante que a amostra aponte para um frame guardado."""
        if self.live is not None and not self.frozen:
            if self._snap_name is None:
                stamp = dt.datetime.fromtimestamp(self.clock()).strftime('%H%M%S')
                name = f'camera_{stamp}_{len(self.frames)}'
                self.frames[name] = self.live.copy()
                self.names.append(name)
                self._snap_name = name
            return self._snap_name
        return self.current_name

    # ---------------------------------------------------------------- faixas
    def apply_ranges(self) -> None:
        """Envia as faixas atuais ao segmentador da etapa 1."""
        self.seg.set_green_box(self.green.lower, self.green.upper)
        self.seg.set_white_range(self.white.lower, self.white.upper)

    def recompute(self) -> None:
        """Recalcula as faixas propostas a partir de todas as amostras."""
        hsv = {k: cv2.cvtColor(v, cv2.COLOR_BGR2HSV) for k, v in self.frames.items()}
        g = core.gather(self.samples, hsv, 'verde')
        w = core.gather(self.samples, hsv, 'branco')
        if len(g):
            self.green = core.propose_green_range(g, self.params)
        if len(w):
            self.white = core.propose_white_range(w, self.green if len(g) else None, self.params)
        self.manual = False
        self.apply_ranges()

    def set_channel(self, classe: str, which: str, channel: int, value: int) -> None:
        """Ajuste fino de um limite (deslizador ou teclado)."""
        rng = self.green if classe == 'verde' else self.white
        lo, up = list(rng.lower), list(rng.upper)
        (lo if which == 'lower' else up)[channel] = int(value)
        new = core.HSVRange(tuple(lo), tuple(up))  # type: ignore[arg-type]
        if new.to_dict() == rng.to_dict():
            return
        if classe == 'verde':
            self.green = new
        else:
            self.white = new
        self.manual = True
        self.dirty = True
        self.apply_ranges()
        self._log(f'ajuste {classe} {which}[{channel}]={value}')

    # --------------------------------------------------------------- amostras
    def add_sample(self, sample: core.Sample) -> None:
        """Acrescenta uma amostra e recalcula a proposta."""
        self.samples.append(sample)
        self.dirty = True
        self._log(f'amostra {sample.classe} {sample.tipo}')
        self.recompute()

    def undo(self) -> None:
        """Remove a última amostra."""
        if self.samples:
            self.samples.pop()
            self.dirty = True
            self._log('desfazer')
            if self.samples:
                self.recompute()
            self.message = f'desfeito ({len(self.samples)} amostras)'

    def clear(self) -> None:
        """Remove todas as amostras (as faixas ficam como estão)."""
        self.samples = []
        self.dirty = True
        self.message = 'amostras apagadas (faixas mantidas)'

    def start_quick(self) -> None:
        """Inicia a recalibração rápida (2 cliques)."""
        self.quick_step = 'verde'
        self.message = 'RAPIDA 1/2: clique no CARPETE VERDE'
        self._log('rapida inicio')

    def quick_click(self, x: int, y: int) -> None:
        """Um clique da recalibração rápida."""
        frame = self.display_frame()
        if frame is None or self.quick_step is None:
            return
        name = self._frame_for_sample()
        classe = self.quick_step
        r = core.quick_click_radius(frame.shape[1], classe)
        s = core.Sample(classe, 'clique', name or '', pontos=[(x, y)], raio=r)
        if classe == 'verde':
            self.samples = [s]
            self.dirty = True
            self.recompute()
            self.quick_step = 'branco'
            self._snap_name = None  # o próximo clique usa o frame que estiver na tela
            self.message = 'RAPIDA 2/2: clique numa LINHA BRANCA (no meio da linha)'
        else:
            self.add_sample(s)
            self.quick_step = None
            self._snap_name = None
            self.message = 'RAPIDA pronta: confira o esqueleto (vermelho) e tecle S'
            self._auto_vmin(frame)
        self._log(f'rapida clique {classe}')

    # ------------------------------------------------------------------ mouse
    def on_mouse(self, event: int, x: int, y: int, flags: int = 0) -> None:
        """Eventos de mouse (coordenadas da imagem)."""
        frame = self.display_frame()
        if frame is None:
            return
        h, w = frame.shape[:2]
        x = int(np.clip(x, 0, w - 1))
        if y >= h and event != EVENT_LUP:
            return
        y = int(np.clip(y, 0, h - 1))
        if event == EVENT_RDOWN:
            self.undo()
            return
        if self.quick_step is not None:
            if event == EVENT_LDOWN:
                self.quick_click(x, y)
            return
        if event == EVENT_LDOWN:
            self.quit_armed = False
            if self.tool == 'pincel':
                self._stroke = [(x, y)]
            else:
                self._rect0, self._rect1 = (x, y), (x, y)
        elif event == EVENT_MOVE:
            if self._stroke is not None:
                if abs(self._stroke[-1][0] - x) + abs(self._stroke[-1][1] - y) >= 2:
                    self._stroke.append((x, y))
            elif self._rect0 is not None:
                self._rect1 = (x, y)
        elif event == EVENT_LUP:
            if self._stroke is None and self._rect0 is None:
                return
            name = self._frame_for_sample()
            if self._stroke is not None:
                s = core.Sample(self.mode, 'pincel', name or '', pontos=self._stroke,
                                raio=self.radius[self.mode])
                self._stroke = None
                self.add_sample(s)
            elif self._rect0 is not None and self._rect1 is not None:
                (x0, y0), (x1, y1) = self._rect0, self._rect1
                self._rect0 = self._rect1 = None
                if abs(x1 - x0) >= 1 and abs(y1 - y0) >= 1:
                    self.add_sample(core.Sample(self.mode, 'retangulo', name or '',
                                                retangulo=(x0, y0, x1, y1)))
            self._snap_name = None
            self.message = f'{len(self.samples)} amostras | modo {self.mode.upper()}'

    # ---------------------------------------------------------------- teclado
    def on_key(self, key: int) -> bool:
        """Trata uma tecla; devolve ``False`` para sair."""
        if key < 0:
            return True
        k = chr(key & 0xFF).lower() if (key & 0xFF) < 128 else ''
        if (key & 0xFF) == 27 or k == 'q':
            if self.dirty and not self.quit_armed:
                self.quit_armed = True
                self.message = 'NAO SALVO! tecle S para salvar ou ESC/Q de novo para sair'
                return True
            return False
        self.quit_armed = False
        if k == 'r':
            self.start_quick()
        elif k == 'g':
            self.mode, self.quick_step = 'verde', None
            self.message = 'modo VERDE: pinte o carpete (sombras e partes claras)'
        elif k == 'b':
            self.mode, self.quick_step = 'branco', None
            self.message = 'modo BRANCO: pinte sobre as linhas'
        elif k == 't':
            self.tool = 'retangulo' if self.tool == 'pincel' else 'pincel'
            self.message = f'ferramenta: {self.tool}'
        elif k == '[':
            self.radius[self.mode] = max(1, self.radius[self.mode] - 1)
        elif k == ']':
            self.radius[self.mode] = min(60, self.radius[self.mode] + 1)
        elif k == 'u':
            self.undo()
        elif k == 'c':
            self.clear()
        elif k == 'f':
            if self.live is not None:
                if not self.frozen:
                    name = self._frame_for_sample()
                    self.idx = self.names.index(name) if name in self.names else self.idx
                    self.frozen = True
                    self._snap_name = None
                    self.message = 'frame congelado (F volta ao vivo)'
                else:
                    self.frozen = False
                    self.message = 'ao vivo'
        elif k == 'n' and self.names:
            self.idx = (self.idx + 1) % len(self.names)
            self.frozen = self.live is not None
        elif k == 'p' and self.names:
            self.idx = (self.idx - 1) % len(self.names)
            self.frozen = self.live is not None
        elif k == 'v':
            self.view = (self.view + 1) % len(VIEWS)
        elif k == 'h':
            self.show_help = not self.show_help
        elif k == 'a':
            self.apply_vmin_suggestion()
        elif k == 's':
            self.save()
        return True

    def _auto_vmin(self, frame: np.ndarray, max_iter: int = 2) -> None:
        """Na recalibração rápida: aplica a tecla A sozinha se houver aviso."""
        for _ in range(max_iter):
            s1, m = self.evaluate(frame)
            if m.get('branco_na_fronteira', 0.0) <= core.SanityThresholds().max_white_at_boundary:
                return
            if self.apply_vmin_suggestion() is None:
                return
            self.message = f'RAPIDA pronta (V min do branco ajustado p/ {self.white.lower[2]}): confira e tecle S'

    def apply_vmin_suggestion(self) -> Optional[int]:
        """Tecla A: sobe o V mínimo do branco para tirar o fundo da fronteira."""
        frame = self.display_frame()
        if frame is None:
            return None
        s1, _ = self.evaluate(frame)
        sug = core.suggest_white_vmin(s1, cv2.cvtColor(frame, cv2.COLOR_BGR2HSV))
        if sug is None or sug <= self.white.lower[2]:
            self.message = 'A: sem sugestao (branco da fronteira nao se separa das linhas)'
            return None
        self.set_channel('branco', 'lower', 2, sug)
        self.message = f'A: V min do branco -> {sug} (confira as linhas distantes)'
        return sug

    # ------------------------------------------------------------ avaliação
    def evaluate(self, frame: Optional[np.ndarray] = None) -> Tuple[Any, Dict[str, Any]]:
        """Roda a etapa 1 com as faixas atuais e calcula as métricas."""
        frame = self.display_frame() if frame is None else frame
        if frame is None:
            return None, {}
        s1 = self.seg.process(frame)
        m = core.sanity_metrics(s1)
        self.last_s1, self.last_metrics = s1, m
        return s1, m

    def calibration(self) -> core.Calibration:
        """Calibração atual (para salvar)."""
        frame = self.display_frame()
        res = None if frame is None else (int(frame.shape[1]), int(frame.shape[0]))
        return core.Calibration(green=self.green, white=self.white, samples=list(self.samples),
                                imagens=sorted({s.imagem for s in self.samples}),
                                resolucao=res, metricas=dict(self.last_metrics),
                                ajuste_manual=self.manual)

    def save(self) -> Path:
        """Salva a calibração versionada e atualiza ``ultima/``."""
        if self.last_s1 is None:
            self.evaluate()
        used = {s.imagem for s in self.samples}
        frames = {k: v for k, v in self.frames.items() if k in used}
        cur = self.display_frame()
        if cur is not None and not frames:
            frames = {'frame_atual': cur}
        cal = self.calibration()
        cal.metricas = dict(self.last_metrics)
        self.saved_dir = core.save_calibration(cal, self.out_root, frames)
        self.dirty = False
        self.message = f'SALVO em {self.saved_dir} (e em {self.out_root / "ultima"})'
        self._log('salvar')
        return self.saved_dir

    # ----------------------------------------------------------------- tela
    def render(self) -> Optional[np.ndarray]:
        """Imagem para a janela: overlay + painel de status embaixo."""
        frame = self.display_frame()
        if frame is None:
            return None
        s1, m = self.evaluate(frame)
        v = VIEWS[self.view]
        if v == 'geral':
            img = overlay.draw_stage1(frame, s1)
        elif v == 'mascara verde':
            img = overlay.mask_view(s1.green_mask, s1.field_mask_full)
            overlay.draw_stage1(img, s1, masks=False, skeleton=False)
        elif v == 'mascara branca':
            img = overlay.mask_view(s1.white_mask, s1.field_mask_full)
        elif v == 'esqueleto':
            img = overlay.draw_stage1(frame // 3, s1, masks=False)
        else:
            img = frame.copy()
        # amostras do frame atual
        name = self.current_name if (self.live is None or self.frozen) else None
        for s in self.samples:
            if name is not None and s.imagem != name:
                continue
            col = overlay.COR_VERDE if s.classe == 'verde' else overlay.COR_BRANCO
            if s.tipo == 'retangulo' and s.retangulo:
                x0, y0, x1, y1 = s.retangulo
                cv2.rectangle(img, (x0, y0), (x1, y1), col, 1)
            else:
                pts = [tuple(map(int, p)) for p in s.pontos]
                for p in pts:
                    cv2.circle(img, p, int(s.raio), col, 1)
                if len(pts) > 1:
                    cv2.polylines(img, [np.array(pts, np.int32).reshape(-1, 1, 2)], False, col, 1)
        if self._stroke:
            col = overlay.COR_VERDE if self.mode == 'verde' else overlay.COR_BRANCO
            cv2.polylines(img, [np.array(self._stroke, np.int32).reshape(-1, 1, 2)], False, col,
                          max(1, 2 * self.radius[self.mode]))
        if self._rect0 and self._rect1:
            cv2.rectangle(img, self._rect0, self._rect1, (255, 255, 255), 1)
        panel = np.zeros((PANEL_H, img.shape[1], 3), np.uint8)
        ok_col = (0, 220, 0) if m.get('ok') else (0, 0, 255)
        fonte = 'AO VIVO' if (self.live is not None and not self.frozen) else (
            self.current_name or '')
        linhas = [
            f'[{VIEWS[self.view]}] {fonte} | modo {self.mode.upper()} | {self.tool} r={self.radius[self.mode]}'
            f' | amostras {len(self.samples)}' + (' | AJUSTE MANUAL' if self.manual else ''),
            f'VERDE  H {self.green.lower[0]}-{self.green.upper[0]}  S {self.green.lower[1]}-{self.green.upper[1]}'
            f'  V {self.green.lower[2]}-{self.green.upper[2]}   BRANCO  H {self.white.lower[0]}-{self.white.upper[0]}'
            f'  S {self.white.lower[1]}-{self.white.upper[1]}  V {self.white.lower[2]}-{self.white.upper[2]}',
            f'campo {"SIM" if m.get("campo_detectado") else "NAO"} | verde no campo {m.get("verde_no_campo", 0):.2f}'
            f' | branco cobre campo {m.get("branco_cobre_campo", 0):.3f}'
            f' | branco dentro {m.get("branco_dentro_campo", 0):.2f}'
            f' | esqueleto {m.get("pixels_esqueleto", 0)}',
            ('; '.join(m.get('avisos', [])) or 'OK')[:160],
            self.message[:160],
        ]
        cols = [(255, 255, 255), (200, 200, 200), ok_col, ok_col, (0, 255, 255)]
        overlay.draw_text_block(panel, linhas, (6, 18), dy=22, scale=0.5, colors=cols)
        if self.show_help:
            overlay.draw_text_block(img, HELP_LINES, (10, 24), scale=0.55, dy=22)
        return np.vstack([img, panel])


# --------------------------------------------------------------------- janela
TRACKBARS = [(c, w, ch) for c in ('verde', 'branco')
             for ch in range(3) for w in ('lower', 'upper')]
_CH = 'HSV'


def _tb_name(classe: str, which: str, ch: int) -> str:
    return f'{"VD" if classe == "verde" else "BR"} {_CH[ch]} {"min" if which == "lower" else "max"}'


def run_gui(cal: Calibrador, source: Optional[Any] = None, win: str = 'calibrador',
            max_width: int = 1280) -> None:  # pragma: no cover - precisa de tela
    """Laço da janela HighGUI. ``source`` tem ``read()`` (câmera/tópico)."""
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.namedWindow('ajustes', cv2.WINDOW_NORMAL)
    syncing = {'on': False}

    def make_cb(c: str, w: str, ch: int) -> Callable[[int], None]:
        def cb(val: int) -> None:
            if not syncing['on']:
                cal.set_channel(c, w, ch, val)
        return cb

    for c, w, ch in TRACKBARS:
        cv2.createTrackbar(_tb_name(c, w, ch), 'ajustes', 0,
                           179 if ch == 0 else 255, make_cb(c, w, ch))

    def sync() -> None:
        syncing['on'] = True
        for c, w, ch in TRACKBARS:
            rng = cal.green if c == 'verde' else cal.white
            val = (rng.lower if w == 'lower' else rng.upper)[ch]
            if cv2.getTrackbarPos(_tb_name(c, w, ch), 'ajustes') != val:
                cv2.setTrackbarPos(_tb_name(c, w, ch), 'ajustes', int(val))
        syncing['on'] = False

    cv2.setMouseCallback(win, lambda e, x, y, f, p: cal.on_mouse(e, x, y, f))
    sized = False
    # Em alguns ambientes (WSLg/Docker, GTK) a propriedade VISIBLE vale 0 ou -1
    # antes de o gerenciador de janelas mostrar a janela; só fecha por ela
    # depois de a janela ter aparecido pelo menos uma vez.
    visto = False
    last_ranges = None
    while True:
        if source is not None:
            fr = source.read()
            if isinstance(fr, tuple):
                fr = fr[1] if fr[0] else None
            if fr is not None:
                cal.set_live_frame(fr)
        img = cal.render()
        if img is None:
            img = np.zeros((240, 640, 3), np.uint8)
            overlay.draw_text_block(img, ['aguardando imagem...'], (20, 120))
        if not sized:
            h, w = img.shape[:2]
            f = min(1.0, max_width / float(w))
            cv2.resizeWindow(win, int(w * f), int(h * f))
            cv2.resizeWindow('ajustes', 520, 420)
            cv2.moveWindow(win, 0, 0)
            cv2.moveWindow('ajustes', int(w * f) + 12, 0)
            sized = True
        ranges = (cal.green.to_dict(), cal.white.to_dict())
        if ranges != last_ranges:
            sync()
            last_ranges = ranges
        cv2.imshow(win, img)
        key = cv2.waitKey(15)
        if not cal.on_key(key):
            break
        visivel = cv2.getWindowProperty(win, cv2.WND_PROP_VISIBLE)
        if visivel >= 1:
            visto = True
        elif visto:
            break
    cv2.destroyAllWindows()


class _CameraSource:  # pragma: no cover - precisa de câmera
    def __init__(self, idx: int, width: int, height: int) -> None:
        self.cap = cv2.VideoCapture(idx)
        if width:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        if height:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        if not self.cap.isOpened():
            raise SystemExit(
                f'nao abriu a camera {idx} (no WSL: usbipd; ou capture frames e use --imagens)')

    def read(self) -> Optional[np.ndarray]:
        ok, fr = self.cap.read()
        return fr if ok else None


def load_images(patterns: Sequence[str]) -> Dict[str, np.ndarray]:
    """Carrega imagens (aceita curingas e pastas)."""
    files: List[str] = []
    for p in patterns:
        pp = Path(p)
        if pp.is_dir():
            files += sorted(str(f) for f in pp.iterdir()
                            if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.bmp'))
        else:
            files += sorted(glob.glob(p)) or [p]
    out: Dict[str, np.ndarray] = {}
    for f in files:
        img = cv2.imread(f, cv2.IMREAD_COLOR)
        if img is None:
            print(f'aviso: nao li {f}', file=sys.stderr)
            continue
        out[Path(f).name] = img
    return out


def avaliar(calib_dir: Path, images: Dict[str, np.ndarray], out_dir: Optional[Path]) -> Dict[str, Any]:
    """Avalia uma calibração salva nas imagens (sem janela)."""
    cal, gcsv, wcsv = core.load_calibration_dir(calib_dir)
    seg = Stage1Segmenter(gcsv, wcsv)
    res: Dict[str, Any] = {}
    for name, img in images.items():
        s1 = seg.process(img)
        res[name] = core.sanity_metrics(s1)
        if out_dir is not None:
            out_dir.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_dir / f'{Path(name).stem}_calib.png'),
                        overlay.draw_stage1(img, s1))
    return res


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Ponto de entrada da linha de comando."""
    ap = argparse.ArgumentParser(description='Calibrador de cor (verde/branco) da etapa 1.')
    ap.add_argument('--imagens', nargs='*', default=[], help='imagens ou pastas')
    ap.add_argument('--camera', type=int, default=None, help='indice da camera (cv2.VideoCapture)')
    ap.add_argument('--largura', type=int, default=0)
    ap.add_argument('--altura', type=int, default=0)
    ap.add_argument('--ros-topico', default=None, help='topico sensor_msgs/Image (opcional)')
    ap.add_argument('--saida', default='calibracoes', help='pasta das calibracoes versionadas')
    ap.add_argument('--inicial', default=None,
                    help='pasta de calibracao para comecar (ex.: calibracoes/ultima)')
    ap.add_argument('--avaliar', action='store_true',
                    help='sem janela: avalia --calib nas --imagens')
    ap.add_argument('--calib', default=None, help='pasta de calibracao para --avaliar')
    ap.add_argument('--relatorio', default=None, help='pasta para overlays/metricas do --avaliar')
    a = ap.parse_args(argv)
    images = load_images(a.imagens) if a.imagens else {}
    if a.avaliar:
        if not a.calib:
            ap.error('--avaliar precisa de --calib')
        r = avaliar(Path(a.calib), images, Path(a.relatorio) if a.relatorio else None)
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 0
    initial = core.load_calibration_dir(Path(a.inicial))[0] if a.inicial else None
    cal = Calibrador(images, Path(a.saida), initial)
    source: Any = None
    if a.camera is not None:
        source = _CameraSource(a.camera, a.largura, a.altura)
    elif a.ros_topico:
        from .ros_image import RosImageSource
        source = RosImageSource(a.ros_topico)
    if not images and source is None:
        ap.error('informe --imagens, --camera ou --ros-topico')
    run_gui(cal, source)
    if cal.saved_dir:
        print(f'calibracao salva em {cal.saved_dir}')
    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
