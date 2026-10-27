"""Application configuration settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "template-python"
    app_env: str = "development"
    debug: bool = False
    trust_identity_header: bool = False
    max_request_body_bytes: int = 1_048_576
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/template_python"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
