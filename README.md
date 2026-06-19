# Contador de porotos — visión por computadora

Sistema end-to-end para **contar y localizar porotos (granos de soja)** en una
imagen. El cuello de botella del problema es la falta de datos etiquetados, así
que el núcleo del proyecto es un **motor de generación de datos sintéticos** que
produce imágenes realistas con su *ground truth* automático, sobre el que se
entrena un detector. La inferencia se sirve por una API HTTP con un frontend de
demo.

```
poroto_cv/
├── synthetic_data/      # generación sintética (4 fases) + ground truth YOLO
├── training/            # entrenamiento YOLO + evaluación de conteo
├── inference/           # FastAPI + código de conteo + repositorio
├── frontend/            # demo web (panel de inspección)
├── samples/             # salidas de ejemplo ya generadas
└── docs/
```

## 1. Generación de datos sintéticos

Replica las 4 fases del documento de diseño:

| Fase | Módulo | Qué hace |
|------|--------|----------|
| 1. Extracción | `extract.py` | Otsu → máscara alfa → recorte a bbox (grano RGBA) |
| 2. Aumentación | `augment.py` | rotación/escala/flip + jitter HSV por grano |
| 3. Composición | `compose.py` | lienzo, control de oclusión (overlap), alpha blending, etiquetas YOLO |
| 4. Postproceso | `postprocess.py` | blur + ruido de sensor (speckle/gaussiano) |

```bash
pip install -r requirements.txt

# (a) Extraer granos reales desde fotos sobre fondo negro:
python -m synthetic_data.generate etapa1 --input-dir data/raw --grains-dir data/grains

# (b) Generar el dataset sintético + data.yaml:
python -m synthetic_data.generate etapa2 --grains-dir data/grains \
    --out-dir data/synthetic --n-images 500

# Demo sin fotos reales (granos procedurales, sólo para probar el pipeline):
python -m synthetic_data.generate demo --out-dir samples/synthetic --n-images 6

# Control visual de las cajas:
python -m synthetic_data.visualize \
    --images-dir samples/synthetic/images/train \
    --labels-dir samples/synthetic/labels/train --out-dir samples/viz
```

> Los parámetros estocásticos (rangos de escala, densidad de granos, umbral de
> oclusión, ruido, etc.) están centralizados en `synthetic_data/config.py`.

## 2. Entrenamiento

```bash
pip install -r requirements-train.txt
python training/train.py --data data/synthetic/data.yaml \
    --model yolov8s.pt --epochs 100 --imgsz 1024

# Evaluar el ERROR DE CONTEO (no sólo mAP):
python training/evaluate_count.py --weights runs/poroto/exp/weights/best.pt \
    --images data/synthetic/images/val --labels data/synthetic/labels/val
```

## 3. Inferencia + demo

El servicio reproduce el diagrama de inferencia: `cliente → FastAPI → código
Python → modelo`, devuelve `{success, cantidad}` y persiste `(IMAGEN*,
metadatos)` en el repositorio.

```bash
# Con detector clásico (sin pesos) — la demo corre igual:
uvicorn inference.app:app --host 0.0.0.0 --port 8000

# Con tu modelo entrenado:
POROTO_WEIGHTS=runs/poroto/exp/weights/best.pt uvicorn inference.app:app --port 8000
```

Abrí `http://localhost:8000/` para la demo. La API queda documentada en `/docs`.

| Variable | Default | Descripción |
|----------|---------|-------------|
| `POROTO_WEIGHTS` | (vacío) | pesos YOLO; si falta, usa detector clásico (watershed) |
| `POROTO_CONF` | `0.25` | umbral de confianza del modelo |
| `POROTO_SUCCESS` | `0.5` | umbral para la bandera `success` |
| `POROTO_REPO` | `repositorio` | carpeta del repositorio |

### Docker

```bash
docker build -t poroto-infer .
docker run -p 8000:8000 -v $(pwd)/repositorio:/app/repositorio poroto-infer
```

## Notas de diseño

- **`success`**: marca si el resultado es confiable. Es `false` cuando la
  confianza promedio cae por debajo del umbral; el frontend avisa para revisar a
  mano.
- **IMAGEN\***: la imagen de entrada con los contornos de cada grano y un índice
  numérico, para verificación visual humana.
- **Detector clásico de respaldo**: permite mostrar la demo end-to-end sin un
  modelo entrenado. No es el modelo final; es una línea de base honesta.

## Datos reales (banco de granos para la ETAPA 1)

```bash
pip install -r requirements-data.txt
python download_data.py --source kaggle --prepare --limit 300
# baja "Soybean Seeds" y deja el banco RGBA en data/grains
```

## Despliegue

Ver `docs/DEPLOY.md` — incluye URL pública instantánea (cloudflared/ngrok),
Render (gratis) y AWS App Runner. La app sirve el frontend en `/`, así que la
URL del servicio es la demo.

## Pipeline completo de una pasada (datos reales + entrenamiento)

```bash
# Local con GPU (o CPU para prueba chica):
bash run_pipeline.sh
# override: EPOCHS=50 MODEL=yolov8n.pt LIMIT_GRAINS=200 bash run_pipeline.sh

# Levantar la demo con el modelo entrenado:
POROTO_WEIGHTS=weights/best.pt uvicorn inference.app:app --host 0.0.0.0 --port 8000
```

¿Sin GPU local? Usá `notebooks/train_colab.ipynb` (GPU gratis en Google Colab):
subís el zip, tu `kaggle.json`, corrés todo y te bajás `best.pt`.
