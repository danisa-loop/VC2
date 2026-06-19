const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.layout = "LAYOUT_WIDE";          // 13.3 x 7.5
p.author = "Dani";
p.title = "Conteo de porotos por visión por computadora";

const W = 13.3, H = 7.5;
const A = "/home/claude/poroto_cv/docs/deck_assets/";

// Paleta agro/soja (consistente con la demo)
const C = {
  dark:   "14201A",
  dark2:  "1C2C24",
  light:  "F4F6F3",
  card:   "FFFFFF",
  soy:    "C68A3E",   // tan legible sobre claro
  soyL:   "D8A657",
  green:  "2F7D52",   // verde señal legible sobre claro
  greenL: "4ADE80",
  text:   "16231C",
  muted:  "5A6F62",
  lineL:  "DCE4DD",
  lineD:  "33503F",
};
const FT = "Calibri";

const sh = (o) => Object.assign({ type:"outer", color:"16231C", blur:9, offset:3, angle:90, opacity:0.10 }, o||{});

// Marcador "semilla" (motivo repetido)
function seed(s, x, y, d=0.32, color=C.soyL) {
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w:d, h:d, rectRadius:d/2.3,
    fill:{ color }, line:{ type:"none" }, rotate:8 });
}
let page = 0;
function footer(s, dark=false) {
  page++;
  s.addText(`Conteo de porotos · VC II — FIUBA`,
    { x:0.5, y:H-0.42, w:8, h:0.3, fontSize:9, color: dark?C.muted:C.muted, fontFace:FT });
  s.addText(String(page),
    { x:W-1.0, y:H-0.42, w:0.5, h:0.3, fontSize:9, color:C.muted, align:"right", fontFace:FT });
}
function header(s, kicker, title) {
  seed(s, 0.5, 0.52);
  s.addText(kicker.toUpperCase(), { x:0.95, y:0.45, w:9, h:0.3, fontSize:11.5,
    color:C.soy, charSpacing:3, bold:true, fontFace:FT, margin:0 });
  s.addText(title, { x:0.5, y:0.78, w:12.3, h:0.85, fontSize:30, bold:true,
    color:C.text, fontFace:FT, margin:0 });
}

// ---------------------------------------------------------------- 1 · TÍTULO
(() => {
  const s = p.addSlide(); s.background = { color:C.dark };
  s.addImage({ path:A+"bg_dense_clean.jpg", x:8.55, y:0, w:H*1.0, h:H,
    sizing:{ type:"cover", w:H*1.0, h:H }, transparency:18 });
  s.addShape(p.shapes.RECTANGLE, { x:8.55, y:0, w:W-8.55, h:H,
    fill:{ color:C.dark, transparency:32 }, line:{ type:"none" } });
  seed(s, 0.85, 1.5, 0.5);
  s.addText("VISIÓN POR COMPUTADORA II · FIUBA", { x:1.5, y:1.5, w:7, h:0.4,
    fontSize:13, color:C.soyL, charSpacing:3, bold:true, fontFace:FT, margin:0 });
  s.addText("Conteo de porotos\npor visión por computadora",
    { x:0.85, y:2.25, w:8.2, h:1.9, fontSize:42, bold:true, color:"FFFFFF",
      fontFace:FT, lineSpacingMultiple:1.0, margin:0 });
  s.addText("Generación de datos sintéticos · detección · despliegue con demo",
    { x:0.9, y:4.25, w:7.6, h:0.5, fontSize:16, color:"CFE0D4", fontFace:FT, margin:0 });
  s.addShape(p.shapes.LINE, { x:0.9, y:5.05, w:3.0, h:0, line:{ color:C.lineD, width:1 } });
  s.addText([
    { text:"Pipeline end-to-end", options:{ color:"E8EFE9", bold:true, breakLine:true } },
    { text:"datos → entrenamiento → API + frontend", options:{ color:C.muted } },
  ], { x:0.9, y:5.2, w:7, h:0.7, fontSize:13, fontFace:FT, margin:0 });
  s.addNotes("Presentarme y dar el titulo en una frase: contar y ubicar porotos de soja en una imagen, con vision por computadora. Anticipar la idea fuerza: el problema no es el modelo, es conseguir datos etiquetados, y lo resolvemos generandolos. Mencionar que cierro con una demo en vivo. ~30 segundos, no leer la slide.");
  footer(s, true);
})();

// ---------------------------------------------------------------- 2 · PROBLEMA
(() => {
  const s = p.addSlide(); s.background = { color:C.light };
  header(s, "El problema", "Contar granos a mano no escala");
  s.addNotes("El conteo manual es lento y subjetivo: dos personas cuentan distinto sobre la misma bandeja. Aterrizar el caso de control de calidad de soja. El mensaje central es el cuello de botella: lo caro es etiquetar miles de imagenes caja por caja, no entrenar. Esto justifica todo lo que sigue. ~1 minuto.");
  const txt = [
    { text:"En control de calidad de granos (soja), contar y localizar cada poroto en una muestra es ", options:{} },
    { text:"lento, tedioso y subjetivo", options:{ bold:true, color:C.text } },
    { text:". Dos personas cuentan distinto sobre la misma bandeja.", options:{} },
  ];
  s.addText(txt, { x:0.5, y:1.9, w:6.6, h:1.4, fontSize:16.5, color:C.muted,
    fontFace:FT, lineSpacingMultiple:1.15, valign:"top" });
  const cuello = [
    { text:"El verdadero cuello de botella", options:{ bold:true, color:C.text, breakLine:true } },
    { text:"No es el modelo: es conseguir miles de imágenes etiquetadas caja por caja. Anotar a mano es carísimo y no cubre toda la variabilidad real.", options:{ color:C.muted } },
  ];
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x:0.5, y:3.5, w:6.6, h:1.7, rectRadius:0.12,
    fill:{ color:C.card }, line:{ color:C.lineL, width:1 }, shadow:sh() });
  s.addText(cuello, { x:0.8, y:3.72, w:6.0, h:1.3, fontSize:14.5, fontFace:FT,
    lineSpacingMultiple:1.12, valign:"top" });
  // stats
  const stat = (x,y,n,l) => {
    s.addText(n, { x, y, w:2.7, h:0.8, fontSize:40, bold:true, color:C.soy, fontFace:FT, margin:0 });
    s.addText(l, { x, y:y+0.82, w:2.7, h:0.6, fontSize:12.5, color:C.muted, fontFace:FT, margin:0 });
  };
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x:7.5, y:1.9, w:5.3, h:3.3, rectRadius:0.12,
    fill:{ color:C.dark }, line:{ type:"none" }, shadow:sh() });
  s.addText("Lo que pedimos al sistema", { x:7.8, y:2.15, w:4.7, h:0.4, fontSize:13,
    color:C.soyL, bold:true, charSpacing:1, fontFace:FT, margin:0 });
  const statD = (x,y,n,l) => {
    s.addText(n, { x, y, w:2.4, h:0.7, fontSize:34, bold:true, color:"FFFFFF", fontFace:FT, margin:0 });
    s.addText(l, { x, y:y+0.7, w:2.4, h:0.6, fontSize:11.5, color:"AFC6B7", fontFace:FT, margin:0 });
  };
  statD(7.8, 2.75, "N", "cantidad exacta de granos");
  statD(10.4, 2.75, "(x,y)", "ubicación de cada uno");
  statD(7.8, 4.05, "✓/✗", "señal de confianza");
  statD(10.4, 4.05, "seg", "por imagen, repetible");
  footer(s);
})();

// ---------------------------------------------------------------- 3 · ENFOQUE
(() => {
  const s = p.addSlide(); s.background = { color:C.light };
  header(s, "Enfoque", "Una solución en tres bloques");
  s.addNotes("Mapa de la charla en tres bloques: datos sinteticos, entrenamiento, inferencia con demo. Dejar claro que el peso del trabajo esta en el bloque 1; los otros dos son consecuencia. Usar las flechas para contar la historia de izquierda a derecha. ~1 minuto.");
  const blocks = [
    ["1", "Datos sintéticos", "Generamos imágenes realistas con su ground truth automático. Resuelve la falta de datos etiquetados."],
    ["2", "Entrenamiento", "Un detector (YOLOv8) aprende a localizar cada grano. La métrica que importa es el error de conteo."],
    ["3", "Inferencia + demo", "API HTTP (FastAPI) que devuelve cantidad y confianza, más un frontend de inspección."],
  ];
  const bw=3.95, gap=0.45, x0=0.5, y0=2.4, bh=3.0;
  blocks.forEach((b,i) => {
    const x = x0 + i*(bw+gap);
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y:y0, w:bw, h:bh, rectRadius:0.12,
      fill:{ color:C.card }, line:{ color:C.lineL, width:1 }, shadow:sh() });
    s.addShape(p.shapes.OVAL, { x:x+0.35, y:y0+0.35, w:0.7, h:0.7, fill:{ color:C.dark }, line:{type:"none"} });
    s.addText(b[0], { x:x+0.35, y:y0+0.37, w:0.7, h:0.66, fontSize:24, bold:true,
      color:C.soyL, align:"center", valign:"middle", fontFace:FT, margin:0 });
    s.addText(b[1], { x:x+0.35, y:y0+1.2, w:bw-0.7, h:0.6, fontSize:18, bold:true,
      color:C.text, fontFace:FT, margin:0 });
    s.addText(b[2], { x:x+0.35, y:y0+1.85, w:bw-0.7, h:1.0, fontSize:13, color:C.muted,
      fontFace:FT, lineSpacingMultiple:1.1, valign:"top", margin:0 });
    if (i<2) s.addText("→", { x:x+bw+0.02, y:y0+1.2, w:0.4, h:0.5, fontSize:22,
      color:C.soy, align:"center", fontFace:FT, margin:0 });
  });
  s.addText("El núcleo del trabajo está en el bloque 1: sin datos, no hay modelo.",
    { x:0.5, y:5.7, w:12, h:0.4, fontSize:13.5, italic:true, color:C.green, fontFace:FT });
  footer(s);
})();

// ---------------------------------------------------------------- 4 · POR QUÉ SINTÉTICO
(() => {
  const s = p.addSlide(); s.background = { color:C.light };
  header(s, "Datos sintéticos", "Por qué generarlos en vez de anotarlos");
  s.addNotes("Cuatro razones: etiqueta perfecta y gratis, control de densidad y oclusion, variabilidad infinita y costo casi cero. Si queda una sola, que sea la etiqueta perfecta: sabemos donde pusimos cada grano, asi que la caja sale exacta sin error humano. ~1 minuto y medio.");
  const items = [
    ["Etiqueta perfecta y gratis", "Sabemos dónde pusimos cada grano: la caja y la máscara salen exactas, sin error humano."],
    ["Control de densidad y oclusión", "Definimos cuántos granos y cuánto se solapan. Forzamos al modelo a generalizar."],
    ["Variabilidad infinita", "Rotación, escala, color y madurez aleatorios por grano simulan la variación biológica."],
    ["Costo marginal ≈ 0", "Una vez armado el pipeline, generar 10.000 imágenes etiquetadas es cuestión de minutos."],
  ];
  const cw=6.0, ch=1.55, gx=0.6, gy=0.35, x0=0.5, y0=2.35;
  items.forEach((it,i) => {
    const x = x0 + (i%2)*(cw+gx), y = y0 + Math.floor(i/2)*(ch+gy);
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w:cw, h:ch, rectRadius:0.1,
      fill:{ color:C.card }, line:{ color:C.lineL, width:1 }, shadow:sh() });
    seed(s, x+0.35, y+0.35, 0.34, C.soy);
    s.addText(it[0], { x:x+0.95, y:y+0.28, w:cw-1.2, h:0.45, fontSize:16.5, bold:true,
      color:C.text, fontFace:FT, margin:0 });
    s.addText(it[1], { x:x+0.95, y:y+0.74, w:cw-1.2, h:0.7, fontSize:13, color:C.muted,
      fontFace:FT, lineSpacingMultiple:1.08, valign:"top", margin:0 });
  });
  footer(s);
})();

// ---------------------------------------------------------------- 5 · DIVISOR 4 FASES
(() => {
  const s = p.addSlide(); s.background = { color:C.dark };
  s.addImage({ path:A+"bg_sparse_clean.jpg", x:8.7, y:0, w:H, h:H,
    sizing:{ type:"cover", w:H, h:H }, transparency:22 });
  s.addShape(p.shapes.RECTANGLE, { x:8.7, y:0, w:W-8.7, h:H,
    fill:{ color:C.dark, transparency:38 }, line:{type:"none"} });
  seed(s, 0.85, 1.25, 0.5);
  s.addNotes("Slide bisagra: presento el motor de datos y las cuatro fases que voy a recorrer. Es un indice, no detenerme: leer los cuatro titulos y pasar. ~30 segundos.");
  s.addText("EL MOTOR DE DATOS", { x:1.5, y:1.27, w:7, h:0.4, fontSize:13,
    color:C.soyL, charSpacing:3, bold:true, fontFace:FT, margin:0 });
  s.addText("Generación sintética en 4 fases", { x:0.85, y:1.85, w:8, h:1.0,
    fontSize:34, bold:true, color:"FFFFFF", fontFace:FT, margin:0 });
  const ph = [
    ["1 · Extracción", "aislar el grano y estandarizarlo (máscara alfa + recorte)"],
    ["2 · Aumentación", "variar cada grano: geometría + fotometría (HSV)"],
    ["3 · Composición", "armar la escena con oclusión controlada y generar el ground truth"],
    ["4 · Postproceso", "unificar la firma óptica: desenfoque + ruido de sensor"],
  ];
  ph.forEach((x,i) => {
    const y = 3.0 + i*0.92;
    s.addText(x[0], { x:0.9, y, w:3.1, h:0.5, fontSize:17, bold:true, color:C.soyL, fontFace:FT, margin:0 });
    s.addText(x[1], { x:3.9, y:y+0.03, w:4.6, h:0.6, fontSize:13, color:"CFE0D4",
      fontFace:FT, lineSpacingMultiple:1.05, valign:"top", margin:0 });
  });
  footer(s, true);
})();

// ---------------------------------------------------------------- 6 · FASE 1+2
(() => {
  const s = p.addSlide(); s.background = { color:C.light };
  header(s, "Fases 1 y 2", "Del grano crudo al grano variado");
  s.addNotes("Fase 1: separar el grano del fondo con Otsu, llevar la mascara al canal alfa y recortar a la bounding box; cada grano queda como un sticker RGBA reutilizable. Fase 2: a cada grano le aplico rotacion, escala, flips y jitter de color en HSV. La imagen de la derecha es el mismo grano en seis variantes. ~1 minuto y medio.");
  // izquierda texto
  s.addText("Fase 1 · Extracción", { x:0.5, y:1.95, w:6, h:0.4, fontSize:17, bold:true, color:C.green, fontFace:FT, margin:0 });
  s.addText([
    { text:"Umbralizado Otsu sobre luminancia → máscara binaria.", options:{ bullet:true, breakLine:true } },
    { text:"La máscara va al canal alfa (grano opaco, fondo transparente).", options:{ bullet:true, breakLine:true } },
    { text:"Recorte a la bounding box → grano RGBA compacto.", options:{ bullet:true } },
  ], { x:0.6, y:2.4, w:6.3, h:1.5, fontSize:13.5, color:C.muted, fontFace:FT, paraSpaceAfter:6, valign:"top" });
  s.addText("Fase 2 · Aumentación por grano", { x:0.5, y:4.0, w:6, h:0.4, fontSize:17, bold:true, color:C.green, fontFace:FT, margin:0 });
  s.addText([
    { text:"Geométrica: rotación 0–360°, escala 0.8–1.2×, flips.", options:{ bullet:true, breakLine:true } },
    { text:"Fotométrica: jitter en HSV (madurez, humedad, iluminación).", options:{ bullet:true, breakLine:true } },
    { text:"Cada inserción es un grano distinto → evita sesgos.", options:{ bullet:true } },
  ], { x:0.6, y:4.45, w:6.3, h:1.5, fontSize:13.5, color:C.muted, fontFace:FT, paraSpaceAfter:6, valign:"top" });
  // derecha imagen
  const iw=5.4, ih=iw/1.5;
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x:7.25, y:2.55, w:iw+0.3, h:ih+0.8, rectRadius:0.1,
    fill:{ color:C.card }, line:{ color:C.lineL, width:1 }, shadow:sh() });
  s.addImage({ path:A+"augment_grid.jpg", x:7.4, y:2.7, w:iw, h:ih });
  s.addText("Un mismo grano, 6 variantes generadas automáticamente",
    { x:7.4, y:2.72+ih, w:iw, h:0.4, fontSize:11.5, italic:true, color:C.muted, align:"center", fontFace:FT, margin:0 });
  footer(s);
})();

// ---------------------------------------------------------------- 7 · FASE 3
(() => {
  const s = p.addSlide(); s.background = { color:C.light };
  header(s, "Fase 3", "Composición y ground truth automático");
  s.addNotes("El corazon del pipeline. Armo un lienzo, decido cuantos granos (20 a 150) y los voy pegando controlando con una mascara de ocupacion que no se tapen del todo. El blending por alfa evita bordes duros. Lo clave: en el mismo paso escribo la etiqueta YOLO exacta de cada grano. La imagen muestra las cajas generadas solas. Ir mas lento aca. ~2 minutos.");
  const img=4.7;
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x:0.5, y:2.0, w:img+0.3, h:img+0.3, rectRadius:0.1,
    fill:{ color:C.card }, line:{ color:C.lineL, width:1 }, shadow:sh() });
  s.addImage({ path:A+"synth_sparse_gt.jpg", x:0.65, y:2.15, w:img, h:img });
  s.addText("Imagen sintética + cajas YOLO generadas (verde)",
    { x:0.5, y:2.0+img+0.32, w:img+0.3, h:0.4, fontSize:11.5, italic:true, color:C.muted, align:"center", fontFace:FT });
  const steps = [
    ["Lienzo y densidad", "Fondo objetivo + N granos aleatorio (20–150) para cubrir muchas densidades."],
    ["Control de oclusión", "Máscara global de ocupación; si el solapamiento supera el umbral, se reubica."],
    ["Alpha blending", "Iₛ = α·grano + (1−α)·fondo. Sin bordes duros ni aliasing."],
    ["Etiquetas exactas", "Se escribe [class, x, y, w, h] normalizado por grano, en el mismo paso."],
  ];
  let y=2.05;
  steps.forEach((st) => {
    seed(s, 6.0, y+0.06, 0.3, C.soy);
    s.addText(st[0], { x:6.5, y, w:6.3, h:0.4, fontSize:16, bold:true, color:C.text, fontFace:FT, margin:0 });
    s.addText(st[1], { x:6.5, y:y+0.42, w:6.3, h:0.6, fontSize:13, color:C.muted, fontFace:FT, lineSpacingMultiple:1.05, valign:"top", margin:0 });
    y += 1.18;
  });
  footer(s);
})();

// ---------------------------------------------------------------- 8 · FASE 4 + DATASET
(() => {
  const s = p.addSlide(); s.background = { color:C.light };
  header(s, "Fase 4 y dataset", "Realismo de sensor y escena densa");
  s.addNotes("Fase 4: con la escena armada, le paso desenfoque y ruido de sensor a TODA la imagen para que fondo y granos compartan la misma firma optica; si no, la red aprende a detectar el borde sintetico en vez del grano. Mostrar las dos variantes (textura y alta densidad) y los numeros del dataset. ~1 minuto y medio.");
  // dos imágenes
  const iw=3.55;
  s.addImage({ path:A+"texture_bg.jpg", x:0.5, y:2.05, w:iw, h:iw, rounding:false });
  s.addText("Fondo con textura (cinta/tolva)", { x:0.5, y:2.05+iw+0.05, w:iw, h:0.35, fontSize:11, italic:true, color:C.muted, align:"center", fontFace:FT, margin:0 });
  s.addImage({ path:A+"synth_dense_gt.jpg", x:4.25, y:2.05, w:iw, h:iw });
  s.addText("Alta densidad (N=93) con oclusión", { x:4.25, y:2.05+iw+0.05, w:iw, h:0.35, fontSize:11, italic:true, color:C.muted, align:"center", fontFace:FT, margin:0 });
  // panel derecha
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x:8.2, y:2.05, w:4.6, h:4.05, rectRadius:0.12,
    fill:{ color:C.dark }, line:{type:"none"}, shadow:sh() });
  s.addText("Fase 4 · Postproceso global", { x:8.5, y:2.25, w:4, h:0.4, fontSize:15, bold:true, color:C.soyL, fontFace:FT, margin:0 });
  s.addText([
    { text:"Desenfoque gaussiano sutil (lente/movimiento).", options:{ bullet:{code:"2022"}, color:"D8E5DC", breakLine:true } },
    { text:"Ruido speckle + gaussiano (sensor).", options:{ bullet:{code:"2022"}, color:"D8E5DC", breakLine:true } },
    { text:"Borra la discontinuidad matemática en los bordes sintetizados.", options:{ bullet:{code:"2022"}, color:"D8E5DC" } },
  ], { x:8.55, y:2.7, w:4.0, h:1.5, fontSize:12.5, fontFace:FT, paraSpaceAfter:5, valign:"top" });
  s.addShape(p.shapes.LINE, { x:8.55, y:4.35, w:3.9, h:0, line:{ color:C.lineD, width:1 } });
  s.addText("Dataset de demostración", { x:8.5, y:4.5, w:4, h:0.35, fontSize:13, bold:true, color:"FFFFFF", fontFace:FT, margin:0 });
  const kv = (y,k,v) => {
    s.addText(k, { x:8.55, y, w:2.6, h:0.35, fontSize:12.5, color:"AFC6B7", fontFace:FT, margin:0 });
    s.addText(v, { x:11.1, y, w:1.5, h:0.35, fontSize:12.5, bold:true, color:C.soyL, align:"right", fontFace:FT, margin:0 });
  };
  kv(4.9, "Densidad por imagen", "20–150");
  kv(5.28, "Instancias (6 imgs)", "559");
  kv(5.66, "Formato de salida", "YOLO");
  footer(s);
})();

// ---------------------------------------------------------------- 9 · ENTRENAMIENTO
(() => {
  const s = p.addSlide(); s.background = { color:C.light };
  header(s, "Entrenamiento", "Detector y la métrica que importa");
  s.addNotes("Uso YOLOv8 por dos razones: el dataset ya sale en formato YOLO y es liviano para servir la demo. Aclarar que el pipeline es agnostico al modelo. Punto importante: no me quedo con el mAP, mido el error de CONTEO en granos (MAE, RMSE, MAPE), que es lo que le importa al negocio. ~1 minuto y medio.");
  s.addText("Modelo: YOLOv8 (Ultralytics)", { x:0.5, y:1.95, w:6.5, h:0.4, fontSize:17, bold:true, color:C.green, fontFace:FT, margin:0 });
  s.addText([
    { text:"Detección de una clase (poroto), entrada 1024×1024.", options:{ bullet:true, breakLine:true } },
    { text:"El dataset ya trae augmentation por grano; en el entrenador sólo sumamos mosaico/flip moderados.", options:{ bullet:true, breakLine:true } },
    { text:"Elegido por: labels nativas YOLO + liviano para servir la demo. El pipeline es agnóstico al modelo.", options:{ bullet:true } },
  ], { x:0.6, y:2.4, w:6.4, h:2.0, fontSize:13.5, color:C.muted, fontFace:FT, paraSpaceAfter:7, valign:"top" });
  s.addText("Evaluamos el conteo, no sólo el mAP", { x:0.5, y:4.5, w:6.5, h:0.4, fontSize:16, bold:true, color:C.text, fontFace:FT, margin:0 });
  s.addText("El objetivo del negocio es cuántos granos hay; reportamos error de conteo en granos.",
    { x:0.6, y:4.92, w:6.4, h:0.7, fontSize:13, color:C.muted, fontFace:FT, lineSpacingMultiple:1.1, valign:"top" });
  // tabla métricas
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x:7.5, y:2.1, w:5.3, h:3.6, rectRadius:0.12,
    fill:{ color:C.card }, line:{ color:C.lineL, width:1 }, shadow:sh() });
  s.addText("Métricas de conteo", { x:7.8, y:2.35, w:4.7, h:0.4, fontSize:14, bold:true, color:C.text, fontFace:FT, margin:0 });
  const rows = [
    ["MAE", "error medio absoluto, en granos"],
    ["RMSE", "penaliza errores grandes"],
    ["MAPE", "error porcentual relativo a N"],
    ["mAP@50", "calidad de localización (auxiliar)"],
  ];
  let y=2.95;
  rows.forEach(r=>{
    s.addText(r[0], { x:7.8, y, w:1.5, h:0.45, fontSize:15, bold:true, color:C.soy, fontFace:FT, margin:0 });
    s.addText(r[1], { x:9.4, y:y+0.03, w:3.2, h:0.45, fontSize:12, color:C.muted, fontFace:FT, valign:"top", margin:0 });
    y+=0.66;
  });
  footer(s);
})();

// ---------------------------------------------------------------- 10 · ARQUITECTURA INFERENCIA
(() => {
  const s = p.addSlide(); s.background = { color:C.light };
  header(s, "Inferencia", "Arquitectura del servicio");
  s.addNotes("Recorrer el diagrama: el cliente manda la imagen por POST, FastAPI se la pasa al codigo Python que corre el modelo y cuenta, y devuelve success y cantidad. En paralelo guarda en el repositorio la IMAGEN con contornos y el archivo de metadatos. Las tres tarjetas: success es la bandera de confianza, IMAGEN es para verificacion visual humana, metadatos para trazabilidad. ~1 minuto y medio.");
  const box = (x,y,w,h,label,fill,tc) => {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius:0.08,
      fill:{ color:fill }, line:{ color:C.lineL, width:1 }, shadow:sh() });
    s.addText(label, { x, y, w, h, fontSize:12.5, bold:true, color:tc, align:"center",
      valign:"middle", fontFace:FT, margin:2 });
  };
  const arrow = (x,y,w,txt) => {
    s.addShape(p.shapes.LINE, { x, y, w, h:0, line:{ color:C.soy, width:1.75, endArrowType:"triangle" } });
    if (txt) s.addText(txt, { x:x-0.1, y:y-0.42, w:w+0.6, h:0.35, fontSize:9.5, color:C.muted, align:"center", fontFace:FT, margin:0 });
  };
  const Y=2.55, bh=0.95;
  box(0.5, Y, 2.0, bh, "Cliente\nHTTP", C.card, C.text);
  box(3.4, Y, 2.2, bh, "FastAPI\n(HTTP server)", C.dark, "FFFFFF");
  box(6.5, Y, 2.2, bh, "Código\nPython", C.card, C.text);
  box(9.6, Y, 2.0, bh, "Modelo\n(YOLO / clásico)", C.dark, "FFFFFF");
  arrow(2.55, Y+0.4, 0.8, "POST imagen");
  arrow(5.65, Y+0.4, 0.8, "imagen");
  arrow(8.75, Y+0.4, 0.8, "imagen");
  // respuesta de vuelta
  s.addText("← {success, cantidad}", { x:3.3, y:Y+bh+0.15, w:5.5, h:0.35, fontSize:11, italic:true, color:C.green, fontFace:FT, margin:0 });
  // repositorio
  box(3.4, Y+1.85, 2.2, 0.9, "Repositorio", C.card, C.text);
  s.addShape(p.shapes.LINE, { x:4.5, y:Y+bh, w:0, h:0.85, line:{ color:C.soy, width:1.75, endArrowType:"triangle" } });
  s.addText("IMAGEN* + metadatos", { x:5.7, y:Y+1.35, w:3, h:0.3, fontSize:9.5, color:C.muted, fontFace:FT, margin:0 });
  // notas inferiores
  const note = (x,t1,t2) => {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y:5.55, w:3.95, h:1.35, rectRadius:0.1,
      fill:{ color:C.card }, line:{ color:C.lineL, width:1 }, shadow:sh() });
    s.addText(t1, { x:x+0.25, y:5.7, w:3.5, h:0.35, fontSize:13, bold:true, color:C.green, fontFace:FT, margin:0 });
    s.addText(t2, { x:x+0.25, y:6.05, w:3.5, h:0.8, fontSize:11.5, color:C.muted, fontFace:FT, lineSpacingMultiple:1.05, valign:"top", margin:0 });
  };
  note(0.5, "success", "Bandera de confianza: si el promedio cae bajo el umbral, avisa para revisar a mano.");
  note(4.67, "IMAGEN*", "La imagen con contornos por grano e índice numérico, para verificación visual.");
  note(8.85, "Metadatos", "id, timestamp, versión de modelo, N de porotos y confianza promedio.");
  footer(s);
})();

// ---------------------------------------------------------------- 11 · DEMO
(() => {
  const s = p.addSlide(); s.background = { color:C.dark };
  seed(s, 0.5, 0.52);
  s.addNotes("Demo en VIDEO grabado de 2 minutos (lo pide la cátedra): se reproduce acá y uno del grupo lo narra en vivo. Mostrar: subir una imagen del val real, el conteo, la lampara de success y el JSON de metadatos. Para insertar el video en PowerPoint: Insertar > Video > Este dispositivo, sobre el recuadro. ~2 minutos.");
  s.addText("DEMO · VIDEO (2 MIN)", { x:0.95, y:0.45, w:9, h:0.3, fontSize:11.5, color:C.soyL, charSpacing:3, bold:true, fontFace:FT, margin:0 });
  s.addText("Subir muestra → contar → inspeccionar", { x:0.5, y:0.78, w:12.3, h:0.7, fontSize:30, bold:true, color:"FFFFFF", fontFace:FT, margin:0 });
  const iw=7.0, ih=iw/1.266;
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x:0.5, y:1.9, w:iw+0.2, h:ih+0.2, rectRadius:0.1,
    fill:{ color:C.dark2 }, line:{ color:C.lineD, width:1 }, shadow:sh({color:"000000",opacity:0.3}) });
  s.addImage({ path:A+"demo_ui.png", x:0.6, y:2.0, w:iw, h:ih });
  // badge de video sobre el visor
  s.addShape(p.shapes.OVAL, { x:0.6+iw/2-0.45, y:2.0+ih/2-0.45, w:0.9, h:0.9, fill:{color:"000000",transparency:25}, line:{color:"FFFFFF",width:1.5} });
  s.addText("▶", { x:0.6+iw/2-0.42, y:2.0+ih/2-0.45, w:0.9, h:0.9, fontSize:30, color:"FFFFFF", align:"center", valign:"middle", fontFace:FT, margin:0 });
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x:0.7, y:2.1, w:2.5, h:0.42, rectRadius:0.08, fill:{color:C.soy}, line:{type:"none"} });
  s.addText("▶  VIDEO · 2 MIN", { x:0.7, y:2.1, w:2.5, h:0.42, fontSize:11, bold:true, color:"241A08", align:"center", valign:"middle", fontFace:FT, margin:0 });
  // panel derecha
  const px=8.5;
  s.addText("Lo que ves en pantalla", { x:px, y:2.0, w:4.3, h:0.4, fontSize:15, bold:true, color:C.soyL, fontFace:FT, margin:0 });
  s.addText([
    { text:"Visor con la IMAGEN* devuelta por el repositorio.", options:{ bullet:{code:"2022"}, color:"D8E5DC", breakLine:true } },
    { text:"Lámpara de estado para success.", options:{ bullet:{code:"2022"}, color:"D8E5DC", breakLine:true } },
    { text:"Conteo y confianza promedio.", options:{ bullet:{code:"2022"}, color:"D8E5DC", breakLine:true } },
    { text:"JSON de metadatos descargable.", options:{ bullet:{code:"2022"}, color:"D8E5DC" } },
  ], { x:px, y:2.5, w:4.3, h:2.2, fontSize:13, fontFace:FT, paraSpaceAfter:7, valign:"top" });
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x:px, y:4.75, w:4.3, h:1.7, rectRadius:0.1,
    fill:{ color:C.dark2 }, line:{ color:C.lineD, width:1 } });
  s.addText("Video grabado, narrado en vivo", { x:px+0.25, y:4.92, w:3.8, h:0.4, fontSize:13.5, bold:true, color:"FFFFFF", fontFace:FT, margin:0 });
  s.addText("Se graba con la demo local (FastAPI) y se reproduce acá durante la defensa. Corre con el YOLOv8n entrenado.",
    { x:px+0.25, y:5.32, w:3.8, h:1.0, fontSize:12, color:"AFC6B7", fontFace:FT, lineSpacingMultiple:1.1, valign:"top", margin:0 });
  footer(s, true);
})();

// ---------------------------------------------------------------- 12 · RESULTADOS / COMPARATIVA
(() => {
  const s = p.addSlide(); s.background = { color:C.light };
  header(s, "Resultados", "Baseline real y comparativa de enfoques");
  s.addNotes("Numero honesto: el baseline clasico da MAE 6.5 y 6 por ciento de MAPE sobre densidades de 23 a 143. Cuenta bien con granos separados y subcuenta cuando se pegan (señalar en la imagen los dos granos fusionados en uno). Eso es justo lo que un detector entrenado deberia mejorar. La tabla es el marco de comparacion de enfoques, alineado con la literatura. ~1 minuto y medio.");
  // imagen imagen_estrella
  const im=3.5;
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x:0.5, y:2.05, w:im+0.2, h:im+0.2, rectRadius:0.1, fill:{color:C.card}, line:{color:C.lineL,width:1}, shadow:sh() });
  s.addImage({ path:A+"imagen_estrella.jpg", x:0.6, y:2.15, w:im, h:im });
  s.addText("Baseline clásico: 22 detectados vs 23 reales", { x:0.5, y:2.05+im+0.22, w:im+0.2, h:0.4, fontSize:11, italic:true, color:C.muted, align:"center", fontFace:FT, margin:0 });
  // métricas baseline
  const stat=(x,n,l)=>{
    s.addText(n,{x,y:2.15,w:2.4,h:0.8,fontSize:34,bold:true,color:C.soy,fontFace:FT,margin:0});
    s.addText(l,{x,y:2.98,w:2.4,h:0.5,fontSize:11.5,color:C.muted,fontFace:FT,margin:0});
  };
  stat(4.55,"6.5","MAE · baseline clásico");
  stat(6.95,"0.995","mAP@.5 · YOLOv8n");
  s.addText("El baseline clásico (watershed) da MAE 6.5: cuenta bien en baja densidad y subcuenta cuando los granos se pegan. El YOLOv8 entrenado sobre el dataset sintético cuenta casi perfecto en validación in-distribution (MAE≈0): valida método y pipeline. La validación con fotos reales (brecha sim-to-real) queda como próximo paso.",
    { x:4.55, y:3.65, w:4.8, h:1.7, fontSize:11.5, color:C.muted, fontFace:FT, lineSpacingMultiple:1.1, valign:"top" });
  // tabla cuantitativa de resultados (validación in-distribution)
  s.addText("Resultados en validación (100 imgs · 1685 instancias)", { x:9.5, y:2.05, w:3.4, h:0.6, fontSize:12, bold:true, color:C.text, fontFace:FT, lineSpacingMultiple:1.0, margin:0, valign:"top" });
  const hc = (t)=>({text:t,options:{bold:true,color:"FFFFFF",fill:{color:C.dark},fontSize:9.5,align:"center"}});
  const tbl = [
    [hc("Modelo"),hc("mAP@.5"),hc("MAE"),hc("ms/img")],
    ["Watershed","—","6.5","—"],
    ["YOLOv8n","0.995","0.00","13"],
    ["YOLOv8s","0.995","0.00","14"],
  ];
  s.addTable(tbl, { x:9.5, y:2.75, w:3.4, colW:[1.25,0.85,0.65,0.65],
    border:{pt:0.5,color:C.lineL}, color:C.text, fontFace:FT, fontSize:10,
    rowH:0.46, valign:"middle", align:"center", fill:{color:C.card} });
  s.addText("mAP@.5:.95 — n 0.979 · s 0.982. Tamaño: n 3.0 M / 6 MB vs s 11.1 M / 22 MB → se despliega el nano. Saturado porque la validación es in-distribution.",
    { x:9.5, y:5.05, w:3.4, h:1.3, fontSize:10, italic:true, color:C.muted, fontFace:FT, lineSpacingMultiple:1.08, valign:"top" });
  footer(s);
})();

// ---------------------------------------------------------------- 13 · LIMITACIONES
(() => {
  const s = p.addSlide(); s.background = { color:C.light };
  header(s, "Honestidad", "Limitaciones y próximos pasos");
  s.addNotes("Ser honesta: la brecha sim-to-real esta sin medir, los granos de la demo son procedurales y la oclusion severa sigue siendo dificil. Proximos pasos concretos: conseguir un set real chico para validar, probar segmentacion y mapas de densidad, fine-tuning mezclando sintetico y real, y monitorear la tasa de success false en produccion. ~1 minuto.");
  const cols = [
    ["Limitaciones", C.soy, [
      "Brecha sim-to-real: falta validar contra fotos reales etiquetadas.",
      "Granos procedurales en la demo; el realismo final depende de buenos recortes.",
      "Oclusión severa y granos partidos siguen siendo difíciles.",
    ]],
    ["Próximos pasos", C.green, [
      "Conseguir/etiquetar un set real chico sólo para validación.",
      "Probar YOLOv8-seg y mapas de densidad para alta densidad.",
      "Mezclar sintético + real (fine-tuning) y medir la brecha.",
      "Monitoreo en producción: distribución de confianza y tasa de success=false.",
    ]],
  ];
  cols.forEach((c,i) => {
    const x = 0.5 + i*6.3;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y:2.05, w:5.9, h:4.2, rectRadius:0.12,
      fill:{ color:C.card }, line:{ color:C.lineL, width:1 }, shadow:sh() });
    seed(s, x+0.35, y_=2.32, 0.34, c[1]);
    s.addText(c[0], { x:x+0.9, y:2.25, w:4.7, h:0.5, fontSize:18, bold:true, color:C.text, fontFace:FT, margin:0 });
    s.addText(c[2].map((t,j)=>({ text:t, options:{ bullet:true, breakLine:true, paraSpaceAfter:9 } })),
      { x:x+0.5, y:3.0, w:5.0, h:3.0, fontSize:13.5, color:C.muted, fontFace:FT, lineSpacingMultiple:1.1, valign:"top" });
  });
  footer(s);
})();

// ---------------------------------------------------------------- 14 · CIERRE
(() => {
  const s = p.addSlide(); s.background = { color:C.dark };
  s.addImage({ path:A+"bg_dense_clean.jpg", x:8.7, y:0, w:H, h:H, sizing:{type:"cover",w:H,h:H}, transparency:30 });
  s.addShape(p.shapes.RECTANGLE, { x:8.7, y:0, w:W-8.7, h:H, fill:{ color:C.dark, transparency:45 }, line:{type:"none"} });
  seed(s, 0.85, 1.7, 0.5);
  s.addNotes("Cerrar con la idea fuerza: los datos sinteticos fueron la llave del problema. Recap de los tres entregables: pipeline de 4 fases, deteccion con metrica de conteo y servicio con demo. Agradecer y abrir a preguntas. ~30 segundos.");
  s.addText("CIERRE", { x:1.5, y:1.72, w:5, h:0.35, fontSize:13, color:C.soyL, charSpacing:3, bold:true, fontFace:FT, margin:0 });
  s.addText("Datos sintéticos como\nllave del problema", { x:0.85, y:2.25, w:8, h:1.6, fontSize:38, bold:true, color:"FFFFFF", fontFace:FT, lineSpacingMultiple:1.0, margin:0 });
  s.addText([
    { text:"Pipeline sintético de 4 fases con ground truth automático.", options:{ bullet:{code:"2022"}, color:"D8E5DC", breakLine:true } },
    { text:"Detección + métrica de conteo orientada al negocio.", options:{ bullet:{code:"2022"}, color:"D8E5DC", breakLine:true } },
    { text:"Servicio FastAPI + demo de inspección, reproducible.", options:{ bullet:{code:"2022"}, color:"D8E5DC" } },
  ], { x:0.9, y:4.1, w:7.3, h:1.5, fontSize:14.5, fontFace:FT, paraSpaceAfter:8, valign:"top" });
  s.addText("¿Preguntas?", { x:0.9, y:5.85, w:6, h:0.6, fontSize:22, bold:true, color:C.soyL, fontFace:FT, margin:0 });
  footer(s, true);
})();

// ============================ APÉNDICE ====================================
// ----------------------------------------------- 15 · DIVISOR APÉNDICE
(() => {
  const s = p.addSlide(); s.background = { color:C.dark };
  s.addImage({ path:A+"bg_sparse_clean.jpg", x:8.7, y:0, w:H, h:H, sizing:{type:"cover",w:H,h:H}, transparency:24 });
  s.addShape(p.shapes.RECTANGLE, { x:8.7, y:0, w:W-8.7, h:H, fill:{color:C.dark,transparency:40}, line:{type:"none"} });
  seed(s, 0.85, 1.7, 0.5);
  s.addText("APÉNDICE", { x:1.5, y:1.72, w:5, h:0.35, fontSize:13, color:C.soyL, charSpacing:3, bold:true, fontFace:FT, margin:0 });
  s.addText("Fundamentos teóricos\ny pipelines", { x:0.85, y:2.25, w:8, h:1.6, fontSize:38, bold:true, color:"FFFFFF", fontFace:FT, lineSpacingMultiple:1.0, margin:0 });
  s.addText("Material de respaldo para preguntas: la teoría de visión detrás de cada etapa.",
    { x:0.9, y:4.0, w:7.2, h:0.6, fontSize:15, color:"CFE0D4", fontFace:FT, margin:0 });
  footer(s, true);
})();

// ----------------------------------------------- 16 · PIPELINE DATOS SINTÉTICOS
(() => {
  const s = p.addSlide(); s.background = { color:C.light };
  header(s, "Pipeline · datos sintéticos", "De la foto real al dataset etiquetado");
  const box = (x,y,w,h,label,fill,tc,fs) => {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius:0.07,
      fill:{color:fill}, line:{color:C.lineL,width:1}, shadow:sh() });
    s.addText(label, { x, y, w, h, fontSize:fs||11, bold:true, color:tc, align:"center", valign:"middle", fontFace:FT, margin:2 });
  };
  const arr = (x,y,w) => s.addShape(p.shapes.LINE, { x, y, w, h:0, line:{color:C.soy,width:1.75,endArrowType:"triangle"} });

  // ETAPA 1
  s.addText("ETAPA 1 · extracción del grano", { x:0.5, y:1.95, w:8, h:0.35, fontSize:14, bold:true, color:C.green, fontFace:FT, margin:0 });
  const y1=2.45, bh=0.85;
  box(0.5,y1,2.55,bh,"Imagen real\n(porotos)",C.card,C.text);
  box(3.75,y1,2.7,bh,"Otsu + canal alfa\n+ recorte bbox",C.dark,"FFFFFF");
  box(7.15,y1,2.7,bh,"Banco de granos\nRGBA",C.card,C.text);
  arr(3.1,y1+bh/2,0.6); arr(6.5,y1+bh/2,0.6);

  // ETAPA 2
  s.addText("ETAPA 2 · composición de la escena (×N granos)", { x:0.5, y:3.75, w:9, h:0.35, fontSize:14, bold:true, color:C.green, fontFace:FT, margin:0 });
  const y2=4.25;
  const steps = [
    ["Elegir grano\ndel banco", C.card, C.text],
    ["Aumentar\n(afín + HSV)", C.card, C.text],
    ["Ubicar sin\ncolisión (IoU)", C.dark, "FFFFFF"],
    ["Alpha\nblending", C.card, C.text],
    ["Escribir\netiqueta YOLO", C.dark, "FFFFFF"],
  ];
  const bw=2.18, gap=0.22, x0=0.5;
  steps.forEach((st,i)=>{
    const x=x0+i*(bw+gap);
    box(x,y2,bw,bh,st[0],st[1],st[2],10);
    if(i<steps.length-1) arr(x+bw,y2+bh/2,gap);
  });
  s.addText("↻ repetir N veces", { x:x0, y:y2+bh+0.1, w:4, h:0.3, fontSize:10.5, italic:true, color:C.soy, fontFace:FT, margin:0 });
  // salida
  box(0.5,y2+1.35,4.6,0.75,"Postproceso global (blur + ruido de sensor)",C.card,C.text,11);
  box(5.4,y2+1.35,4.45,0.75,"Imagen sintética + labels (ground truth exacto)",C.dark,"FFFFFF",11);
  arr(5.1,y2+1.35+0.375,0.3);
  footer(s);
})();

// ----------------------------------------------- 17 · FUNDAMENTOS I (síntesis)
(() => {
  const s = p.addSlide(); s.background = { color:C.light };
  header(s, "Fundamentos I", "Teoría de la síntesis de imagen");
  const card = (x,y,t,formula,desc) => {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w:6.0, h:1.78, rectRadius:0.1,
      fill:{color:C.card}, line:{color:C.lineL,width:1}, shadow:sh() });
    s.addText(t, { x:x+0.3, y:y+0.2, w:5.4, h:0.4, fontSize:15, bold:true, color:C.text, fontFace:FT, margin:0 });
    s.addText(formula, { x:x+0.3, y:y+0.62, w:5.4, h:0.45, fontSize:14, bold:true, color:C.green, fontFace:"Consolas", margin:0 });
    s.addText(desc, { x:x+0.3, y:y+1.08, w:5.4, h:0.6, fontSize:11, color:C.muted, fontFace:FT, lineSpacingMultiple:1.05, valign:"top", margin:0 });
  };
  card(0.5, 2.0, "Umbralizado de Otsu", "t* = argmax  σ²_b(t)",
       "Elige solo el umbral que maximiza la varianza entre objeto y fondo. No paramétrico.");
  card(6.8, 2.0, "Máscara alfa + recorte", "RGBA · α=255 grano / 0 fondo",
       "La máscara va al canal alfa; se recorta a la bbox. Grano reutilizable sin fondo.");
  card(0.5, 4.0, "Alpha compositing", "I = α·F + (1−α)·B",
       "Pega el grano con bordes suaves (sin aliasing). Ecuación 'over' de Porter–Duff.");
  card(6.8, 4.0, "Control de oclusión (IoU)", "IoU = |A∩B| / |A∪B|",
       "Solapamiento contra la ocupación global; si supera el umbral, se reubica.");
  s.addText("Domain randomization: aleatorizar lo irrelevante (pose, color, ruido) fuerza al modelo a aprender lo invariante — la forma del grano.",
    { x:0.5, y:6.0, w:12.3, h:0.5, fontSize:12.5, italic:true, color:C.soy, fontFace:FT, align:"center" });
  footer(s);
})();

// ----------------------------------------------- 18 · FUNDAMENTOS II (aprendizaje)
(() => {
  const s = p.addSlide(); s.background = { color:C.light };
  header(s, "Fundamentos II", "Teoría del aprendizaje y la evaluación");
  // esquema forward/backprop
  s.addText("Esquema de entrenamiento", { x:0.5, y:1.95, w:6, h:0.35, fontSize:14, bold:true, color:C.green, fontFace:FT, margin:0 });
  const box = (x,y,w,label) => {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w, h:0.8, rectRadius:0.07, fill:{color:C.card}, line:{color:C.lineL,width:1}, shadow:sh() });
    s.addText(label, { x, y, w, h:0.8, fontSize:11, bold:true, color:C.text, align:"center", valign:"middle", fontFace:FT, margin:2 });
  };
  const arr = (x,y,w) => s.addShape(p.shapes.LINE, { x, y, w, h:0, line:{color:C.soy,width:1.75,endArrowType:"triangle"} });
  const y=2.45;
  box(0.5,y,1.9,"Forward\n(predicción)");
  box(2.7,y,2.0,"Pérdida L\nvs ground truth");
  box(5.0,y,2.0,"Backprop\n∂L/∂w");
  box(7.3,y,1.9,"Actualizar\npesos");
  arr(2.4,y+0.4,0.3); arr(4.7,y+0.4,0.3); arr(7.0,y+0.4,0.3);
  s.addShape(p.shapes.LINE, { x:8.25, y:y+0.8, w:0, h:0.45, line:{color:C.soy,width:1.5} });
  s.addShape(p.shapes.LINE, { x:1.45, y:y+1.25, w:6.8, h:0, line:{color:C.soy,width:1.5} });
  s.addShape(p.shapes.LINE, { x:1.45, y:y+0.8, w:0, h:0.45, line:{color:C.soy,width:1.5,endArrowType:"triangle"} });
  s.addText("se repite por épocas hasta converger", { x:2.4, y:y+1.3, w:5, h:0.3, fontSize:10, italic:true, color:C.muted, fontFace:FT, margin:0 });

  // tarjetas teoría
  const card = (x,y2,t,d) => {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y:y2, w:6.0, h:1.35, rectRadius:0.1, fill:{color:C.card}, line:{color:C.lineL,width:1}, shadow:sh() });
    s.addText(t, { x:x+0.3, y:y2+0.18, w:5.4, h:0.4, fontSize:14, bold:true, color:C.text, fontFace:FT, margin:0 });
    s.addText(d, { x:x+0.3, y:y2+0.58, w:5.4, h:0.7, fontSize:11, color:C.muted, fontFace:FT, lineSpacingMultiple:1.05, valign:"top", margin:0 });
  };
  card(0.5, 4.5, "Detector one-stage (YOLO)", "Predice cajas + clase en una sola pasada (vs. dos etapas de Faster R-CNN). El conteo = nº de detecciones sobre el umbral.");
  card(6.8, 4.5, "mAP vs MAE", "mAP@50 mide localización; MAE/MAPE miden el conteo — la métrica del negocio. In-distribution el conteo es casi perfecto.");
  card(0.5, 6.0, "Brecha sim-to-real", "MAE≈0 valida el método, no la generalización. Validar con fotos reales es el límite honesto del trabajo.");
  card(6.8, 6.0, "Pipeline agnóstico al modelo", "Las etiquetas YOLO no atan: se podría usar Faster R-CNN, segmentación o mapas de densidad.");
  footer(s);
})();

p.writeFile({ fileName: "/home/claude/poroto_cv/docs/Presentacion_Conteo_Porotos.pptx" })
  .then(f => console.log("OK:", f));
