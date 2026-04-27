import io
import time
import google.generativeai as genai
from PIL import Image


MODEL = "gemini-2.5-flash-preview-05-20"


def generate_image(tema: str) -> tuple[Image.Image, float]:
    start = time.time()

    model = genai.GenerativeModel(MODEL)
    response = model.generate_content(
        tema,
        generation_config=genai.GenerationConfig(
            response_modalities=["IMAGE"]
        ),
    )

    image_bytes = _extract_image_bytes(response)
    elapsed = round(time.time() - start, 2)
    return Image.open(io.BytesIO(image_bytes)), elapsed


def _extract_image_bytes(response) -> bytes:
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            return part.inline_data.data
    raise ValueError("El modelo no devolvió una imagen en la respuesta de generación.")
