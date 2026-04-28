import os
from functools import lru_cache
from google import genai


MODEL = "gemini-2.5-flash"


@lru_cache(maxsize=None)
def get_client() -> genai.Client:
    if not os.getenv("GOOGLE_API_KEY"):
        raise EnvironmentError(
            "GOOGLE_API_KEY no está configurada. Copia .env.example a .env y agrega tu key."
        )
    return genai.Client(http_options={"timeout": 120})
