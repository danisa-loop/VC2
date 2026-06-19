"""
Evaluación orientada a la TAREA real: contar porotos.

Más allá del mAP de detección, lo que importa es el error de conteo. Este
script compara la cantidad predicha vs. la del ground truth y reporta
MAE, RMSE y MAPE sobre el split de validación.

Uso:
    python training/evaluate_count.py --weights runs/poroto/exp/weights/best.pt \
        --images data/synthetic/images/val --labels data/synthetic/labels/val
"""
from __future__ import annotations

import argparse
import os
from glob import glob

import numpy as np


def count_gt(label_path: str) -> int:
    if not os.path.exists(label_path):
        return 0
    return sum(1 for line in open(label_path) if line.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True)
    ap.add_argument("--images", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--imgsz", type=int, default=1024)
    args = ap.parse_args()

    from ultralytics import YOLO
    model = YOLO(args.weights)

    gts, preds = [], []
    for img_path in sorted(glob(os.path.join(args.images, "*.jpg"))):
        name = os.path.splitext(os.path.basename(img_path))[0]
        gt = count_gt(os.path.join(args.labels, f"{name}.txt"))
        res = model.predict(img_path, conf=args.conf, imgsz=args.imgsz, verbose=False)[0]
        pred = len(res.boxes)
        gts.append(gt)
        preds.append(pred)

    gts, preds = np.array(gts), np.array(preds)
    err = preds - gts
    mae = np.mean(np.abs(err))
    rmse = np.sqrt(np.mean(err ** 2))
    mape = np.mean(np.abs(err) / np.maximum(gts, 1)) * 100
    print(f"Imágenes evaluadas : {len(gts)}")
    print(f"Conteo GT (prom)   : {gts.mean():.1f}")
    print(f"MAE  (granos)      : {mae:.2f}")
    print(f"RMSE (granos)      : {rmse:.2f}")
    print(f"MAPE (%)           : {mape:.1f}")


if __name__ == "__main__":
    main()
