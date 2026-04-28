import io
import time

from google.genai import types, errors
from PIL import Image

from client import get_client, MODEL


def generate_image(tema: str) -> tuple[Image.Image, float]:
    start = time.time()
    try:
        response = get_client().models.generate_content(
            model=MODEL,
            contents=tema,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                safety_settings=[],
            ),
        )
    except errors.APIError as e:
        raise RuntimeError(f"[Step 1] Error de API {e.code}: {e.message}") from e

    image_bytes = _extract_image_bytes(response, "generación")
    return Image.open(io.BytesIO(image_bytes)), round(time.time() - start, 2)


def _extract_image_bytes(response, step: str) -> bytes:
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            return part.inline_data.data
    raise ValueError(f"El modelo no devolvió una imagen en la respuesta de {step}.")
