FROM python:3.11-slim

# Dependencias de sistema para OpenCV.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY inference ./inference
COPY frontend ./frontend

# Repositorio persistente (montar como volumen en producción).
ENV POROTO_REPO=/app/repositorio
RUN mkdir -p /app/repositorio/imagenes /app/repositorio/metadatos

# Si tenés pesos YOLO entrenados, montalos y seteá:
#   -e POROTO_WEIGHTS=/app/weights/best.pt
EXPOSE 8000
CMD ["uvicorn", "inference.app:app", "--host", "0.0.0.0", "--port", "8000"]
