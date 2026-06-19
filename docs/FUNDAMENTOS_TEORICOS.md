# Fundamentos teóricos — Conteo de porotos por visión por computadora

> Documento de respaldo. Explica el *por qué* de cada etapa del proyecto, con la
> teoría de visión por computadora detrás. Pensado para acompañar la defensa.

---

## 0. El problema y la decisión de diseño

La tarea es **detectar y contar** porotos de soja en una imagen. El cuello de
botella no es el modelo sino los **datos etiquetados**: anotar miles de imágenes
caja por caja es caro, lento y no cubre la variabilidad real.

**Decisión central:** generar **datos sintéticos** con *ground truth* automático.
Como nosotros colocamos cada grano en el lienzo, la etiqueta (caja/máscara) es
**exacta y determinista**, no estimada. Esto convierte el problema de "conseguir
datos" en uno de "diseñar un generador realista".

El sistema tiene tres bloques: **(1) generación sintética → (2) entrenamiento →
(3) inferencia/despliegue**.

---

## 1. Fase 1 — Segmentación y extracción del grano

### 1.1 Umbralizado de Otsu
Para separar el grano del fondo trabajamos sobre la **luminancia** (escala de
grises). El método de **Otsu** elige automáticamente el umbral `t*` que **maximiza
la varianza inter-clase** entre los dos grupos de píxeles (objeto y fondo):

```
t* = argmax_t  σ²_b(t),    σ²_b(t) = w₀(t)·w₁(t)·[μ₀(t) − μ₁(t)]²
```

donde `w₀, w₁` son las probabilidades (proporciones) de cada clase para el umbral
`t`, y `μ₀, μ₁` sus medias de intensidad. Maximizar la separación entre clases es
equivalente a minimizar la varianza intra-clase. Es **no paramétrico**: no hay que
fijar el umbral a mano.

**Auto-polaridad:** el objeto puede ser más claro (fondo negro) o más oscuro
(fondo claro) que el fondo. Para que funcione en ambos casos, si el **borde** de
la imagen queda marcado como objeto, invertimos la máscara — el fondo siempre debe
quedar transparente.

### 1.2 Canal alfa y recorte
La máscara binaria `M` se asigna al **canal alfa** de una imagen RGBA: el grano
queda opaco (α=255) y el fondo transparente (α=0). Luego recortamos a la **caja
delimitadora mínima** (bounding box) de los píxeles activos. Resultado: un "sticker"
RGBA compacto, reutilizable, que se puede pegar sin arrastrar fondo.

---

## 2. Fase 2 — Aumentación a nivel de componente

Antes de insertar un grano, lo perturbamos para simular variabilidad real.

- **Transformaciones geométricas (afines):** rotación `θ ∈ [0,360°)`, escala
  `s ∈ [s_min, s_max]`, y espejados. Una transformación afín preserva líneas y
  paralelismo; se aplica con una matriz `2×3` sobre las coordenadas. Rotar en todo
  el rango evita que el modelo aprenda una orientación preferida.
- **Transformaciones fotométricas (HSV):** convertimos a **HSV** y perturbamos
  Saturación y Valor (y levemente el Tono). HSV separa color de iluminación mejor
  que RGB, así que es el espacio natural para simular **madurez/humedad** (S) y
  **gradientes de luz** (V).

**Concepto clave — Domain Randomization:** aleatorizar lo que *no* importa (pose,
color, brillo) fuerza al modelo a apoyarse en lo *invariante* (la forma del grano).
Es la base teórica para reducir la **brecha sim-to-real**.

---

## 3. Fase 3 — Composición de la escena y ground truth

### 3.1 Alpha compositing (blending)
Pegamos cada grano sobre el lienzo con la **ecuación de composición sobre** ("over"
de Porter–Duff), por píxel:

```
I_out = α · F + (1 − α) · B
```

donde `F` es el grano (foreground), `B` el fondo acumulado y `α ∈ [0,1]` el canal
alfa. Esto produce bordes suaves (sin *aliasing*) en la periferia del grano, en
lugar de un recorte duro que el modelo podría aprender como artefacto.

### 3.2 Control de oclusión (IoU)
Para evitar que los granos se tapen completamente, mantenemos una **máscara global
de ocupación**. Antes de fijar un grano evaluamos su solapamiento con lo ya
ocupado. La medida estándar es la **Intersección sobre la Unión**:

```
IoU(A, B) = |A ∩ B| / |A ∪ B|
```

En la práctica usamos el solapamiento relativo al área del grano nuevo
(`|A ∩ ocupado| / |A|`). Si supera un umbral, reubicamos. Esto da **oclusión
controlada**: los granos pueden tocarse, pero no desaparecer.

### 3.3 Ground truth determinista
En el **mismo paso** en que ubicamos el grano, escribimos su etiqueta en formato
**YOLO**: `[class_id, x_center, y_center, width, height]` normalizado al tamaño del
lienzo. No hay anotación humana ni estimación: la etiqueta es correcta por
construcción.

---

## 4. Fase 4 — Postprocesamiento global

Una imagen "demasiado perfecta" delata su origen sintético: los bordes pegados
tienen una firma matemática distinta al fondo, y la red puede aprender ese atajo
en vez del objeto. Para evitarlo, sobre la **imagen completa** aplicamos:

- **Desenfoque gaussiano** sutil (simula lente/movimiento).
- **Ruido de sensor**: multiplicativo (speckle) y gaussiano de baja amplitud.

El objetivo es **unificar la firma óptica** de fondo y granos, cerrando una vía de
"trampa" para la red.

---

## 5. Entrenamiento

### 5.1 Esquema forward → pérdida → backprop
1. **Forward:** la imagen pasa por la red y produce una predicción (cajas + clase).
2. **Comparación:** se compara con el *ground truth* (las ubicaciones reales que
   generamos) mediante una **función de pérdida** `L` (combinación de error de
   caja, objetividad y clasificación).
3. **Backpropagation:** se calcula el gradiente `∂L/∂w` respecto de cada peso.
4. **Actualización:** un optimizador (SGD/Adam) ajusta los pesos en sentido
   contrario al gradiente. Se repite por épocas hasta converger.

### 5.2 Detector one-stage (YOLOv8)
YOLO es un detector de **una sola pasada**: predice cajas y clase directamente
sobre una grilla, sin etapa separada de propuestas (a diferencia de Faster R-CNN,
de dos etapas). Es **rápido y liviano**, ideal para servir una demo. El **conteo**
es simplemente la **cantidad de detecciones** por encima del umbral de confianza.

Elegimos YOLOv8 porque (a) el dataset ya sale en su formato de etiquetas y (b) es
liviano para desplegar. El pipeline es **agnóstico al modelo**: se podría usar
Faster R-CNN, segmentación por instancias o mapas de densidad.

---

## 6. Métricas: localizar vs. contar

- **mAP@50** (mean Average Precision con IoU≥0.5): mide la **calidad de
  localización** de las cajas. Es la métrica estándar de detección.
- **MAE / RMSE / MAPE** sobre el **conteo**: miden lo que de verdad importa al
  negocio — *cuántos granos hay*. 

> Una nota de criterio: en validación **in-distribution** (imágenes sintéticas de
> la misma distribución que el entrenamiento) el conteo puede ser casi perfecto
> (MAE≈0). Eso **valida el método y el pipeline**, pero **no** prueba la
> generalización al mundo real. Esa es la **brecha sim-to-real**, y su validación
> (con fotos reales etiquetadas) es el límite honesto del trabajo.

---

## 7. Inferencia y despliegue

Servicio **FastAPI**: el cliente envía la imagen por HTTP; un módulo de código
corre el modelo, **cuenta** y calcula la confianza promedio; se devuelve
`{success, cantidad}`. En paralelo se persiste en un repositorio:

- **IMAGEN\***: la imagen con cada grano marcado (caja/contorno) e **índice
  numérico**, para verificación visual humana.
- **Metadatos**: id, timestamp, versión del modelo, N de porotos y confianza.

La bandera **`success`** baja a `false` si la confianza promedio cae por debajo de
un umbral: le avisa al usuario que conviene **revisar esa imagen a mano**.

---

## 8. Limitaciones y trabajo futuro

- **Brecha sim-to-real:** sin un set real etiquetado, la generalización está sin
  medir. Próximo paso: validar (y eventualmente *fine-tunear*) con fotos reales.
- **Oclusión severa / granos partidos:** siguen siendo difíciles; los **mapas de
  densidad** son una alternativa para densidades muy altas.
- **Monitoreo en producción:** seguir la distribución de confianza y la tasa de
  `success=false` para detectar *drift*.

---

## Referencia del dataset

Lin, Wei; Fu, Youhao; Xu, Peiquan; Liu, Shuo; Ma, Daoyi; Jiang, Zitian; Zang,
Siyang; Yao, Heyang; Su, Qin (2023), *"Soybean Seeds"*, Mendeley Data, V5,
doi: 10.17632/v6vzvfszj6.5 — 5513 imágenes de porotos individuales (227×227) en
cinco categorías (Intact, Immature, Skin-damaged, Spotted, Broken).
