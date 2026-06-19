"""
Generador de granos sintéticos "stand-in" para demo.

IMPORTANTE: esto NO reemplaza a la ETAPA 1 real (extracción desde fotos de
porotos sobre fondo negro). Sirve únicamente para poder ejecutar el pipeline
completo y mostrar salidas cuando todavía no hay un banco de recortes reales.

Cuando tengas tus fotos reales, corré la ETAPA 1 (extract_grain) y guardá los
recortes RGBA en --grains-dir; el resto del pipeline no cambia.
"""
from __future__ import annotations

import cv2
import numpy as np


# Paleta tipo soja: tonos beige/marrón claro en BGR.
_SOY_COLORS = [
    (120, 170, 205),
    (110, 160, 200),
    (130, 180, 215),
    (95, 150, 190),
    (140, 185, 220),
]


def make_grain(rng: np.random.Generator, size: int = 90) -> np.ndarray:
    """Crea un grano elíptico con textura y sombreado, en BGRA recortado."""
    canvas = np.zeros((size, size, 4), dtype=np.uint8)
    cx, cy = size // 2, size // 2
    ax = int(rng.integers(int(size * 0.30), int(size * 0.42)))
    ay = int(rng.integers(int(size * 0.22), int(size * 0.34)))
    angle = float(rng.uniform(0, 180))
    color = list(_SOY_COLORS[rng.integers(0, len(_SOY_COLORS))])

    mask = np.zeros((size, size), dtype=np.uint8)
    cv2.ellipse(mask, (cx, cy), (ax, ay), angle, 0, 360, 255, -1)

    bgr = np.zeros((size, size, 3), dtype=np.uint8)
    cv2.ellipse(bgr, (cx, cy), (ax, ay), angle, 0, 360, color, -1)

    # Sombreado radial sutil para dar volumen.
    yy, xx = np.mgrid[0:size, 0:size]
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    shade = np.clip(1.15 - dist / (size * 0.6), 0.6, 1.15)[:, :, None]
    bgr = np.clip(bgr.astype(np.float32) * shade, 0, 255).astype(np.uint8)

    # Hilio (la "cicatriz" del poroto): una línea más oscura.
    p1 = (int(cx - ax * 0.6 * np.cos(np.radians(angle))),
          int(cy - ax * 0.6 * np.sin(np.radians(angle))))
    p2 = (int(cx + ax * 0.6 * np.cos(np.radians(angle))),
          int(cy + ax * 0.6 * np.sin(np.radians(angle))))
    cv2.line(bgr, p1, p2, (60, 90, 120), 2)

    # Textura: ruido leve sólo dentro de la máscara.
    noise = rng.normal(0, 6, size=(size, size, 3)).astype(np.float32)
    bgr = np.clip(bgr.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    out = np.dstack([bgr, mask])
    ys, xs = np.where(mask > 0)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()


def make_grain_bank(n: int, rng: np.random.Generator) -> list[np.ndarray]:
    return [make_grain(rng) for _ in range(n)]
