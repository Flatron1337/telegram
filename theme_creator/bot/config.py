from __future__ import annotations

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment or .env file."""

    bot_token: SecretStr
    max_file_size_mb: int = 15
    environment: str = "production"
    webapp_url: str | None = None
    webapp_host: str = "0.0.0.0"
    webapp_port: int = Field(
        default=8080,
        validation_alias=AliasChoices("WEBAPP_PORT", "PORT", "webapp_port"),
    )


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    """Instantiate and return settings singleton."""
    return Settings()  # type: ignore[call-arg]
