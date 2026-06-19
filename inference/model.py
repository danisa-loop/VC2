"""
Wrappers de detección de porotos.

Se exponen dos detectores con la misma interfaz:

  - YOLODetector     -> usa Ultralytics YOLO si hay pesos entrenados.
  - ClassicalDetector -> respaldo de visión clásica (umbral + watershed)
                         para separar granos que se tocan. Permite correr la
                         demo end-to-end sin un modelo entrenado.

Ambos devuelven una lista de Detection(box, score, mask_opcional).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import cv2
import numpy as np


@dataclass
class Detection:
    x0: int
    y0: int
    x1: int
    y1: int
    score: float
    mask: Optional[np.ndarray] = None  # máscara binaria del tamaño de la imagen


class ClassicalDetector:
    """Detector sin entrenamiento: segmentación + watershed por marcadores.

    Pensado para imágenes con granos sobre fondo oscuro (como las sintéticas).
    No es el modelo final; es un respaldo honesto para la demo.
    """

    name = "classical-watershed"
    version = "cv-1.0"

    def __init__(self, min_area: int = 250):
        self.min_area = min_area

    def predict(self, bgr: np.ndarray) -> List[Detection]:
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        thresh = cv2.morphologyEx(
            thresh, cv2.MORPH_OPEN,
            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)),
            iterations=2,
        )

        # Fondo seguro / frente seguro vía transformada de distancia.
        sure_bg = cv2.dilate(thresh, np.ones((3, 3), np.uint8), iterations=3)
        dist = cv2.distanceTransform(thresh, cv2.DIST_L2, 5)
        _, sure_fg = cv2.threshold(dist, 0.45 * dist.max(), 255, 0)
        sure_fg = sure_fg.astype(np.uint8)
        unknown = cv2.subtract(sure_bg, sure_fg)

        n_markers, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0
        markers = cv2.watershed(bgr, markers)

        detections: List[Detection] = []
        for label in range(2, n_markers + 1):
            region = (markers == label).astype(np.uint8)
            area = int(region.sum())
            if area < self.min_area:
                continue
            ys, xs = np.where(region > 0)
            x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
            # "Confianza" heurística: compacidad del blob (área / área bbox).
            fill = area / max(1, (x1 - x0) * (y1 - y0))
            score = float(np.clip(0.55 + 0.45 * fill, 0.0, 0.99))
            detections.append(
                Detection(int(x0), int(y0), int(x1), int(y1), score, region * 255)
            )
        return detections


class YOLODetector:
    """Detector basado en Ultralytics YOLO (requiere pesos entrenados)."""

    name = "yolov8"

    def __init__(self, weights: str, conf: float = 0.25, imgsz: int = 1024):
        from ultralytics import YOLO  # import diferido
        self.model = YOLO(weights)
        self.conf = conf
        self.imgsz = imgsz
        self.version = f"yolov8-{weights}"

    def predict(self, bgr: np.ndarray) -> List[Detection]:
        res = self.model.predict(
            bgr, conf=self.conf, imgsz=self.imgsz, verbose=False
        )[0]
        detections: List[Detection] = []
        masks = getattr(res, "masks", None)
        for i, box in enumerate(res.boxes):
            x0, y0, x1, y1 = box.xyxy[0].cpu().numpy().astype(int)
            score = float(box.conf[0].cpu().numpy())
            m = None
            if masks is not None and masks.data is not None:
                m = (masks.data[i].cpu().numpy() * 255).astype(np.uint8)
                m = cv2.resize(m, (bgr.shape[1], bgr.shape[0]))
            detections.append(Detection(int(x0), int(y0), int(x1), int(y1), score, m))
        return detections


def build_detector(weights: Optional[str], conf: float = 0.25) -> object:
    """Devuelve YOLO si hay pesos válidos; si no, el detector clásico."""
    if weights:
        try:
            return YOLODetector(weights, conf=conf)
        except Exception as e:  # pesos ausentes o ultralytics no instalado
            print(f"[detector] YOLO no disponible ({e}); uso respaldo clásico.")
    return ClassicalDetector()
