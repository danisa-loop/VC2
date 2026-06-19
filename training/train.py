"""
Entrenamiento del detector de porotos con Ultralytics YOLO.

Requiere el dataset sintético generado por synthetic_data.generate (etapa2),
que ya deja el data.yaml listo.

Uso:
    python training/train.py --data data/synthetic/data.yaml \
        --model yolov8s.pt --epochs 100 --imgsz 1024

El conteo de porotos en inferencia es, simplemente, la cantidad de detecciones
por encima del umbral de confianza.
"""
from __future__ import annotations

import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="ruta al data.yaml")
    ap.add_argument("--model", default="yolov8s.pt",
                    help="checkpoint base (yolov8n/s/m.pt o -seg.pt)")
    ap.add_argument("--epochs", type=int, default=100)
    ap.add_argument("--imgsz", type=int, default=1024)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--project", default="runs/poroto")
    ap.add_argument("--name", default="exp")
    ap.add_argument("--device", default=None, help="auto si se omite; '0' GPU, 'cpu' o '0,1'")
    args = ap.parse_args()

    from ultralytics import YOLO

    model = YOLO(args.model)
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=args.project,
        name=args.name,
        device=args.device,
        # Importante: el dataset sintético ya trae augmentation a nivel grano.
        # Acá habilitamos sólo augmentation global moderada para no destruir
        # la coherencia de densidad/oclusión.
        mosaic=0.3,
        mixup=0.0,
        degrees=0.0,      # ya rotamos los granos individualmente
        translate=0.05,
        scale=0.2,
        fliplr=0.5,
        flipud=0.5,
        hsv_h=0.01, hsv_s=0.3, hsv_v=0.3,
        patience=25,
    )
    metrics = model.val()
    print("mAP50:", metrics.box.map50, "| mAP50-95:", metrics.box.map)
    print("Pesos:", f"{args.project}/{args.name}/weights/best.pt")


if __name__ == "__main__":
    main()
