import pytest
import pytest_asyncio
from unittest.mock import AsyncMock

from httpx import ASGITransport, AsyncClient


# ── Sample data factories ────────────────────────────────────────────

SAMPLE_TASK = {
    "id": 1,
    "title": "Test task",
    "description": "A test task description",
    "status": "pending",
    "due_at": "2026-03-01T12:00:00",
    "category_id": 1,
    "tag_ids": [1, 2],
}

SAMPLE_COMPLETED_TASK = {
    "id": 2,
    "title": "Done task",
    "description": "Already done",
    "status": "completed",
    "due_at": "2026-02-15T10:00:00",
    "category_id": None,
    "tag_ids": [],
}

SAMPLE_CATEGORY = {"id": 1, "name": "Work"}
SAMPLE_TAG = {"id": 1, "name": "urgent"}

DEFAULT_SETTINGS = {
    "timezone": "America/Santiago",
    "theme": "light",
    "notifications_enabled": True,
    "near_due_hours": 24,
    "scheduler_interval_seconds": 60,
    "ntfy_topics": "",
}

SAMPLE_HEALTH = {
    "status": "healthy",
    "version": "2.0.0-vibe",
    "checks": {
        "database": {"status": "up"},
        "settings": {"status": "loaded", "timezone": "America/Santiago"},
        "platform": {"python": "3.13", "system": "Linux", "machine": "x86_64"},
    },
}


# ── Fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
def mock_backend():
    """Create a mock BackendClient with sensible defaults."""
    from app.utils.backend import BackendClient
    mock = AsyncMock(spec=BackendClient)

    # Task operations
    mock.get_tasks.return_value = [SAMPLE_TASK]
    mock.create_task.return_value = SAMPLE_TASK
    mock.delete_task.return_value = {"message": "deleted"}
    mock.complete_task.return_value = {**SAMPLE_TASK, "status": "completed"}
    mock.get_next_tasks.return_value = [SAMPLE_TASK]
    mock.get_overdue_tasks.return_value = []

    # Category operations
    mock.get_categories.return_value = [SAMPLE_CATEGORY]
    mock.create_category.return_value = SAMPLE_CATEGORY
    mock.delete_category.return_value = {"message": "deleted"}

    # Tag operations
    mock.get_tags.return_value = [SAMPLE_TAG]
    mock.create_tag.return_value = SAMPLE_TAG
    mock.delete_tag.return_value = {"message": "deleted"}

    # Notification operations
    mock.trigger_notifications.return_value = {"sent": 0}
    mock.test_notification.return_value = {"destinations": []}
    mock.get_notification_logs.return_value = []
    mock.get_notification_template.return_value = {"key": "due_soon", "markdown": ""}
    mock.update_notification_template.return_value = {"ok": True}

    # Settings
    mock.get_settings.return_value = DEFAULT_SETTINGS.copy()
    mock.update_settings.return_value = {"ok": True, "settings": DEFAULT_SETTINGS}

    # Views
    mock.get_views_summary.return_value = [
        {"key": "pending", "count": 5},
        {"key": "completed", "count": 3},
    ]

    # Health
    mock.health_check.return_value = SAMPLE_HEALTH.copy()

    return mock


@pytest_asyncio.fixture
async def client(mock_backend):
    """Provide an httpx AsyncClient with the backend mocked out."""
    import app.app as app_module

    original_backend = app_module.backend
    app_module.backend = mock_backend

    transport = ASGITransport(app=app_module.app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app_module.backend = original_backend
