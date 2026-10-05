from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    database_sslmode: str = "require"
    supabase_url: str
    supabase_publishable_key: str
    frontend_origin: str = "http://localhost:5173"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.8-flash"
    gemini_timeout_ms: int = Field(default=30000, ge=1000, le=120000)
    ai_review_cooldown_seconds: int = Field(default=10, ge=0, le=3600)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
