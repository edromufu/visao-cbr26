"""Tipos de saída do núcleo (independentes de ROS)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

NUM_RAYS = {'L': 2, 'T': 3, 'X': 4}


@dataclass
class CrossingFeature:
    """
    Cruzamento de linhas (IV-A).

    ``heading_rays`` em radianos, [0, 2π), ordem crescente, convenção de
    ``soccer_vision_2d_msgs/MarkingIntersection``: 0 aponta para +x da imagem
    (direita) e π/2 para +y (para baixo).
    """

    tipo: str                         # 'L', 'T' ou 'X'
    x: float                          # pixel na imagem
    y: float
    heading_rays: List[float]
    confianca: float
    fonte: str = 'grafo'              # 'grafo', 'grafo+yolo' ou 'yolo'
    verificacao: Dict[str, Any] = field(default_factory=dict)
    grade: Optional[Tuple[float, float]] = None
    distancia_m: Optional[float] = None
    angulo_rad: Optional[float] = None

    @property
    def num_rays(self) -> int:
        """Número de braços pelo tipo."""
        return NUM_RAYS.get(self.tipo, len(self.heading_rays))

    def to_dict(self) -> Dict[str, Any]:
        """Para JSON."""
        return asdict(self)


@dataclass
class LineFeature:
    """Linha do campo (IV-B), extremos projetados na reta ajustada."""

    x1: float
    y1: float
    x2: float
    y2: float
    confianca: float
    n_nos: int = 0
    rms_px: float = 0.0
    distancia_m: Optional[float] = None   # distância perpendicular robô-reta
    angulo_rad: Optional[float] = None    # direção do pé da perpendicular
    comprimento_m: Optional[float] = None

    @property
    def length(self) -> float:
        """Comprimento em pixels."""
        return float(((self.x2 - self.x1) ** 2 + (self.y2 - self.y1) ** 2) ** 0.5)

    def to_dict(self) -> Dict[str, Any]:
        """Para JSON."""
        return asdict(self)


@dataclass
class EllipseFeature:
    """Elipse (círculo central visto em perspectiva), em pixels."""

    cx: float
    cy: float
    eixo_maior: float                 # diâmetro (convenção do cv2.fitEllipse)
    eixo_menor: float
    angulo_graus: float
    confianca: float
    n_nos: int = 0
    rms_px: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Para JSON."""
        return asdict(self)


@dataclass
class Detection:
    """Caixa do detector (centro, largura, altura em pixels)."""

    classe: str
    class_id: int
    conf: float
    x: float
    y: float
    w: float
    h: float
    rejeitada: bool = False
    motivo: str = ''

    def to_dict(self) -> Dict[str, Any]:
        """Para JSON."""
        return asdict(self)
