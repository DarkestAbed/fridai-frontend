"""Tests for page routes — verify each returns 200 with HTML."""

import pytest


@pytest.mark.asyncio
async def test_home_page(client):
    resp = await client.get("/app")
    assert resp.status_code == 200
    assert "Task Management Dashboard" in resp.text


@pytest.mark.asyncio
async def test_tasks_page(client):
    resp = await client.get("/app/tasks")
    assert resp.status_code == 200
    assert "Task Management" in resp.text
    assert "Add New Task" in resp.text


@pytest.mark.asyncio
async def test_all_tasks_page(client):
    resp = await client.get("/app/all")
    assert resp.status_code == 200
    assert "All Tasks" in resp.text
    assert "Filters" in resp.text


@pytest.mark.asyncio
async def test_categories_page(client):
    resp = await client.get("/app/categories")
    assert resp.status_code == 200
    assert "Category Management" in resp.text


@pytest.mark.asyncio
async def test_tags_page(client):
    resp = await client.get("/app/tags")
    assert resp.status_code == 200
    assert "Tag Management" in resp.text


@pytest.mark.asyncio
async def test_next_page(client):
    resp = await client.get("/app/next")
    assert resp.status_code == 200
    assert "Upcoming Tasks" in resp.text


@pytest.mark.asyncio
async def test_notifications_page(client):
    resp = await client.get("/app/notifications")
    assert resp.status_code == 200
    assert "Notification Management" in resp.text


@pytest.mark.asyncio
async def test_settings_page(client):
    resp = await client.get("/app/settings")
    assert resp.status_code == 200
    assert "Settings" in resp.text


@pytest.mark.asyncio
async def test_pages_contain_navigation(client):
    """All pages should contain the nav bar."""
    for path in ["/app", "/app/tasks", "/app/all", "/app/categories",
                 "/app/tags", "/app/next", "/app/notifications", "/app/settings"]:
        resp = await client.get(path)
        assert resp.status_code == 200
        assert "Task Manager" in resp.text, f"Nav missing on {path}"
        assert "picocss" in resp.text.lower() or "pico" in resp.text.lower(), \
            f"PicoCSS missing on {path}"
