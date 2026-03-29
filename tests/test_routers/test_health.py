import pytest


async def test_health_connected_returns_200(client_connected):
    """GET /health returns 200 with status ok and database connected."""
    response = await client_connected.get("/health/")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "connected"
    assert "timestamp" in body


async def test_health_disconnected_returns_503(client_disconnected):
    """GET /health returns 503 with status degraded and database disconnected."""
    response = await client_disconnected.get("/health/")
    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail["status"] == "degraded"
    assert detail["database"] == "disconnected"


async def test_health_no_auth_required(client_connected):
    """GET /health without Authorization header returns 200, not 401/403."""
    response = await client_connected.get("/health/")
    assert response.status_code not in (401, 403)
    assert response.status_code == 200
