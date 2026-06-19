"""Esquemas de entrada/salida de la API de inferencia."""
from __future__ import annotations

from typing import List

from pydantic import BaseModel


class InferenceResponse(BaseModel):
    success: bool          # bandera: el resultado es confiable o no
    cantidad: int          # número de porotos detectados
    avg_confidence: float
    model_version: str
    image_id: str
    annotated_image_url: str
    metadata_url: str


class HealthResponse(BaseModel):
    status: str
    detector: str
    model_version: str
