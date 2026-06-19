"""
Fase 4 - Postprocesamiento global de la imagen compuesta.

  8. Degradación convolucional (blur) + ruido de sensor (speckle/gaussiano)
     para unificar la firma óptica y borrar discontinuidades en los bordes
     sintetizados.
"""
from __future__ import annotations

import cv2
import numpy as np

from .config import PostprocessConfig


def apply_postprocess(
    img: np.ndarray, cfg: PostprocessConfig, rng: np.random.Generator
) -> np.ndarray:
    """Aplica desenfoque, ruido speckle y ruido gaussiano de baja amplitud."""
    out = img.astype(np.float32)

    # Desenfoque óptico/movimiento sutil.
    if cfg.blur_kernel and cfg.blur_kernel >= 3:
        k = cfg.blur_kernel | 1  # forzar impar
        out = cv2.GaussianBlur(out, (k, k), cfg.blur_sigma)

    # Ruido multiplicativo (speckle) -> simula respuesta del sensor.
    if cfg.speckle_std > 0:
        speckle = rng.normal(1.0, cfg.speckle_std, size=out.shape).astype(np.float32)
        out = out * speckle

    # Ruido gaussiano aditivo de baja amplitud -> homogeneiza textura.
    if cfg.gaussian_noise_std > 0:
        noise = rng.normal(0.0, cfg.gaussian_noise_std, size=out.shape).astype(np.float32)
        out = out + noise

    return np.clip(out, 0, 255).astype(np.uint8)
