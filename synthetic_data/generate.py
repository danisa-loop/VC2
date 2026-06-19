"""
Orquestador del pipeline de datos sintéticos (ETAPA 1 + ETAPA 2).

ETAPA 1  -> extracción de granos individuales desde fotos sobre fondo negro.
ETAPA 2  -> composición de imágenes sintéticas con su ground truth YOLO.

Uso típico:
    # 1) Extraer recortes de granos reales (si tenés fotos):
    python -m synthetic_data.generate etapa1 \
        --input-dir data/raw --grains-dir data/grains

    # 2) Generar el dataset sintético:
    python -m synthetic_data.generate etapa2 \
        --grains-dir data/grains --out-dir data/synthetic --n-images 200

    # Demo end-to-end sin fotos reales (usa granos procedurales):
    python -m synthetic_data.generate demo --out-dir samples --n-images 4
"""
from __future__ import annotations

import argparse
import json
import os
from glob import glob
from typing import List

import cv2
import numpy as np

from .config import PipelineConfig
from .extract import extract_grain
from .augment import augment_grain
from .compose import init_canvas, place_grains, sample_n_grains, Annotation
from .postprocess import apply_postprocess
from ._demo_grains import make_grain_bank


# --------------------------------------------------------------------------- #
# ETAPA 1
# --------------------------------------------------------------------------- #
def etapa1_extract(input_dir: str, grains_dir: str, cfg: PipelineConfig) -> int:
    os.makedirs(grains_dir, exist_ok=True)
    # Búsqueda recursiva: el dataset real trae subcarpetas por categoría.
    exts = ("png", "jpg", "jpeg", "bmp", "tif", "tiff")
    paths = []
    for root, _, files in os.walk(input_dir, followlinks=True):
        for fn in files:
            if fn.lower().rsplit(".", 1)[-1] in exts:
                paths.append(os.path.join(root, fn))
    paths = sorted(paths)
    n = 0
    for p in paths:
        bgr = cv2.imread(p, cv2.IMREAD_COLOR)
        if bgr is None:
            continue
        try:
            grain = extract_grain(bgr, cfg.extract)
        except ValueError:
            continue
        name = os.path.splitext(os.path.basename(p))[0]
        cv2.imwrite(os.path.join(grains_dir, f"{name}.png"), grain)
        n += 1
    print(f"[ETAPA 1] Recortes guardados: {n} -> {grains_dir}")
    return n


def load_grain_bank(grains_dir: str) -> List[np.ndarray]:
    paths = sorted(glob(os.path.join(grains_dir, "*.png")))
    bank = []
    for p in paths:
        g = cv2.imread(p, cv2.IMREAD_UNCHANGED)
        if g is not None and g.ndim == 3 and g.shape[2] == 4:
            bank.append(g)
    return bank


# --------------------------------------------------------------------------- #
# ETAPA 2  (incluye el subproceso "Generar imagen y metadatos")
# --------------------------------------------------------------------------- #
def generar_imagen_y_metadatos(
    bank: List[np.ndarray], cfg: PipelineConfig, rng: np.random.Generator
):
    """Subproceso del diagrama: arma UNA imagen sintética y sus etiquetas."""
    n_grains = sample_n_grains(cfg.compose, rng)

    # Elegir aleatoriamente y aumentar cada grano.
    aug_grains = []
    for _ in range(n_grains):
        base = bank[rng.integers(0, len(bank))]
        aug_grains.append(augment_grain(base, cfg.augment, rng))

    canvas = init_canvas(cfg.compose, rng)
    annotations = place_grains(canvas, aug_grains, cfg.compose, rng)
    canvas = apply_postprocess(canvas, cfg.postprocess, rng)
    return canvas, annotations


def _write_sample(out_dir, split, name, img, anns: List[Annotation]):
    img_dir = os.path.join(out_dir, "images", split)
    lbl_dir = os.path.join(out_dir, "labels", split)
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(lbl_dir, exist_ok=True)
    cv2.imwrite(os.path.join(img_dir, f"{name}.jpg"), img)
    with open(os.path.join(lbl_dir, f"{name}.txt"), "w") as f:
        f.write("\n".join(a.to_yolo_line() for a in anns))


def etapa2_compose(
    grains_dir: str,
    out_dir: str,
    n_images: int,
    cfg: PipelineConfig,
    val_frac: float = 0.2,
    bank: List[np.ndarray] | None = None,
) -> None:
    rng = np.random.default_rng(cfg.seed)
    if bank is None:
        bank = load_grain_bank(grains_dir)
    if not bank:
        raise SystemExit(
            f"No hay granos en {grains_dir}. Corré la ETAPA 1 o usá 'demo'."
        )

    n_val = int(round(n_images * val_frac))
    counts = []
    for i in range(n_images):
        split = "val" if i < n_val else "train"
        img, anns = generar_imagen_y_metadatos(bank, cfg, rng)
        name = f"synth_{i:05d}"
        _write_sample(out_dir, split, name, img, anns)
        counts.append(len(anns))

    # data.yaml para Ultralytics YOLO.
    yaml_path = os.path.join(out_dir, "data.yaml")
    with open(yaml_path, "w") as f:
        f.write(
            f"path: {os.path.abspath(out_dir)}\n"
            f"train: images/train\n"
            f"val: images/val\n"
            f"nc: 1\n"
            f"names: ['{cfg.compose.class_name}']\n"
        )
    stats = {
        "n_images": n_images,
        "n_val": n_val,
        "grains_per_image_mean": float(np.mean(counts)) if counts else 0.0,
        "grains_per_image_min": int(np.min(counts)) if counts else 0,
        "grains_per_image_max": int(np.max(counts)) if counts else 0,
        "total_instances": int(np.sum(counts)),
    }
    with open(os.path.join(out_dir, "stats.json"), "w") as f:
        json.dump(stats, f, indent=2)
    print(f"[ETAPA 2] {n_images} imágenes -> {out_dir}")
    print(f"[ETAPA 2] stats: {stats}")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Pipeline de datos sintéticos de porotos")
    sub = p.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("etapa1", help="Extraer granos individuales")
    p1.add_argument("--input-dir", required=True)
    p1.add_argument("--grains-dir", required=True)

    p2 = sub.add_parser("etapa2", help="Componer dataset sintético")
    p2.add_argument("--grains-dir", required=True)
    p2.add_argument("--out-dir", required=True)
    p2.add_argument("--n-images", type=int, default=200)
    p2.add_argument("--val-frac", type=float, default=0.2)
    p2.add_argument("--seed", type=int, default=42)

    pd = sub.add_parser("demo", help="End-to-end con granos procedurales")
    pd.add_argument("--out-dir", required=True)
    pd.add_argument("--n-images", type=int, default=4)
    pd.add_argument("--bank-size", type=int, default=24)
    pd.add_argument("--seed", type=int, default=42)
    return p


def main(argv=None):
    args = _build_parser().parse_args(argv)
    cfg = PipelineConfig()

    if args.cmd == "etapa1":
        etapa1_extract(args.input_dir, args.grains_dir, cfg)
    elif args.cmd == "etapa2":
        cfg.seed = args.seed
        etapa2_compose(args.grains_dir, args.out_dir, args.n_images, cfg,
                       val_frac=args.val_frac)
    elif args.cmd == "demo":
        cfg.seed = args.seed
        rng = np.random.default_rng(cfg.seed)
        bank = make_grain_bank(args.bank_size, rng)
        etapa2_compose("(demo)", args.out_dir, args.n_images, cfg,
                       val_frac=0.25, bank=bank)


if __name__ == "__main__":
    main()
