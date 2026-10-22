"""Composition root: связывает конфигурацию, сервисы и HTTP."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from flower_shop.api.health import router as health_router
from flower_shop.config.settings import Settings
from flower_shop.service.health import HealthService


def create_app(settings: Settings | None = None) -> FastAPI:
    configuration = settings if settings is not None else Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.health_service = HealthService(
            app_name=configuration.app_name,
            version=configuration.app_version,
            environment=configuration.app_env,
        )
        yield

    app = FastAPI(
        title=configuration.app_name,
        version=configuration.app_version,
        description="Лабораторная №3: реализована проверка здоровья. Полный проектный контракт находится в openapi.yaml.",
        lifespan=lifespan,
    )
    app.include_router(health_router)
    return app
