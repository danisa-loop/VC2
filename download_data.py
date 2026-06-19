"""
Descarga y prepara un dataset real de porotos de soja para alimentar la ETAPA 1
(extracción de granos individuales) del pipeline sintético.

Dataset por defecto: "Soybean Seeds" (Nanjing Agricultural University)
  - Mendeley : https://data.mendeley.com/datasets/v6vzvfszj6  (DOI 10.17632/v6vzvfszj6)
  - Kaggle   : aryashah2k/soybean-seedsclassification-dataset (espejo)
  5513 imágenes de porotos individuales (227x227), en 5 categorías de calidad.
  Sirven directo como banco de granos para augment/compose.

Uso:
    # Opción A — Kaggle (recomendada; requiere token de Kaggle):
    python download_data.py --source kaggle --prepare --limit 300

    # Opción B — Mendeley (sin login):
    python download_data.py --source mendeley --prepare --limit 300

  --prepare corre la ETAPA 1 sobre las imágenes bajadas y deja el banco de
  granos RGBA en --grains-dir, listo para:
    python -m synthetic_data.generate etapa2 --grains-dir data/grains \
        --out-dir data/synthetic --n-images 500

Notas:
  - Las imágenes individuales traen el grano sobre un fondo relativamente
    uniforme; Otsu lo separa bien en la mayoría. Revisá unos PNG de salida.
  - El token de Kaggle se configura una vez: https://www.kaggle.com/settings
    (Create New Token -> ~/.kaggle/kaggle.json) o via KAGGLE_USERNAME/KAGGLE_KEY.
"""
from __future__ import annotations

import argparse
import os
import sys
import zipfile
from glob import glob

IMG_EXT = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff")
MENDELEY_ID = "v6vzvfszj6"


# --------------------------------------------------------------------------- #
# Descarga
# --------------------------------------------------------------------------- #
def download_kaggle(out_dir: str) -> str:
    """Baja el espejo de Kaggle vía kagglehub y copia a out_dir."""
    try:
        import kagglehub
    except ImportError:
        sys.exit("Falta kagglehub. Instalá:  pip install kagglehub")
    print("[kaggle] descargando dataset…")
    path = kagglehub.dataset_download("aryashah2k/soybean-seedsclassification-dataset")
    print(f"[kaggle] descargado en cache: {path}")
    os.makedirs(out_dir, exist_ok=True)
    # kagglehub deja una carpeta cacheada; la enlazamos/copiamos.
    import shutil
    for item in os.listdir(path):
        src = os.path.join(path, item)
        dst = os.path.join(out_dir, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
    return out_dir


def download_mendeley(out_dir: str) -> str:
    """Baja los archivos del dataset de Mendeley vía su API pública."""
    try:
        import requests
    except ImportError:
        sys.exit("Falta requests. Instalá:  pip install requests")
    os.makedirs(out_dir, exist_ok=True)

    # Última versión del dataset.
    base = f"https://data.mendeley.com/public-api/datasets/{MENDELEY_ID}"
    versions = requests.get(f"{base}/versions").json()
    version = max(int(v["version"]) for v in versions)
    print(f"[mendeley] versión {version}")

    files = requests.get(
        f"{base}/files", params={"version": version, "folder_id": "root"}
    ).json()

    for f in files:
        name = f.get("filename") or f.get("name")
        url = (f.get("content_details") or {}).get("download_url") or f.get("download_url")
        if not url:
            continue
        dst = os.path.join(out_dir, name)
        print(f"[mendeley] bajando {name}…")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(dst, "wb") as fh:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    fh.write(chunk)
        if name.lower().endswith(".zip"):
            print(f"[mendeley] descomprimiendo {name}…")
            with zipfile.ZipFile(dst) as z:
                z.extractall(out_dir)
    return out_dir


# --------------------------------------------------------------------------- #
# Preparación (ETAPA 1)
# --------------------------------------------------------------------------- #
def prepare_grains(raw_dir: str, grains_dir: str, limit: int | None) -> int:
    """Corre la ETAPA 1 (extracción) sobre las imágenes y arma el banco RGBA."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import cv2
    from synthetic_data.config import PipelineConfig
    from synthetic_data.extract import extract_grain

    cfg = PipelineConfig()
    os.makedirs(grains_dir, exist_ok=True)

    paths = []
    for root, _, _ in os.walk(raw_dir, followlinks=True):
        for ext in IMG_EXT:
            paths += glob(os.path.join(root, f"*{ext}"))
    paths = sorted(set(paths))
    if limit:
        paths = paths[:limit]

    n_ok = 0
    for i, p in enumerate(paths):
        bgr = cv2.imread(p, cv2.IMREAD_COLOR)
        if bgr is None:
            continue
        try:
            grain = extract_grain(bgr, cfg.extract)
        except ValueError:
            continue
        cv2.imwrite(os.path.join(grains_dir, f"grain_{i:05d}.png"), grain)
        n_ok += 1
    print(f"[prepare] banco de granos: {n_ok} -> {grains_dir}")
    if n_ok:
        print("[prepare] revisá unos PNG: el grano debe quedar opaco y el fondo transparente.")
    return n_ok


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description="Descarga y prepara dataset real de soja")
    ap.add_argument("--source", choices=["kaggle", "mendeley"], default="kaggle")
    ap.add_argument("--out", default="data/real_seeds", help="carpeta de descarga cruda")
    ap.add_argument("--grains-dir", default="data/grains", help="salida del banco RGBA")
    ap.add_argument("--prepare", action="store_true", help="correr ETAPA 1 tras bajar")
    ap.add_argument("--limit", type=int, default=None, help="tope de granos a preparar")
    args = ap.parse_args()

    if args.source == "kaggle":
        raw = download_kaggle(args.out)
    else:
        raw = download_mendeley(args.out)
    print(f"[ok] dataset en: {raw}")

    if args.prepare:
        prepare_grains(raw, args.grains_dir, args.limit)


if __name__ == "__main__":
    main()
