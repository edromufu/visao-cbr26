"""
Vision pipeline (pipe-and-filter) inspirado no artigo Hamburg Bit-Bots.

Este subpacote NAO depende de ROS: pode ser testado com `pytest` puro.
A cola com o ROS 2 fica em `object_finder.connecting_and_showing`.
"""

from .color_common import (
    DEFAULT_COLOR_SPACES,
    ColorDetector,
    ColorSpaceHSV,
    build_color_detector,
    color_spaces_from_calibration,
    load_color_spaces_from_csv,
)
from .dynamic_color import DynamicColorSpace
from .field_boundary_detector import detect_field_boundary
from .line_detector import detect_line_points
from .main_pipeline import (
    PipelineConfig,
    PipelineResult,
    VisionPipeline,
    draw_pipeline_overlay,
    filter_points_in_boxes,
)

__all__ = [
    "DynamicColorSpace",
    "ColorDetector", "ColorSpaceHSV", "DEFAULT_COLOR_SPACES",
    "PipelineConfig", "PipelineResult", "VisionPipeline",
    "build_color_detector", "color_spaces_from_calibration",
    "detect_field_boundary", "detect_line_points",
    "draw_pipeline_overlay", "filter_points_in_boxes",
    "load_color_spaces_from_csv",
]
