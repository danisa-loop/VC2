"""
Configuración centralizada del pipeline de generación de datos sintéticos.

Todos los rangos estocásticos del documento de diseño se exponen acá para que
sean reproducibles y fáciles de ajustar sin tocar la lógica.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class ExtractConfig:
    """Fase 1 - Extracción y estandarización del grano individual."""
    # Umbralizado: 'otsu' (adaptativo global) o un entero fijo [0-255].
    threshold_method: str = "otsu"
    threshold_fixed: int = 10
    # Operaciones morfológicas para limpiar la máscara binaria.
    morph_kernel: int = 3
    morph_iterations: int = 1


@dataclass
class AugmentConfig:
    """Fase 2 - Aumento de datos a nivel de componente."""
    rotation_range: Tuple[float, float] = (0.0, 360.0)
    scale_range: Tuple[float, float] = (0.8, 1.2)
    p_hflip: float = 0.5
    p_vflip: float = 0.5
    # Perturbación fotométrica en HSV (offsets en S y V).
    saturation_jitter: float = 0.12   # fracción +/- sobre S
    value_jitter: float = 0.12        # fracción +/- sobre V
    hue_jitter: int = 4               # grados +/- sobre H (sutil)


@dataclass
class ComposeConfig:
    """Fase 3 - Composición de la imagen sintética y ground truth."""
    canvas_size: Tuple[int, int] = (1024, 1024)   # (alto, ancho)
    # Fondo: 'black' (negro absoluto) o 'texture' (textura tipo cinta/tolva).
    background: str = "black"
    n_grains_range: Tuple[int, int] = (20, 150)
    # Control de oclusión: máximo solapamiento permitido del grano nuevo
    # respecto de su propia área (derivado del criterio IoU del diseño).
    max_overlap: float = 0.15
    max_placement_attempts: int = 30
    class_id: int = 0
    class_name: str = "poroto"


@dataclass
class PostprocessConfig:
    """Fase 4 - Postprocesamiento global de la imagen compuesta."""
    blur_kernel: int = 3
    blur_sigma: float = 0.6
    speckle_std: float = 0.03      # ruido multiplicativo (sensor)
    gaussian_noise_std: float = 4.0  # ruido aditivo de baja amplitud (0-255)


@dataclass
class PipelineConfig:
    seed: int = 42
    extract: ExtractConfig = field(default_factory=ExtractConfig)
    augment: AugmentConfig = field(default_factory=AugmentConfig)
    compose: ComposeConfig = field(default_factory=ComposeConfig)
    postprocess: PostprocessConfig = field(default_factory=PostprocessConfig)
