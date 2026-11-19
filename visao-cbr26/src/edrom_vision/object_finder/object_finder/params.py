"""Leitura dos parâmetros (YAML) para os dataclasses de cada etapa."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .crossings import CrossingParams, LineCrossingParams
from .fusion import FusionParams
from .graph_nodes import GraphParams
from .lines import LineParams


@dataclass
class Stage1Params:
    """III-A (etapa 1 original)."""

    tpix: int = 20
    trow: int = 10000
    twin: int = 3000


@dataclass
class DetectorParams:
    """YOLO (valores do nó finder)."""

    imgsz: int = 320
    conf: float = 0.45
    iou: float = 0.5
    max_det: int = 10


@dataclass
class OutputParams:
    """Filtros finais e extensões."""

    min_conf_cruzamento: float = 0.0
    ellipse_tol_px: float = 10.0
    cruzamentos_de_retas: bool = True   # extensão: interseções de retas/elipse


@dataclass
class CameraParams:
    """Projeção ao chão."""

    modelo: str = 'nenhum'
    hfov_rad: float = 0.785
    altura_m: float = 0.70
    pitch_rad: float = 0.0
    camera_matrix: str = ''
    dist_coeffs: str = ''
    homography: str = ''
    calib_largura: int = 640
    calib_altura: int = 480


@dataclass
class Params:
    """Todos os parâmetros."""

    etapa1: Stage1Params = field(default_factory=Stage1Params)
    grafo: GraphParams = field(default_factory=GraphParams)
    cruzamentos: CrossingParams = field(default_factory=CrossingParams)
    cruzamentos_retas: LineCrossingParams = field(default_factory=LineCrossingParams)
    linhas: LineParams = field(default_factory=LineParams)
    fusao: FusionParams = field(default_factory=FusionParams)
    detector: DetectorParams = field(default_factory=DetectorParams)
    saida: OutputParams = field(default_factory=OutputParams)
    camera: CameraParams = field(default_factory=CameraParams)


def _fill(obj: Any, d: Dict[str, Any], where: str) -> None:
    names = {f.name: f for f in fields(obj)}
    for k, v in (d or {}).items():
        if k not in names:
            raise KeyError(f'parâmetro desconhecido: {where}.{k}')
        cur = getattr(obj, k)
        if isinstance(cur, tuple):
            v = tuple(v)
        elif isinstance(cur, bool):
            v = bool(v)
        elif isinstance(cur, float) and isinstance(v, int):
            v = float(v)
        setattr(obj, k, v)


def load_params(path: Optional[str] = None, overrides: Optional[Dict[str, Dict[str, Any]]] = None) -> Params:
    """Lê o YAML (se houver) por cima dos padrões e aplica ``overrides``."""
    p = Params()
    data: Dict[str, Any] = {}
    if path:
        import yaml
        with open(path, encoding='utf-8') as fh:
            data = yaml.safe_load(fh) or {}
    for sec, vals in list(data.items()) + list((overrides or {}).items()):
        if not hasattr(p, sec):
            raise KeyError(f'seção desconhecida: {sec}')
        _fill(getattr(p, sec), vals, sec)
    return p


def default_params_file() -> Optional[Path]:
    """``config/params.yaml`` do pacote (fonte ou share do ament)."""
    here = Path(__file__).resolve().parent
    cands = [here.parent / 'config' / 'params.yaml']
    try:  # instalado pelo colcon
        from ament_index_python.packages import get_package_share_directory
        cands.insert(0, Path(get_package_share_directory(
            'object_finder')) / 'config' / 'params.yaml')
    except Exception:  # noqa: BLE001 - sem ROS
        pass
    for c in cands:
        if c.is_file():
            return c
    return None


def as_tuple(x: Any) -> Tuple:
    """Utilitário."""
    return tuple(x)
