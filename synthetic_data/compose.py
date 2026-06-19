"""
Fase 3 - Composición de la imagen sintética y generación de ground truth.

  5. Inicialización del lienzo y densidad (N granos).
  6. Ubicación espacial con control de colisiones (oclusión controlada).
  7. Alpha blending y registro de etiquetas (YOLO).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import cv2
import numpy as np

from .config import ComposeConfig


@dataclass
class Annotation:
    """Etiqueta YOLO normalizada respecto del tamaño del lienzo."""
    class_id: int
    x_center: float
    y_center: float
    width: float
    height: float

    def to_yolo_line(self) -> str:
        return (
            f"{self.class_id} {self.x_center:.6f} {self.y_center:.6f} "
            f"{self.width:.6f} {self.height:.6f}"
        )


def init_canvas(cfg: ComposeConfig, rng: np.random.Generator) -> np.ndarray:
    """Crea el lienzo BGR del tamaño objetivo."""
    h, w = cfg.canvas_size
    if cfg.background == "texture":
        # Textura sutil tipo cinta/tolva: gris con ruido de baja frecuencia.
        base = rng.integers(35, 55, size=(h, w, 1), dtype=np.uint8)
        canvas = np.repeat(base, 3, axis=2)
        canvas = cv2.GaussianBlur(canvas, (0, 0), sigmaX=8)
    else:  # 'black'
        canvas = np.zeros((h, w, 3), dtype=np.uint8)
    return canvas


def _alpha_blend(
    canvas: np.ndarray,
    grain_bgra: np.ndarray,
    top: int,
    left: int,
) -> Tuple[int, int, int, int]:
    """Inserta un grano en (top,left) con combinación lineal por canal alfa.

        I_sint = a * I_grano + (1-a) * I_sint

    Devuelve la bbox efectiva (x0,y0,x1,y1) realmente escrita en el lienzo
    (recortada a los límites del lienzo).
    """
    H, W = canvas.shape[:2]
    gh, gw = grain_bgra.shape[:2]

    # Intersección del grano con el lienzo (manejo de bordes).
    y0, y1 = max(0, top), min(H, top + gh)
    x0, x1 = max(0, left), min(W, left + gw)
    if y0 >= y1 or x0 >= x1:
        return (0, 0, 0, 0)

    gy0, gy1 = y0 - top, y1 - top
    gx0, gx1 = x0 - left, x1 - left

    grain_crop = grain_bgra[gy0:gy1, gx0:gx1]
    a = (grain_crop[:, :, 3:4].astype(np.float32)) / 255.0
    fg = grain_crop[:, :, :3].astype(np.float32)
    bg = canvas[y0:y1, x0:x1].astype(np.float32)
    blended = a * fg + (1.0 - a) * bg
    canvas[y0:y1, x0:x1] = blended.astype(np.uint8)
    return (x0, y0, x1, y1)


def _tight_bbox(alpha_region: np.ndarray, x0: int, y0: int) -> Optional[Tuple[int, int, int, int]]:
    """Bbox ajustada de los píxeles activos, en coordenadas del lienzo."""
    ys, xs = np.where(alpha_region > 0)
    if ys.size == 0:
        return None
    return (x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1)


def place_grains(
    canvas: np.ndarray,
    grains: List[np.ndarray],
    cfg: ComposeConfig,
    rng: np.random.Generator,
) -> List[Annotation]:
    """Ubica `grains` ya aumentados en el lienzo controlando oclusión.

    Mantiene una máscara global de ocupación. Para cada grano calcula el
    solapamiento de su huella contra lo ya ocupado; si supera `max_overlap`
    reintenta otra posición (hasta `max_placement_attempts`).
    """
    H, W = canvas.shape[:2]
    occupancy = np.zeros((H, W), dtype=np.uint8)
    annotations: List[Annotation] = []

    for grain in grains:
        gh, gw = grain.shape[:2]
        if gh >= H or gw >= W:
            # Grano más grande que el lienzo: lo salteamos.
            continue

        placed = False
        for _ in range(cfg.max_placement_attempts):
            top = int(rng.integers(0, H - gh))
            left = int(rng.integers(0, W - gw))

            # Huella binaria del grano candidato sobre un parche del lienzo.
            footprint = (grain[:, :, 3] > 0).astype(np.uint8)
            patch = occupancy[top:top + gh, left:left + gw]
            inter = np.logical_and(footprint, patch).sum()
            area = footprint.sum()
            overlap = inter / area if area > 0 else 1.0

            if overlap <= cfg.max_overlap:
                bbox = _alpha_blend(canvas, grain, top, left)
                x0, y0, x1, y1 = bbox
                if x1 <= x0 or y1 <= y0:
                    break
                # Actualizar ocupación con la huella efectiva.
                eff_fp = footprint[y0 - top:y1 - top, x0 - left:x1 - left]
                occupancy[y0:y1, x0:x1] = np.maximum(
                    occupancy[y0:y1, x0:x1], eff_fp
                )
                tb = _tight_bbox(eff_fp * 255, x0, y0)
                if tb is None:
                    break
                bx0, by0, bx1, by1 = tb
                annotations.append(
                    Annotation(
                        class_id=cfg.class_id,
                        x_center=((bx0 + bx1) / 2.0) / W,
                        y_center=((by0 + by1) / 2.0) / H,
                        width=(bx1 - bx0) / W,
                        height=(by1 - by0) / H,
                    )
                )
                placed = True
                break
        # Si no se pudo ubicar tras los reintentos, se descarta el grano.
        if not placed:
            continue

    return annotations


def sample_n_grains(cfg: ComposeConfig, rng: np.random.Generator) -> int:
    lo, hi = cfg.n_grains_range
    return int(rng.integers(lo, hi + 1))
