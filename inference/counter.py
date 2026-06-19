"""
"CÓDIGO PYTHON" del diagrama de inferencia.

Toma el resultado crudo del modelo y:
  - cuenta la cantidad de porotos detectados,
  - calcula el vector/promedio de confianza,
  - decide la bandera `success` según un threshold,
  - dibuja la IMAGEN* (contornos + índice numérico por grano),
  - arma el diccionario de metadatos.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Tuple

import cv2
import numpy as np

from .model import Detection


@dataclass
class CountResult:
    success: bool
    cantidad: int
    avg_confidence: float
    confidences: List[float]
    annotated: np.ndarray          # IMAGEN*
    metadata: dict                 # ARCHIVO_METADATOS (dict serializable)


def _draw_imagen_estrella(
    bgr: np.ndarray, detections: List[Detection]
) -> np.ndarray:
    """IMAGEN*: contornos de las máscaras + índice numérico por grano."""
    out = bgr.copy()
    for i, d in enumerate(detections, start=1):
        color = (0, 255, 0)
        if d.mask is not None:
            cnts, _ = cv2.findContours(
                d.mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            cv2.drawContours(out, cnts, -1, color, 2)
        else:
            cv2.rectangle(out, (d.x0, d.y0), (d.x1, d.y1), color, 2)
        cx, cy = (d.x0 + d.x1) // 2, (d.y0 + d.y1) // 2
        cv2.putText(out, str(i), (cx - 8, cy + 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(out, str(i), (cx - 8, cy + 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def count_and_annotate(
    bgr: np.ndarray,
    detections: List[Detection],
    image_id: str,
    model_version: str,
    success_threshold: float = 0.5,
) -> CountResult:
    confidences = [round(float(d.score), 4) for d in detections]
    cantidad = len(detections)
    avg_conf = float(np.mean(confidences)) if confidences else 0.0

    # `success` = la corrida es confiable. False si el promedio cae por debajo
    # del threshold o si no se detectó nada -> se avisa al usuario que hubo un
    # problema con la detección en esa imagen.
    success = bool(cantidad > 0 and avg_conf >= success_threshold)

    annotated = _draw_imagen_estrella(bgr, detections)

    metadata = {
        "image_id": image_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_version": model_version,
        "n_porotos": cantidad,
        "avg_confidence": round(avg_conf, 4),
        "confidences": confidences,
        "success": success,
        "success_threshold": success_threshold,
    }
    return CountResult(success, cantidad, avg_conf, confidences, annotated, metadata)
