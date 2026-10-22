import os
from pathlib import Path
import subprocess
import sys

from pydantic import ValidationError
import pytest

from flower_shop.config.settings import Settings


def test_defaults_allow_local_start_without_env():
    settings = Settings()

    assert settings.app_name == "Flower Shop API"
    assert settings.app_version == "1.0.0"
    assert settings.app_env == "development"
    assert settings.http_host == "127.0.0.1"
    assert settings.http_port == 8000


def test_dotenv_loads_utf8_configuration():
    Path(".env").write_text(
        'APP_NAME="Цветочный магазин"\nAPP_VERSION=2.1.0\n'
        "APP_ENV=test\nHTTP_HOST=127.0.0.2\nHTTP_PORT=8123\n",
        encoding="utf-8",
    )

    settings = Settings()

    assert settings.app_name == "Цветочный магазин"
    assert settings.app_version == "2.1.0"
    assert settings.app_env == "test"
    assert settings.http_host == "127.0.0.2"
    assert settings.http_port == 8123


def test_process_environment_overrides_dotenv(monkeypatch):
    Path(".env").write_text("APP_NAME=From file\nHTTP_PORT=8123\n", encoding="utf-8")
    monkeypatch.setenv("APP_NAME", "From environment")
    monkeypatch.setenv("HTTP_PORT", "8234")

    settings = Settings()

    assert settings.app_name == "From environment"
    assert settings.http_port == 8234


def test_unrelated_dotenv_keys_do_not_prevent_start():
    Path(".env").write_text("FUTURE_DATABASE_URL=not-used-in-lab3\n", encoding="utf-8")

    assert Settings().app_name == "Flower Shop API"


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("APP_NAME", ""),
        ("APP_VERSION", ""),
        ("HTTP_HOST", ""),
        ("APP_ENV", "staging"),
        ("HTTP_PORT", "0"),
        ("HTTP_PORT", "65536"),
        ("HTTP_PORT", "not-a-port"),
    ],
)
def test_invalid_configuration_fails_before_serving_requests(monkeypatch, name, value):
    monkeypatch.setenv(name, value)

    with pytest.raises(ValidationError):
        Settings()


def test_import_does_not_read_invalid_configuration():
    environment = os.environ.copy()
    environment["APP_ENV"] = "invalid-import-test"
    result = subprocess.run(
        [sys.executable, "-c", "import flower_shop.main; print('imported')"],
        env=environment,
        text=True,
        capture_output=True,
        check=False,
        timeout=15,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "imported"
