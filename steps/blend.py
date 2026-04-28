import io
import time

import httpx
from google.genai import types, errors
from PIL import Image
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from client import get_blend_client, MODEL, TIMEOUT_BLEND as TIMEOUT

BLEND_PROMPT = (
    "Fusiona estas dos imágenes en una sola imagen coherente y visualmente armoniosa. "
    "Combina los elementos visuales de ambas de manera natural."
)


def _on_retry(retry_state):
    print(f"  [Step 3] Timeout en intento {retry_state.attempt_number}, reintentando...")


@retry(
    retry=retry_if_exception_type(httpx.ReadTimeout),
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=4, max=30),
    before_sleep=_on_retry,
    reraise=True,
)
def _call_api(bytes_a: bytes, bytes_b: bytes):
    return get_blend_client().models.generate_content(
        model=MODEL,
        contents=[
            BLEND_PROMPT,
            types.Part.from_bytes(data=bytes_a, mime_type="image/png"),
            types.Part.from_bytes(data=bytes_b, mime_type="image/png"),
        ],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            safety_settings=[],
        ),
    )


def blend_images(
    image_a: Image.Image, image_b: Image.Image
) -> tuple[Image.Image, float]:
    start = time.time()
    bytes_a = _to_bytes(image_a)
    bytes_b = _to_bytes(image_b)
    try:
        response = _call_api(bytes_a, bytes_b)
    except errors.APIError as e:
        raise RuntimeError(f"[Step 3] Error de API {e.code}: {e.message}") from e
    except httpx.ReadTimeout:
        raise RuntimeError(f"[Step 3] Timeout tras 3 intentos (>{TIMEOUT}s c/u). Reintentá más tarde.") from None

    image_bytes = _extract_image_bytes(response)
    return Image.open(io.BytesIO(image_bytes)), round(time.time() - start, 2)


def _to_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def _extract_image_bytes(response) -> bytes:
    candidate = response.candidates[0]
    if candidate.content is None:
        reason = getattr(candidate, "finish_reason", "desconocido")
        raise ValueError(f"[Step 3] El modelo no generó contenido. finish_reason={reason}")
    for part in candidate.content.parts:
        if part.inline_data is not None:
            return part.inline_data.data
    raise ValueError("[Step 3] El modelo respondió pero sin imagen. Revisá las imágenes de entrada.")
