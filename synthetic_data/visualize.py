"""Utilidad para dibujar las cajas YOLO sobre una imagen (control visual)."""
from __future__ import annotations

import os
from glob import glob

import cv2
import numpy as np


def draw_yolo(img: np.ndarray, label_path: str) -> np.ndarray:
    H, W = img.shape[:2]
    out = img.copy()
    if not os.path.exists(label_path):
        return out
    with open(label_path) as f:
        for line in f:
            parts = line.split()
            if len(parts) != 5:
                continue
            _, xc, yc, w, h = map(float, parts)
            x0 = int((xc - w / 2) * W)
            y0 = int((yc - h / 2) * H)
            x1 = int((xc + w / 2) * W)
            y1 = int((yc + h / 2) * H)
            cv2.rectangle(out, (x0, y0), (x1, y1), (0, 255, 0), 2)
    return out


def annotate_dir(images_dir: str, labels_dir: str, out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    for p in sorted(glob(os.path.join(images_dir, "*.jpg"))):
        name = os.path.splitext(os.path.basename(p))[0]
        img = cv2.imread(p)
        lbl = os.path.join(labels_dir, f"{name}.txt")
        vis = draw_yolo(img, lbl)
        n = sum(1 for _ in open(lbl)) if os.path.exists(lbl) else 0
        cv2.putText(vis, f"N={n}", (20, 45), cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, (0, 255, 255), 3)
        cv2.imwrite(os.path.join(out_dir, f"{name}_gt.jpg"), vis)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--images-dir", required=True)
    ap.add_argument("--labels-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    annotate_dir(a.images_dir, a.labels_dir, a.out_dir)
