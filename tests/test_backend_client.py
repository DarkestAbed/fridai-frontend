"""Unit tests for BackendClient — mock the httpx transport layer with respx."""

import pytest
import respx
from httpx import Response

from app.utils.backend import (
    BackendClient,
    BackendUnavailableError,
    BackendAPIError,
)

BASE = "http://test-backend"


@pytest.fixture
def bc():
    return BackendClient(BASE)


# ── Task endpoints ───────────────────────────────────────────────────

@respx.mock
@pytest.mark.asyncio
async def test_get_tasks_no_params(bc):
    respx.get(f"{BASE}/api/tasks").mock(return_value=Response(200, json=[]))
    result = await bc.get_tasks()
    assert result == []


@respx.mock
@pytest.mark.asyncio
async def test_get_tasks_with_status(bc):
    respx.get(f"{BASE}/api/tasks").mock(return_value=Response(200, json=[]))
    await bc.get_tasks(status="pending")
    assert "status=pending" in str(respx.calls[0].request.url)


@respx.mock
@pytest.mark.asyncio
async def test_create_task(bc):
    task = {"id": 1, "title": "Test", "status": "pending"}
    respx.post(f"{BASE}/api/tasks").mock(return_value=Response(201, json=task))
    result = await bc.create_task({"title": "Test"})
    assert result["id"] == 1


@respx.mock
@pytest.mark.asyncio
async def test_delete_task_with_force(bc):
    respx.delete(f"{BASE}/api/tasks/1").mock(
        return_value=Response(200, json={"message": "deleted"})
    )
    await bc.delete_task("1", force=True)
    assert "force=true" in str(respx.calls[0].request.url)


@respx.mock
@pytest.mark.asyncio
async def test_complete_task(bc):
    task = {"id": 1, "title": "Test", "status": "completed"}
    respx.post(f"{BASE}/api/tasks/1/complete").mock(
        return_value=Response(200, json=task)
    )
    result = await bc.complete_task("1")
    assert result["status"] == "completed"


@respx.mock
@pytest.mark.asyncio
async def test_get_overdue_tasks(bc):
    respx.get(f"{BASE}/api/tasks/overdue").mock(
        return_value=Response(200, json=[])
    )
    result = await bc.get_overdue_tasks()
    assert result == []


# ── Settings endpoints ───────────────────────────────────────────────

@respx.mock
@pytest.mark.asyncio
async def test_get_settings_hits_config(bc):
    respx.get(f"{BASE}/api/config").mock(
        return_value=Response(200, json={"timezone": "UTC"})
    )
    result = await bc.get_settings()
    assert result["timezone"] == "UTC"


@respx.mock
@pytest.mark.asyncio
async def test_update_settings_uses_patch(bc):
    respx.patch(f"{BASE}/api/config").mock(
        return_value=Response(200, json={"ok": True})
    )
    result = await bc.update_settings({"timezone": "UTC"})
    assert result["ok"] is True


# ── Notification endpoints ───────────────────────────────────────────

@respx.mock
@pytest.mark.asyncio
async def test_trigger_notifications_endpoint(bc):
    respx.post(f"{BASE}/api/notifications/cron").mock(
        return_value=Response(200, json={"sent": 3})
    )
    result = await bc.trigger_notifications(mode="both")
    assert result["sent"] == 3
    assert "mode=both" in str(respx.calls[0].request.url)


@respx.mock
@pytest.mark.asyncio
async def test_test_notification(bc):
    respx.post(f"{BASE}/api/notifications/test").mock(
        return_value=Response(200, json={"destinations": ["https://ntfy.sh/test"]})
    )
    result = await bc.test_notification()
    assert len(result["destinations"]) == 1


@respx.mock
@pytest.mark.asyncio
async def test_health_check(bc):
    respx.get(f"{BASE}/healthz").mock(
        return_value=Response(200, json={"status": "healthy"})
    )
    result = await bc.health_check()
    assert result["status"] == "healthy"


# ── Error handling ───────────────────────────────────────────────────

@respx.mock
@pytest.mark.asyncio
async def test_http_error_raises_api_error(bc):
    respx.get(f"{BASE}/api/tasks").mock(
        return_value=Response(404, text="Not found")
    )
    with pytest.raises(BackendAPIError) as exc_info:
        await bc.get_tasks()
    assert exc_info.value.status_code == 404


@respx.mock
@pytest.mark.asyncio
async def test_connect_error_raises_unavailable(bc):
    respx.get(f"{BASE}/api/tasks").mock(side_effect=Exception("connection refused"))
    with pytest.raises(Exception):
        await bc.get_tasks()
