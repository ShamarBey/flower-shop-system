"""Только реализованные HTTP-модели; полный план API — openapi.yaml."""

from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["pass"]
    app_name: str
    version: str
    environment: Literal["development", "test", "production"]
    uptime: float = Field(ge=0, description="Время с запуска сервиса, в секундах")
