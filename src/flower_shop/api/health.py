"""Публичная проверка жизни процесса, без запросов к базе данных."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from flower_shop.api.schemas import HealthResponse
from flower_shop.service.health import HealthService

router = APIRouter(prefix="/api/v1", tags=["Health"])


def get_health_service(request: Request) -> HealthService:
    return request.app.state.health_service


@router.get(
    "/health",
    response_model=HealthResponse,
    operation_id="getHealth",
    summary="Проверить работоспособность серверного процесса",
)
def get_health(service: Annotated[HealthService, Depends(get_health_service)]) -> HealthResponse:
    snapshot = service.get_health()
    return HealthResponse(
        status=snapshot.status,
        app_name=snapshot.app_name,
        version=snapshot.version,
        environment=snapshot.environment,
        uptime=snapshot.uptime,
    )
