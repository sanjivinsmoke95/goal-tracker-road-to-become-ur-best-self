"""Application configuration, read once from the environment."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    # App
    app_name: str = "Adaptive Learning OS"
    environment: str = "development"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Auth
    secret_key: str = "dev-insecure-secret-change-me"
    access_token_expire_minutes: int = 60 * 24 * 7
    jwt_algorithm: str = "HS256"

    # Database
    database_url: str = "postgresql+psycopg2://learnos:learnos@localhost:5433/learnos"

    # AI provider — swappable. Default "stub" so the app runs with no keys.
    ai_provider: str = "stub"  # stub | gemini | openai_compatible
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    openai_base_url: str = ""
    openai_api_key: str = ""
    openai_model: str = ""

    # Platform integrations (Codeforces API is public — no key required).
    codeforces_api_base: str = "https://codeforces.com/api"
    codeforces_rate_limit_seconds: float = 1.0

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
