from fastapi.testclient import TestClient

from flower_shop.config.settings import Settings
from flower_shop.main import create_app
from flower_shop.service.health import HealthService


def test_public_health_returns_configured_service_identity_and_uptime():
    app = create_app(
        Settings(
            app_name="Flower Shop QA",
            app_version="3.2.1",
            app_env="test",
        )
    )

    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    body = response.json()
    assert set(body) == {"status", "app_name", "version", "environment", "uptime"}
    assert body["status"] == "pass"
    assert body["app_name"] == "Flower Shop QA"
    assert body["version"] == "3.2.1"
    assert body["environment"] == "test"
    assert isinstance(body["uptime"], (int, float)) and body["uptime"] >= 0


def test_repeated_health_checks_have_nondecreasing_uptime():
    with TestClient(create_app(Settings())) as client:
        first = client.get("/api/v1/health").json()
        second = client.get("/api/v1/health").json()

    assert first["status"] == second["status"] == "pass"
    assert second["uptime"] >= first["uptime"] >= 0


def test_live_openapi_documents_only_implemented_public_health():
    with TestClient(create_app(Settings())) as client:
        specification = client.get("/openapi.json")
        documentation = client.get("/docs")

    assert specification.status_code == 200
    body = specification.json()
    assert set(body["paths"]) == {"/api/v1/health"}
    operation = body["paths"]["/api/v1/health"]["get"]
    assert "200" in operation["responses"]
    assert operation.get("security", body.get("security", [])) == []
    assert documentation.status_code == 200
    assert "SwaggerUIBundle" in documentation.text


def test_catalog_and_orders_are_not_fake_implemented_routes():
    with TestClient(create_app(Settings())) as client:
        assert client.get("/api/v1/products").status_code == 404
        assert client.post("/api/v1/orders", json={}).status_code == 404


def test_service_uses_elapsed_clock_instead_of_calendar_time():
    ticks = iter([100.0, 104.25])
    service = HealthService("Flower Shop API", "1.0.0", "test", clock=lambda: next(ticks))

    snapshot = service.get_health()

    assert snapshot.uptime == 4.25
    assert snapshot.status == "pass"


def test_service_instances_have_independent_uptime():
    first_clock = iter([10.0, 15.0])
    second_clock = iter([1000.0, 1002.0])
    first = HealthService("First", "1.0.0", "test", clock=lambda: next(first_clock))
    second = HealthService("Second", "1.0.0", "test", clock=lambda: next(second_clock))

    assert first.get_health().uptime == 5.0
    assert second.get_health().uptime == 2.0
