import io
import time
import google.generativeai as genai
from PIL import Image


MODEL = "gemini-2.5-flash-preview-05-20"


def edit_image(image: Image.Image, instruccion: str) -> tuple[Image.Image, float]:
    start = time.time()

    img_bytes = _image_to_bytes(image)

    model = genai.GenerativeModel(MODEL)
    response = model.generate_content(
        [
            instruccion,
            {"mime_type": "image/png", "data": img_bytes},
        ],
        generation_config=genai.GenerationConfig(
            response_modalities=["IMAGE"]
        ),
    )

    edited_bytes = _extract_image_bytes(response)
    elapsed = round(time.time() - start, 2)
    return Image.open(io.BytesIO(edited_bytes)), elapsed


def _image_to_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def _extract_image_bytes(response) -> bytes:
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            return part.inline_data.data
    raise ValueError("El modelo no devolvió una imagen en la respuesta de edición.")
