"""
Fase 2 - Aumento de datos a nivel de componente (variabilidad estocástica).

Transformaciones geométricas (rotación, escala, flips) y fotométricas
(perturbaciones en HSV) aplicadas a cada grano ANTES de insertarlo en el lienzo.
"""
from __future__ import annotations

import cv2
import numpy as np

from .config import AugmentConfig


def geometric_augment(
    bgra: np.ndarray, cfg: AugmentConfig, rng: np.random.Generator
) -> np.ndarray:
    """Rotación afín [0,360), escala estocástica y flips probabilísticos.

    Se preserva el canal alfa rotándolo con la misma matriz; el borde nuevo
    se rellena con transparencia (alfa=0).
    """
    h, w = bgra.shape[:2]

    # --- Escala ---
    s = rng.uniform(*cfg.scale_range)
    new_w, new_h = max(1, int(round(w * s))), max(1, int(round(h * s)))
    bgra = cv2.resize(bgra, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    # --- Rotación con lienzo expandido para no recortar esquinas ---
    theta = rng.uniform(*cfg.rotation_range)
    h, w = bgra.shape[:2]
    cx, cy = w / 2.0, h / 2.0
    M = cv2.getRotationMatrix2D((cx, cy), theta, 1.0)
    cos, sin = abs(M[0, 0]), abs(M[0, 1])
    nw = int(h * sin + w * cos)
    nh = int(h * cos + w * sin)
    M[0, 2] += (nw / 2.0) - cx
    M[1, 2] += (nh / 2.0) - cy
    bgra = cv2.warpAffine(
        bgra, M, (nw, nh),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0),
    )

    # --- Flips ---
    if rng.random() < cfg.p_hflip:
        bgra = cv2.flip(bgra, 1)
    if rng.random() < cfg.p_vflip:
        bgra = cv2.flip(bgra, 0)

    return bgra


def photometric_augment(
    bgra: np.ndarray, cfg: AugmentConfig, rng: np.random.Generator
) -> np.ndarray:
    """Perturba madurez/iluminación moviendo H, S y V en HSV.

    Sólo se modifican los píxeles del grano (alfa>0). El canal alfa no se toca.
    """
    bgr = bgra[:, :, :3]
    alpha = bgra[:, :, 3]

    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)

    # Offsets aleatorios.
    dh = rng.uniform(-cfg.hue_jitter, cfg.hue_jitter)
    ds = 1.0 + rng.uniform(-cfg.saturation_jitter, cfg.saturation_jitter)
    dv = 1.0 + rng.uniform(-cfg.value_jitter, cfg.value_jitter)

    hsv[:, :, 0] = (hsv[:, :, 0] + dh) % 180.0
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * ds, 0, 255)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * dv, 0, 255)

    bgr_out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    out = np.dstack([bgr_out, alpha])
    return out


def augment_grain(
    bgra: np.ndarray, cfg: AugmentConfig, rng: np.random.Generator
) -> np.ndarray:
    """Aplica geometría + fotometría en secuencia."""
    bgra = geometric_augment(bgra, cfg, rng)
    bgra = photometric_augment(bgra, cfg, rng)
    return bgra
