"""Конфигурация загружается явно в точке сборки приложения."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        str_strip_whitespace=True,
        frozen=True,
        hide_input_in_errors=True,
    )

    app_name: str = Field(default="Flower Shop API", validation_alias="APP_NAME", min_length=1)
    app_version: str = Field(default="1.0.0", validation_alias="APP_VERSION", min_length=1)
    app_env: Literal["development", "test", "production"] = Field(
        default="development", validation_alias="APP_ENV"
    )
    http_host: str = Field(default="127.0.0.1", validation_alias="HTTP_HOST", min_length=1)
    http_port: int = Field(default=8000, validation_alias="HTTP_PORT", ge=1, le=65535)
