# Nano Banana Studio — PoC
> Este archivo es el inicializador del proyecto. Léelo completo antes de escribir una sola línea de código.

---

## Contexto del proyecto

PoC standalone que demuestra las 3 capacidades principales de **Nano Banana (Gemini 2.5 Flash Image)** en un flujo secuencial con el mismo tema como hilo conductor.

No es parte de la serie ADK ni LangGraph — es un proyecto independiente enfocado en generación y edición de imágenes con IA.

---

## Objetivo del PoC

Dado un tema en texto libre, el sistema genera una imagen, la edita y la fusiona con una imagen de referencia. Las 3 capacidades del modelo en un solo flujo, con output visual concreto.

---

## ¿Qué hace el sistema?

```
INPUT:
  --tema      : concepto en texto libre (ej: "ciudad cyberpunk al amanecer")
  --edit      : instrucción de edición (ej: "agrega lluvia y neón reflejado")
  --referencia: path a imagen local para el blend (ej: foto.jpg)

FLUJO:
Step 1 — Generate  → genera imagen desde --tema (text-to-image)
                     guarda: outputs/01_generated.png
Step 2 — Edit      → edita la imagen generada con --edit
                     guarda: outputs/02_edited.png
Step 3 — Blend     → fusiona 02_edited.png con --referencia
                     guarda: outputs/03_blended.png
Step 4 — Report    → genera reporte MD con prompts, tiempos y paths

OUTPUT:
  outputs/01_generated.png
  outputs/02_edited.png
  outputs/03_blended.png
  outputs/report_YYYY-MM-DD.md
```

---

## Arquitectura

```
main.py
├── step_generate.py   → text-to-image con Nano Banana
├── step_edit.py       → edición de imagen con prompt
├── step_blend.py      → fusión de 2 imágenes
└── report.py          → genera MD con resumen del proceso
```

Sin agentes, sin grafos — flujo directo y simple. La complejidad está en el uso correcto de la API de imagen.

---

## Estructura de carpetas

```
nano-banana-studio/
├── main.py              # Entry point — orquesta los 3 steps
├── steps/
│   ├── __init__.py
│   ├── generate.py      # Step 1: text-to-image
│   ├── edit.py          # Step 2: edición con prompt
│   └── blend.py         # Step 3: fusión de imágenes
├── report.py            # Genera reporte MD final
├── outputs/             # Imágenes generadas + reporte
├── assets/              # Imágenes de referencia del usuario
├── .env.example
├── requirements.txt
└── README.md
```

---

## Cómo se ejecuta

```bash
# Instalar dependencias
pip install google-generativeai Pillow python-dotenv

# Configurar variables de entorno
cp .env.example .env

# Ejecutar flujo completo
python main.py \
  --tema "ciudad cyberpunk al amanecer" \
  --edit "agrega lluvia intensa y neón reflejado en el suelo" \
  --referencia assets/mi_foto.jpg

# Ejecutar solo steps específicos
python main.py --tema "bosque encantado" --solo generate
python main.py --tema "bosque encantado" --solo edit --edit "agrega niebla"
```

---

## Variables de entorno

```env
GEMINI_API_KEY=your_gemini_api_key
```

> Nano Banana usa el mismo API key de Gemini.
> Obtener en: https://aistudio.google.com/apikey

---

## Implementación de cada step

### Step 1 — Generate (text-to-image)
```python
import google.generativeai as genai
from PIL import Image
import io

def generate_image(tema: str) -> Image:
    client = genai.ImageGenerationModel("gemini-2.5-flash-image")
    response = client.generate_images(prompt=tema)
    image_data = response.generated_images[0].image.image_bytes
    return Image.open(io.BytesIO(image_data))
```

### Step 2 — Edit (image + prompt)
```python
def edit_image(image: Image, instruccion: str) -> Image:
    # Envía imagen + prompt de edición al modelo
    # El modelo retorna la imagen modificada
```

### Step 3 — Blend (multi-image fusion)
```python
def blend_images(image_a: Image, image_b: Image) -> Image:
    # Envía 2 imágenes al modelo
    # El modelo las fusiona en una sola imagen coherente
```

---

## Formato del reporte esperado

```markdown
# Nano Banana Studio — Reporte
**Fecha:** YYYY-MM-DD HH:MM

## Step 1 — Generate
**Prompt:** "ciudad cyberpunk al amanecer"
**Tiempo:** 3.2s
**Output:** outputs/01_generated.png

## Step 2 — Edit
**Instrucción:** "agrega lluvia intensa y neón reflejado en el suelo"
**Tiempo:** 2.8s
**Output:** outputs/02_edited.png

## Step 3 — Blend
**Referencia:** assets/mi_foto.jpg
**Tiempo:** 4.1s
**Output:** outputs/03_blended.png

## Resumen
- Total: 10.1s
- 3 imágenes generadas
- Capacidades demostradas: text-to-image ✅ | edición ✅ | blend ✅
```

---

## Conceptos Nano Banana que se practican

| Capacidad | Step | Descripción |
|---|---|---|
| **Text-to-image** | Step 1 | Genera imagen desde prompt de texto |
| **Image editing** | Step 2 | Modifica imagen existente con lenguaje natural |
| **Multi-image blend** | Step 3 | Fusiona 2 imágenes en una coherente |
| **World knowledge** | Todos | El modelo usa contexto real para generar |
| **SynthID** | Output | Watermark invisible en todas las imágenes |

---

## Restricciones de scope

- ❌ No UI — solo CLI
- ❌ No encadenar más de 3 steps
- ❌ No video ni audio — solo imágenes estáticas
- ✅ Output visual concreto en cada step
- ✅ Reporte MD con tiempos y prompts usados
- ✅ Manejo de errores de API con mensajes descriptivos

---

## Definition of Done

- [ ] Step 1 genera imagen desde texto correctamente
- [ ] Step 2 edita la imagen con el prompt dado
- [ ] Step 3 fusiona 2 imágenes en una coherente
- [ ] Las 3 imágenes se guardan en `/outputs`
- [ ] Reporte MD generado con tiempos y paths
- [ ] Funciona con `python main.py --tema X --edit Y --referencia Z`
- [ ] Manejo de errores si la API falla en algún step
