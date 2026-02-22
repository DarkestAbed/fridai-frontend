"""Tests for UI components — task_card, error_message, success_message, nav."""

import pytest
from fasthtml.common import to_xml

from app.utils.components import task_card, error_message, success_message, nav


def _render(element) -> str:
    """Render a FastHTML element to an HTML string."""
    return to_xml(element)


class TestTaskCard:
    """Tests for the task_card component."""

    def test_renders_title(self):
        task = {"id": 1, "title": "My Task", "status": "pending", "tag_ids": []}
        html = _render(task_card(task))
        assert "My Task" in html

    def test_completed_task_has_class(self):
        task = {"id": 2, "title": "Done", "status": "completed", "tag_ids": []}
        html = _render(task_card(task))
        assert "task-completed" in html

    def test_pending_task_has_complete_button(self):
        task = {"id": 3, "title": "Todo", "status": "pending", "tag_ids": []}
        html = _render(task_card(task))
        assert "Complete" in html
        assert "hx-put" in html

    def test_completed_task_no_complete_button(self):
        task = {"id": 4, "title": "Done", "status": "completed", "tag_ids": []}
        html = _render(task_card(task))
        # Should have Delete but not the Complete action button
        assert "Delete" in html
        assert "hx-put" not in html

    def test_due_at_rendered(self):
        task = {
            "id": 5,
            "title": "Due",
            "status": "pending",
            "due_at": "2026-03-01T12:00:00",
            "tag_ids": [],
        }
        html = _render(task_card(task))
        assert "Due:" in html
        assert "2026-03-01" in html

    def test_category_map_resolves_name(self):
        task = {
            "id": 6,
            "title": "Cat",
            "status": "pending",
            "category_id": 1,
            "tag_ids": [],
        }
        html = _render(task_card(task, category_map={1: "Work"}))
        assert "Category: Work" in html

    def test_category_fallback_without_map(self):
        task = {
            "id": 7,
            "title": "Cat",
            "status": "pending",
            "category_id": 42,
            "tag_ids": [],
        }
        html = _render(task_card(task))
        assert "#42" in html

    def test_tag_map_resolves_names(self):
        task = {
            "id": 8,
            "title": "Tagged",
            "status": "pending",
            "tag_ids": [1, 2],
        }
        html = _render(task_card(task, tag_map={1: "urgent", 2: "work"}))
        assert "urgent" in html
        assert "work" in html

    def test_tag_fallback_without_map(self):
        task = {
            "id": 9,
            "title": "Tagged",
            "status": "pending",
            "tag_ids": [10],
        }
        html = _render(task_card(task))
        assert "#10" in html

    def test_no_priority_class(self):
        """Backend has no priority field — verify no priority-* CSS class."""
        task = {"id": 10, "title": "Test", "status": "pending", "tag_ids": []}
        html = _render(task_card(task))
        assert "priority-" not in html


class TestMessages:
    def test_error_message(self):
        html = _render(error_message("Something went wrong"))
        assert "Something went wrong" in html
        assert "error-message" in html

    def test_success_message(self):
        html = _render(success_message("Task created"))
        assert "Task created" in html
        assert "success-message" in html


class TestNav:
    def test_nav_contains_links(self):
        html = _render(nav())
        assert "Home" in html
        assert "Tasks" in html
        assert "Categories" in html
        assert "Tags" in html
        assert "Settings" in html
