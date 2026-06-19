#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Pipeline completo de una sola pasada:
#   1) descarga dataset real + ETAPA 1 (banco de granos)
#   2) ETAPA 2 (dataset sintético + ground truth YOLO)
#   3) entrenamiento YOLO
#   4) evaluación de conteo + publicación de pesos para la demo
#
# Uso:
#   bash run_pipeline.sh
#
# Parámetros (override por variable de entorno):
#   SOURCE=kaggle|mendeley   N_IMAGES=500   EPOCHS=100
#   MODEL=yolov8s.pt         IMGSZ=1024     LIMIT_GRAINS=400
#   DEVICE=                  (vacío = auto; 'cpu' o '0' para forzar)
#
# Ej.: EPOCHS=50 MODEL=yolov8n.pt bash run_pipeline.sh
# ---------------------------------------------------------------------------
set -euo pipefail

SOURCE=${SOURCE:-kaggle}
N_IMAGES=${N_IMAGES:-500}
EPOCHS=${EPOCHS:-100}
MODEL=${MODEL:-yolov8s.pt}
IMGSZ=${IMGSZ:-1024}
LIMIT_GRAINS=${LIMIT_GRAINS:-400}
DEVICE=${DEVICE:-}

cd "$(dirname "$0")"
mkdir -p weights data

echo "==> 1/4  Dataset real + ETAPA 1 (banco de granos)"
python download_data.py --source "$SOURCE" --prepare \
    --limit "$LIMIT_GRAINS" --grains-dir data/grains

echo "==> 2/4  ETAPA 2 — dataset sintético ($N_IMAGES imágenes)"
python -m synthetic_data.generate etapa2 \
    --grains-dir data/grains --out-dir data/synthetic --n-images "$N_IMAGES"

echo "==> 3/4  Entrenamiento YOLO ($MODEL, $EPOCHS épocas, imgsz $IMGSZ)"
DEVICE_ARG=""
[ -n "$DEVICE" ] && DEVICE_ARG="--device $DEVICE"
python training/train.py --data data/synthetic/data.yaml \
    --model "$MODEL" --epochs "$EPOCHS" --imgsz "$IMGSZ" $DEVICE_ARG

echo "==> 4/4  Evaluación de conteo + publicación de pesos"
BEST=$(ls -t runs/poroto/*/weights/best.pt | head -1)
python training/evaluate_count.py --weights "$BEST" \
    --images data/synthetic/images/val --labels data/synthetic/labels/val
cp "$BEST" weights/best.pt
echo
echo "Pesos entrenados -> weights/best.pt"
echo "Levantá la demo con el modelo real:"
echo "  POROTO_WEIGHTS=weights/best.pt uvicorn inference.app:app --host 0.0.0.0 --port 8000"
