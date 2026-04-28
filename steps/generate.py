import io
import time

import httpx
from google.genai import types, errors
from PIL import Image
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from client import get_client, MODEL, TIMEOUT


def _on_retry(retry_state):
    print(f"  [Step 1] Timeout en intento {retry_state.attempt_number}, reintentando...")


@retry(
    retry=retry_if_exception_type(httpx.ReadTimeout),
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=4, max=30),
    before_sleep=_on_retry,
    reraise=True,
)
def _call_api(tema: str):
    return get_client().models.generate_content(
        model=MODEL,
        contents=tema,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            safety_settings=[],
        ),
    )


def generate_image(tema: str) -> tuple[Image.Image, float]:
    start = time.time()
    try:
        response = _call_api(tema)
    except errors.APIError as e:
        raise RuntimeError(f"[Step 1] Error de API {e.code}: {e.message}") from e
    except httpx.ReadTimeout:
        raise RuntimeError(f"[Step 1] Timeout tras 3 intentos (>{TIMEOUT}s c/u). Reintentá más tarde.") from None

    image_bytes = _extract_image_bytes(response)
    return Image.open(io.BytesIO(image_bytes)), round(time.time() - start, 2)


def _extract_image_bytes(response) -> bytes:
    candidate = response.candidates[0]
    if candidate.content is None:
        reason = getattr(candidate, "finish_reason", "desconocido")
        raise ValueError(f"[Step 1] El modelo no generó contenido. finish_reason={reason}")
    for part in candidate.content.parts:
        if part.inline_data is not None:
            return part.inline_data.data
    raise ValueError("[Step 1] El modelo respondió pero sin imagen. Revisá el prompt.")
