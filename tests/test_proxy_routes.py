"""Tests for API proxy routes that return HTML fragments."""

import pytest

from tests.conftest import SAMPLE_TASK, SAMPLE_CATEGORY, SAMPLE_TAG


@pytest.mark.asyncio
async def test_get_tasks_returns_html(client, mock_backend):
    """GET /api/tasks returns task card HTML."""
    resp = await client.get("/api/tasks")
    assert resp.status_code == 200
    assert "Test task" in resp.text
    mock_backend.get_tasks.assert_called_once()


@pytest.mark.asyncio
async def test_get_tasks_empty(client, mock_backend):
    """GET /api/tasks with no tasks returns message."""
    mock_backend.get_tasks.return_value = []
    resp = await client.get("/api/tasks")
    assert resp.status_code == 200
    assert "No tasks found" in resp.text


@pytest.mark.asyncio
async def test_get_tasks_with_status_param(client, mock_backend):
    """GET /api/tasks?status=pending passes status to backend."""
    resp = await client.get("/api/tasks?status=pending")
    assert resp.status_code == 200
    mock_backend.get_tasks.assert_called_once_with(status="pending")


@pytest.mark.asyncio
async def test_get_tasks_with_limit(client, mock_backend):
    """GET /api/tasks?limit=1 truncates the response."""
    mock_backend.get_tasks.return_value = [SAMPLE_TASK, {**SAMPLE_TASK, "id": 2}]
    resp = await client.get("/api/tasks?limit=1")
    assert resp.status_code == 200
    # Should only contain one task card (count article ids)
    assert 'id="task-1"' in resp.text
    assert 'id="task-2"' not in resp.text


@pytest.mark.asyncio
async def test_delete_task(client, mock_backend):
    """DELETE /api/tasks/{id} calls backend with force=True."""
    resp = await client.delete("/api/tasks/1")
    assert resp.status_code == 200
    mock_backend.delete_task.assert_called_once_with("1", force=True)


@pytest.mark.asyncio
async def test_complete_task(client, mock_backend):
    """PUT /api/tasks/{id}/complete returns updated task card."""
    resp = await client.put("/api/tasks/1/complete")
    assert resp.status_code == 200
    mock_backend.complete_task.assert_called_once_with("1")
    assert "task-item" in resp.text


@pytest.mark.asyncio
async def test_delete_category(client, mock_backend):
    """DELETE /api/categories/{id} calls backend."""
    resp = await client.delete("/api/categories/1")
    assert resp.status_code == 200
    mock_backend.delete_category.assert_called_once_with("1")


@pytest.mark.asyncio
async def test_delete_tag(client, mock_backend):
    """DELETE /api/tags/{id} calls backend."""
    resp = await client.delete("/api/tags/1")
    assert resp.status_code == 200
    mock_backend.delete_tag.assert_called_once_with("1")


@pytest.mark.asyncio
async def test_get_categories_returns_html(client, mock_backend):
    """GET /api/categories returns category cards."""
    resp = await client.get("/api/categories")
    assert resp.status_code == 200
    assert "Work" in resp.text


@pytest.mark.asyncio
async def test_get_tags_returns_html(client, mock_backend):
    """GET /api/tags returns tag cards."""
    resp = await client.get("/api/tags")
    assert resp.status_code == 200
    assert "urgent" in resp.text


@pytest.mark.asyncio
async def test_backend_unavailable_shows_error(client, mock_backend):
    """When backend is down, proxy routes return error message."""
    from app.utils.backend import BackendUnavailableError
    mock_backend.get_tasks.side_effect = BackendUnavailableError("down")
    resp = await client.get("/api/tasks")
    assert resp.status_code == 200  # HTMX expects 200 with error HTML
    assert "unreachable" in resp.text.lower()
