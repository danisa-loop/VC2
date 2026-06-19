# Despliegue de la demo

La app de FastAPI **sirve el frontend en `/`**, así que la URL raíz del servicio
*es* la demo. CORS está abierto y el frontend usa el mismo origen, por lo que
funciona detrás de cualquier dominio sin tocar código.

Health check: `GET /health` · API: `POST /infer` · Docs: `/docs`.

---

## 0 · Local (recap)

```bash
pip install -r requirements.txt
uvicorn inference.app:app --host 0.0.0.0 --port 8000
# abrir http://localhost:8000
```

---

## 1 · URL pública instantánea (para la defensa / demo en vivo)

La forma más rápida de tener un link público sin desplegar nada: un túnel a tu
máquina local. Ideal para mostrarlo en clase. El link vive mientras corre el
proceso.

**Con cloudflared (sin cuenta):**

```bash
# Terminal 1: la app
uvicorn inference.app:app --host 0.0.0.0 --port 8000

# Terminal 2: instalar cloudflared (WSL/Ubuntu) y abrir el túnel
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
cloudflared tunnel --url http://localhost:8000
```

Te imprime una URL tipo `https://algo-al-azar.trycloudflare.com` → compartila.

**Alternativa con ngrok:**

```bash
ngrok http 8000     # requiere cuenta gratis + authtoken
```

> Limitación: el túnel se cae cuando cerrás la terminal o apagás la máquina. Para
> algo siempre disponible, usá la opción 2 o 3.

---

## 2 · Siempre disponible, sin AWS (Render — gratis)

1. Subí el proyecto a un repo de GitHub (incluye `Dockerfile` y `render.yaml`).
2. En https://render.com → **New → Blueprint** → elegí el repo. Render lee
   `render.yaml` y crea el servicio Docker solo.
   - O manual: **New → Web Service → Docker**, puerto `8000`, health check `/health`.
3. Te queda una URL fija `https://poroto-conteo.onrender.com`.

> El plan free duerme tras inactividad y tarda ~30 s en despertar en la primera
> request. Para demo está bien; para producción, plan pago.

Equivalentes igual de simples: **Railway**, **Fly.io** (`fly launch` lee el Dockerfile).

---

## 3 · AWS App Runner desde ECR (tu stack)

Despliegue gestionado desde la imagen Docker, con HTTPS y autoescalado, sin
manejar servidores.

```bash
ACCOUNT=<TU_ACCOUNT_ID>
REGION=us-east-1
REPO=poroto-infer

# 1) build
docker build -t $REPO .

# 2) crear repo ECR + login
aws ecr create-repository --repository-name $REPO --region $REGION
aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin $ACCOUNT.dkr.ecr.$REGION.amazonaws.com

# 3) tag + push
docker tag $REPO:latest $ACCOUNT.dkr.ecr.$REGION.amazonaws.com/$REPO:latest
docker push $ACCOUNT.dkr.ecr.$REGION.amazonaws.com/$REPO:latest
```

4. **App Runner → Create service → Container registry (ECR)** → elegí la imagen.
   - Puerto: `8000`. Health check: `/health`.
   - CPU/Mem: 1 vCPU / 2 GB alcanza para el detector clásico. Para YOLO subí a
     2 vCPU / 4 GB (o usá ECS/EC2 con GPU si el volumen lo justifica).
   - Variables: `POROTO_SUCCESS=0.5`, y `POROTO_WEIGHTS` si montás pesos.
5. App Runner te da una URL `https://xxxx.<region>.awsapprunner.com`.

### Persistencia en la nube

El `LocalRepository` escribe en disco efímero (se pierde al reiniciar). Para
producción, reemplazá `inference/repository.py` por una implementación S3 +
(opcional) DynamoDB para los metadatos, manteniendo la misma interfaz `save()`.
La IAM role del servicio necesita `s3:PutObject` sobre el bucket.

### Pesos del modelo

Para servir YOLO en la nube, horneá los pesos en la imagen (copialos en el
`Dockerfile`) o bajalos al arrancar desde S3, y seteá `POROTO_WEIGHTS`.

---

## Resumen

| Necesidad | Opción | URL |
|-----------|--------|-----|
| Mostrarlo ya, en vivo | cloudflared / ngrok | efímera, al instante |
| Algo fijo sin AWS | Render / Railway / Fly | fija, gratis |
| Producción en tu stack | AWS App Runner (ECR) | fija, HTTPS, autoescala |
