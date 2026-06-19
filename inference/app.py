"""
HTTP SERVER (FastAPI) del diagrama de inferencia.

Flujo:
  CLIENTE --POST(imagen)--> FastAPI --> CÓDIGO PYTHON --> MODELO
  MODELO --> CÓDIGO PYTHON --> {success, cantidad} --> CLIENTE
  FastAPI --> (IMAGEN*, METADATOS) --> REPOSITORIO

Variables de entorno:
  POROTO_WEIGHTS   ruta a pesos YOLO (si no existe, usa detector clásico)
  POROTO_CONF      umbral de confianza del modelo (default 0.25)
  POROTO_SUCCESS   threshold para la bandera success (default 0.5)
  POROTO_REPO      carpeta del repositorio (default ./repositorio)
"""
from __future__ import annotations

import os
import uuid

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .model import build_detector, ClassicalDetector
from .counter import count_and_annotate
from .repository import LocalRepository
from .schemas import InferenceResponse, HealthResponse

WEIGHTS = os.getenv("POROTO_WEIGHTS", "")
CONF = float(os.getenv("POROTO_CONF", "0.25"))
SUCCESS_TH = float(os.getenv("POROTO_SUCCESS", "0.5"))
REPO_ROOT = os.getenv("POROTO_REPO", "repositorio")

app = FastAPI(title="Contador de Porotos - Inferencia", version="1.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

detector = build_detector(WEIGHTS or None, conf=CONF)
repo = LocalRepository(REPO_ROOT)
MODEL_VERSION = getattr(detector, "version", "unknown")

# Servir el repositorio y el frontend como archivos estáticos.
app.mount("/repositorio", StaticFiles(directory=REPO_ROOT), name="repositorio")
_FRONT = os.path.join(os.path.dirname(__file__), "..", "frontend")


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        detector=getattr(detector, "name", type(detector).__name__),
        model_version=MODEL_VERSION,
    )


@app.post("/infer", response_model=InferenceResponse)
async def infer(file: UploadFile = File(...)):
    raw = await file.read()
    arr = np.frombuffer(raw, np.uint8)
    bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if bgr is None:
        raise HTTPException(400, "No se pudo decodificar la imagen.")

    image_id = uuid.uuid4().hex[:12]

    # MODELO -> CÓDIGO PYTHON
    detections = detector.predict(bgr)
    result = count_and_annotate(
        bgr, detections, image_id, MODEL_VERSION, success_threshold=SUCCESS_TH
    )

    # FastAPI -> REPOSITORIO
    img_path, meta_path = repo.save(image_id, result.annotated, result.metadata)

    return InferenceResponse(
        success=result.success,
        cantidad=result.cantidad,
        avg_confidence=round(result.avg_confidence, 4),
        model_version=MODEL_VERSION,
        image_id=image_id,
        annotated_image_url=f"/repositorio/imagenes/{image_id}.jpg",
        metadata_url=f"/repositorio/metadatos/{image_id}.json",
    )


@app.get("/")
def index():
    idx = os.path.join(_FRONT, "index.html")
    if os.path.exists(idx):
        return FileResponse(idx)
    return {"msg": "Frontend no encontrado. Ver /docs para la API."}
