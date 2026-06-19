# INICIO RÁPIDO (ver el frontend en 5 minutos)

## Antes que nada: qué es cada cosa

- **El frontend / demo** = la página web donde subís una imagen y te cuenta los
  porotos. **Funciona YA, sin datos y sin entrenar** (trae un detector clásico de
  respaldo). Esto es lo que querés correr para ver la demo.
- **El notebook + los datos + el entrenamiento** = OPCIONAL, solo para mejorar el
  modelo más adelante. Eso va en Google Colab, después. No hace falta para la demo.

> No tenés que subir datos a ningún lado para ver el frontend.

---

## PARTE A — Ver el frontend (en tu compu)

**1. Descomprimí el zip.** Te queda una carpeta `poroto_cv/`. No abras ni edites
los archivos: es código, solo vas a correr comandos parada dentro de esa carpeta.

**2. Abrí una terminal en esa carpeta.**
- En VS Code: *File → Open Folder →* elegí `poroto_cv` → *Terminal → New Terminal*.
- O en WSL/Ubuntu: `cd /ruta/a/poroto_cv`

**3. Creá el entorno e instalá las dependencias** (copiar y pegar):
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
(En Windows PowerShell, la activación es `.venv\Scripts\Activate.ps1`.)

**4. Levantá el servidor — esto ES el frontend:**
```bash
uvicorn inference.app:app --host 0.0.0.0 --port 8000
```
Vas a ver `Uvicorn running on http://0.0.0.0:8000`. Dejá esa terminal corriendo.

**5. Abrí el navegador en** http://localhost:8000

**6. Probala:** clic en el visor → elegí una imagen de
`poroto_cv/samples/synthetic/images/train/` → botón **Analizar muestra**.
Te muestra el conteo, la confianza y la imagen con los porotos numerados.

Para frenar el servidor: `Ctrl + C` en la terminal.

---

## PARTE B — Que sea público (para la defensa)

Con el server corriendo, en OTRA terminal:
```bash
cloudflared tunnel --url http://localhost:8000
```
Te da un link `https://...trycloudflare.com` para compartir. La instalación de
cloudflared está en `docs/DEPLOY.md`.

---

## PARTE C — (Opcional, después) Entrenar el modelo de verdad

Esto NO es necesario para la demo. Es para cambiar el detector clásico por un
YOLO entrenado con datos reales.

- **¿Dónde corro el notebook?** En **Google Colab** (gratis, con GPU), no en tu
  compu. Entrá a https://colab.research.google.com → *Archivo → Subir cuaderno* →
  elegí `notebooks/train_colab.ipynb`. Arriba: *Entorno de ejecución → Cambiar
  tipo de entorno → GPU*.
- **¿Dónde subo los datos?** A ningún lado a mano. El notebook los **baja solo de
  Kaggle**. Solo necesitás tu credencial: en kaggle.com → *Settings → Create New
  Token* (se baja `kaggle.json`); el notebook te pide subir ese archivito.
- Seguí las celdas: subís el zip, subís `kaggle.json`, corre todo, y al final te
  descargás `best.pt`.
- **Usar el modelo entrenado en la demo:** poné `best.pt` en `poroto_cv/weights/`
  y levantá:
```bash
POROTO_WEIGHTS=weights/best.pt uvicorn inference.app:app --host 0.0.0.0 --port 8000
```

---

## Si algo falla

- **`uvicorn: command not found`** → te olvidaste de activar el entorno:
  `source .venv/bin/activate` y reintentá.
- **`pip install` se queja de "externally-managed-environment"** → estás sin el
  venv activado; hacé el paso 3 completo (el `python3 -m venv .venv` primero).
- **El puerto 8000 está ocupado** → usá otro: `--port 8001` y abrí
  `http://localhost:8001`.
- **La página carga pero "API offline"** → el server no está corriendo o lo
  cerraste; volvé al paso 4.
