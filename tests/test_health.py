"""Tests for frontend health endpoints."""

import pytest


@pytest.mark.asyncio
async def test_health_liveness(client):
    """GET /health returns alive status."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "alive"
    assert data["service"] == "frontend"


@pytest.mark.asyncio
async def test_healthz_healthy(client, mock_backend):
    """GET /healthz returns healthy when backend is reachable."""
    resp = await client.get("/healthz")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0-vibe"
    assert data["checks"]["backend"]["status"] == "up"


@pytest.mark.asyncio
async def test_healthz_degraded(client, mock_backend):
    """GET /healthz returns 503 when backend is unreachable."""
    from app.utils.backend import BackendUnavailableError
    mock_backend.health_check.side_effect = BackendUnavailableError("down")

    resp = await client.get("/healthz")
    assert resp.status_code == 503
    data = resp.json()
    assert data["status"] == "degraded"
    assert data["checks"]["backend"]["status"] == "down"
