"""Информация о процессе без зависимости от веб-фреймворка."""

from collections.abc import Callable
from dataclasses import dataclass
from time import monotonic


@dataclass(frozen=True, slots=True)
class HealthSnapshot:
    status: str
    app_name: str
    version: str
    environment: str
    uptime: float


class HealthService:
    def __init__(
        self,
        app_name: str,
        version: str,
        environment: str,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self._app_name = app_name
        self._version = version
        self._environment = environment
        self._clock = clock
        self._started_at = clock()

    def get_health(self) -> HealthSnapshot:
        return HealthSnapshot(
            status="pass",
            app_name=self._app_name,
            version=self._version,
            environment=self._environment,
            uptime=round(max(0.0, self._clock() - self._started_at), 3),
        )
