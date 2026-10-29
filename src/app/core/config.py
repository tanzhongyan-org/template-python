"""Application configuration settings."""

from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Environments where the dev identity shortcut may run. Every other value is
# treated as production and the shortcut stays off there.
DEV_ENVS = frozenset({"development", "test"})


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "template-python"
    app_env: str = "development"
    debug: bool = False
    trust_identity_header: bool = False
    max_request_body_bytes: int = 1_048_576
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/template_python"
    # Product JWT validation. Point these at the product's Better Auth `jwt`
    # plugin; while they are unset, bearer tokens are rejected.
    # TEMPLATE-TODO(auth): set JWKS_URL, JWT_ISSUER and JWT_AUDIENCE for the product
    jwks_url: str | None = None
    jwt_issuer: str | None = None
    jwt_audience: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def _forbid_dev_shortcut_outside_dev(self) -> Self:
        """Fail boot when the dev identity shortcut is on outside dev/test."""
        if self.trust_identity_header and self.app_env not in DEV_ENVS:
            raise ValueError(
                "TRUST_IDENTITY_HEADER is true but APP_ENV is "
                f"'{self.app_env}'; dev identity works only in development and test"
            )
        return self


settings = Settings()
