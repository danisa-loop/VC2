"""
REPOSITORIO del diagrama: persiste (IMAGEN*, ARCHIVO_METADATOS).

Implementación local en disco. En producción esto sería S3 + DynamoDB; la
interfaz `save` se mantiene igual para poder cambiar el backend.
"""
from __future__ import annotations

import json
import os
from typing import Tuple

import cv2
import numpy as np


class LocalRepository:
    def __init__(self, root: str = "repositorio"):
        self.img_dir = os.path.join(root, "imagenes")
        self.meta_dir = os.path.join(root, "metadatos")
        os.makedirs(self.img_dir, exist_ok=True)
        os.makedirs(self.meta_dir, exist_ok=True)

    def save(self, image_id: str, annotated: np.ndarray, metadata: dict) -> Tuple[str, str]:
        img_path = os.path.join(self.img_dir, f"{image_id}.jpg")
        meta_path = os.path.join(self.meta_dir, f"{image_id}.json")
        cv2.imwrite(img_path, annotated)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        return img_path, meta_path
