# pages/all_tasks.py

from fasthtml.common import *

from app.i18n import t
from app.utils.components import shell, task_card, error_message
from app.utils.backend import BackendClient


def all_tasks_page(backend: BackendClient):
    """Display all tasks with filtering and sorting options"""
    # Filter controls
    filters = Div(
        H3(t("all_tasks.filters_title")),
        Form(
            Div(
                Label(t("all_tasks.status_label")),
                Select(
                    Option(t("all_tasks.status_all"), value="all", selected=True),
                    Option(t("all_tasks.status_active"), value="pending"),
                    Option(t("all_tasks.status_completed"), value="completed"),
                    name="status"
                ),
                style="display: inline-block; margin-right: 1rem;"
            ),
            Div(
                Label(t("all_tasks.sort_label")),
                Select(
                    Option(t("all_tasks.sort_due_date"), value="due_at", selected=True),
                    Option(t("all_tasks.sort_title"), value="title"),
                    name="sort"
                ),
                style="display: inline-block; margin-right: 1rem;"
            ),
            Button(t("all_tasks.apply_filters"), type="submit"),
            **{
                "hx-get": "/app/all/tasks",
                "hx-target": "#tasks-container",
                "hx-include": "[name='status'], [name='sort']",
                "hx-swap": "innerHTML",
            },
        ),
        **{"class": "form-section"}
    )
    content = Section(
        H2(t("all_tasks.title")),
        filters,
        Div(
            Div(
                t("all_tasks.loading_all"),
                **{                                     # type: ignore
                    "hx-get": "/app/all/tasks",
                    "hx-trigger": "load",
                    "hx-target": "this",
                    "hx-swap": "innerHTML",
                }
            ),
            id="tasks-container"
        ),
    )
    return shell(content)


async def render_tasks_list(
    backend: BackendClient,
    status: str = "all",
    sort: str = "due_at",
):
    """Render filtered and sorted tasks list as an HTML fragment."""
    try:
        # Map frontend filter to backend param
        backend_status = None
        if status in ("pending", "completed"):
            backend_status = status

        tasks = await backend.get_tasks(status=backend_status)

        # Build lookup maps
        categories = await backend.get_categories()
        tags = await backend.get_tags()
        cat_map = {c['id']: c['name'] for c in categories}
        tag_map = {tg['id']: tg['name'] for tg in tags}

        # Client-side sort
        if sort == "title":
            tasks.sort(key=lambda tk: tk.get("title", "").lower())
        else:  # default: due_at
            tasks.sort(key=lambda tk: tk.get("due_at") or "9999-12-31")

        if not tasks:
            return Div(P(t("empty_states.no_tasks_filtered")))

        task_elements = [task_card(task, cat_map, tag_map) for task in tasks]
        return Div(
            P(t("all_tasks.showing_count", count=len(tasks))),
            *task_elements
        )
    except Exception as e:
        return error_message(t("errors.loading_tasks", error=str(e)))
