import io
import time

from google.genai import types, errors
from PIL import Image

from client import get_client, MODEL


def edit_image(image: Image.Image, instruccion: str) -> tuple[Image.Image, float]:
    start = time.time()
    try:
        response = get_client().models.generate_content(
            model=MODEL,
            contents=[
                instruccion,
                types.Part.from_bytes(data=_to_bytes(image), mime_type="image/png"),
            ],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                safety_settings=[],
            ),
        )
    except errors.APIError as e:
        raise RuntimeError(f"[Step 2] Error de API {e.code}: {e.message}") from e

    image_bytes = _extract_image_bytes(response)
    return Image.open(io.BytesIO(image_bytes)), round(time.time() - start, 2)


def _to_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def _extract_image_bytes(response) -> bytes:
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            return part.inline_data.data
    raise ValueError("El modelo no devolvió una imagen en la respuesta de edición.")
