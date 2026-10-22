"""Запуск: python -m flower_shop; host и port берутся из окружения."""

import uvicorn

from flower_shop.config.settings import Settings
from flower_shop.main import create_app


def main() -> None:
    settings = Settings()
    uvicorn.run(create_app(settings), host=settings.http_host, port=settings.http_port)


if __name__ == "__main__":
    main()
