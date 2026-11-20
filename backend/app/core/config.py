"""Application configuration using Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me"

    database_url: str = "sqlite:///./reposentinel.db"

    github_client_id: str = ""
    github_client_secret: str = ""
    github_redirect_uri: str = "http://localhost:5173/auth/callback"

    frontend_url: str = "http://localhost:5173"

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
