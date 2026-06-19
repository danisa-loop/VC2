"""
Fase 1 - Extracción y estandarización del componente (grano individual).

Pasos del documento de diseño:
  1. Segmentación + extracción de máscara de canal alfa (Otsu sobre luminancia).
  2. Recorte de la región de interés (bbox cropping) -> matriz RGBA compacta.
"""
from __future__ import annotations

import cv2
import numpy as np

from .config import ExtractConfig


def segment_alpha(bgr: np.ndarray, cfg: ExtractConfig) -> np.ndarray:
    """Aísla el grano del fondo negro y devuelve una imagen BGRA.

    El canal alfa toma 255 en los píxeles del grano y 0 en el fondo, lo que
    permite hacer alpha blending posterior sin artefactos de borde.
    """
    if bgr.ndim != 3 or bgr.shape[2] != 3:
        raise ValueError("Se espera una imagen BGR de 3 canales.")

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    if cfg.threshold_method == "otsu":
        _, mask = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
    else:
        _, mask = cv2.threshold(gray, cfg.threshold_fixed, 255, cv2.THRESH_BINARY)

    # Auto-polaridad: el fondo SIEMPRE debe quedar transparente. Si el borde de
    # la imagen quedó marcado como "objeto", invertimos la máscara. Esto hace que
    # funcione tanto con fondo oscuro (enunciado) como claro (dataset real).
    border = np.concatenate(
        [mask[0, :], mask[-1, :], mask[:, 0], mask[:, -1]]
    )
    if border.mean() > 127:
        mask = cv2.bitwise_not(mask)

    # Limpieza morfológica: cierre para tapar huecos internos del grano.
    if cfg.morph_kernel > 0:
        k = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (cfg.morph_kernel, cfg.morph_kernel)
        )
        mask = cv2.morphologyEx(
            mask, cv2.MORPH_CLOSE, k, iterations=cfg.morph_iterations
        )

    bgra = cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)
    bgra[:, :, 3] = mask
    return bgra


def crop_to_bbox(bgra: np.ndarray) -> np.ndarray:
    """Recorta el RGBA a la caja delimitadora mínima de la máscara alfa."""
    alpha = bgra[:, :, 3]
    ys, xs = np.where(alpha > 0)
    if ys.size == 0:
        raise ValueError("Máscara vacía: no se detectó grano.")
    y0, y1 = ys.min(), ys.max() + 1
    x0, x1 = xs.min(), xs.max() + 1
    return bgra[y0:y1, x0:x1].copy()


def extract_grain(bgr: np.ndarray, cfg: ExtractConfig) -> np.ndarray:
    """Atajo: segmenta y recorta. Devuelve el grano BGRA estandarizado."""
    return crop_to_bbox(segment_alpha(bgr, cfg))
