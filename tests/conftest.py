"""Изоляция конфигурации: тесты не используют локальный .env разработчика."""

import pytest


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for name in ("APP_NAME", "APP_VERSION", "APP_ENV", "HTTP_HOST", "HTTP_PORT"):
        monkeypatch.delenv(name, raising=False)
