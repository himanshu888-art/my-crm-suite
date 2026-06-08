from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str | None = None
    JWT_SECRET: str
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    OPENAI_MODEL: str = "microsoft/phi-4-mini-instruct"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()