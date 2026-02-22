"""Tests for the task creation form handler."""

import pytest

from tests.conftest import SAMPLE_TASK, SAMPLE_CATEGORY, SAMPLE_TAG


@pytest.mark.asyncio
async def test_create_task_success(client, mock_backend):
    """POST /app/tasks with valid title creates a task."""
    resp = await client.post(
        "/app/tasks",
        data={"title": "New task", "description": "", "due_date": "", "category": "", "tags": ""},
    )
    assert resp.status_code == 200
    assert "created successfully" in resp.text
    mock_backend.create_task.assert_called_once()
    call_args = mock_backend.create_task.call_args[0][0]
    assert call_args["title"] == "New task"


@pytest.mark.asyncio
async def test_create_task_empty_title(client, mock_backend):
    """POST /app/tasks with empty title returns error."""
    resp = await client.post(
        "/app/tasks",
        data={"title": "", "description": "", "due_date": "", "category": "", "tags": ""},
    )
    assert resp.status_code == 200
    assert "Title is required" in resp.text
    mock_backend.create_task.assert_not_called()


@pytest.mark.asyncio
async def test_create_task_with_due_date(client, mock_backend):
    """POST /app/tasks with due_date sets due_at field."""
    resp = await client.post(
        "/app/tasks",
        data={
            "title": "Deadline task",
            "description": "",
            "due_date": "2026-03-01T12:00",
            "category": "",
            "tags": "",
        },
    )
    assert resp.status_code == 200
    call_args = mock_backend.create_task.call_args[0][0]
    assert call_args["due_at"] == "2026-03-01T12:00"


@pytest.mark.asyncio
async def test_create_task_with_existing_category(client, mock_backend):
    """POST /app/tasks resolves existing category by name."""
    mock_backend.get_categories.return_value = [SAMPLE_CATEGORY]
    resp = await client.post(
        "/app/tasks",
        data={
            "title": "Cat task",
            "description": "",
            "due_date": "",
            "category": "Work",
            "tags": "",
        },
    )
    assert resp.status_code == 200
    call_args = mock_backend.create_task.call_args[0][0]
    assert call_args["category_id"] == 1
    # Should NOT have created a new category
    mock_backend.create_category.assert_not_called()


@pytest.mark.asyncio
async def test_create_task_with_new_category(client, mock_backend):
    """POST /app/tasks creates a new category if not found."""
    mock_backend.get_categories.return_value = []
    mock_backend.create_category.return_value = {"id": 5, "name": "NewCat"}
    resp = await client.post(
        "/app/tasks",
        data={
            "title": "New cat task",
            "description": "",
            "due_date": "",
            "category": "NewCat",
            "tags": "",
        },
    )
    assert resp.status_code == 200
    mock_backend.create_category.assert_called_once_with({"name": "NewCat"})
    call_args = mock_backend.create_task.call_args[0][0]
    assert call_args["category_id"] == 5


@pytest.mark.asyncio
async def test_create_task_with_tags(client, mock_backend):
    """POST /app/tasks resolves and creates tags from comma-separated input."""
    mock_backend.get_tags.return_value = [SAMPLE_TAG]  # "urgent" exists
    mock_backend.create_tag.return_value = {"id": 99, "name": "new-tag"}
    resp = await client.post(
        "/app/tasks",
        data={
            "title": "Tagged task",
            "description": "",
            "due_date": "",
            "category": "",
            "tags": "urgent, new-tag",
        },
    )
    assert resp.status_code == 200
    # "urgent" exists so only "new-tag" should be created
    mock_backend.create_tag.assert_called_once_with({"name": "new-tag"})
    call_args = mock_backend.create_task.call_args[0][0]
    assert 1 in call_args["tag_ids"]   # existing tag
    assert 99 in call_args["tag_ids"]  # newly created tag
