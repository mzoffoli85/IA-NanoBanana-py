import io
import time
import google.generativeai as genai
from PIL import Image


MODEL = "gemini-2.5-flash"
BLEND_PROMPT = (
    "Fusiona estas dos imágenes en una sola imagen coherente y visualmente armoniosa. "
    "Combina los elementos visuales de ambas de manera natural."
)


def blend_images(
    image_a: Image.Image, image_b: Image.Image
) -> tuple[Image.Image, float]:
    start = time.time()

    bytes_a = _image_to_bytes(image_a)
    bytes_b = _image_to_bytes(image_b)

    model = genai.GenerativeModel(MODEL)
    response = model.generate_content(
        [
            BLEND_PROMPT,
            {"mime_type": "image/png", "data": bytes_a},
            {"mime_type": "image/png", "data": bytes_b},
        ],
        generation_config=genai.GenerationConfig(
            response_modalities=["IMAGE"]
        ),
    )

    blended_bytes = _extract_image_bytes(response)
    elapsed = round(time.time() - start, 2)
    return Image.open(io.BytesIO(blended_bytes)), elapsed


def _image_to_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def _extract_image_bytes(response) -> bytes:
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            return part.inline_data.data
    raise ValueError("El modelo no devolvió una imagen en la respuesta de blend.")
