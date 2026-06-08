from openai import OpenAI
from backend.database.config import get_settings

settings = get_settings()

client_kwargs = {"api_key": settings.OPENAI_API_KEY}
if settings.OPENAI_BASE_URL:
    base_url = settings.OPENAI_BASE_URL.rstrip("/")
    if not base_url.endswith("/v1"):
        base_url = base_url + "/v1"
    client_kwargs["base_url"] = base_url

client = OpenAI(**client_kwargs)
