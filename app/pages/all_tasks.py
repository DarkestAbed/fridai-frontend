# pages/all_tasks.py

from fasthtml.common import *

from app.utils.components import shell, task_card
from app.utils.backend import BackendClient


def all_tasks_page(backend: BackendClient):
    """Display all tasks with filtering and sorting options"""
    # Filter controls
    filters = Div(
        H3("Filters & Sorting"),
        Form(
            Div(
                Label("Status:"),
                Select(
                    Option("All", value="all", selected=True),
                    Option("Active", value="active"),
                    Option("Completed", value="completed"),
                    name="status"
                ),
                style="display: inline-block; margin-right: 1rem;"
            ),
            Div(
                Label("Priority:"),
                Select(
                    Option("All", value="all", selected=True),
                    Option("High", value="high"),
                    Option("Medium", value="medium"),
                    Option("Low", value="low"),
                    name="priority"
                ),
                style="display: inline-block; margin-right: 1rem;"
            ),
            Div(
                Label("Sort by:"),
                Select(
                    Option("Created Date", value="created", selected=True),
                    Option("Due Date", value="due_date"),
                    Option("Title", value="title"),
                    Option("Priority", value="priority"),
                    name="sort"
                ),
                style="display: inline-block; margin-right: 1rem;"
            ),
            Button("Apply Filters", type="submit"),
            **{
                "hx-get": "/app/all",
                "hx-target": "#tasks-container",
                "hx-include": "[name='status'], [name='priority'], [name='sort']"
            },
        ),
        class_="form-section"
    )
    content = Section(
        H2("All Tasks"),
        filters,   
        Div(
            Div(
                "Loading all tasks...", 
                **{                                     # type: ignore
                    "hx-get": "/api/tasks",
                    "hx-trigger": "load",
                    "hx-target": "this",
                    "hx-swap": "innerHTML",
                }
            ),
            id="tasks-container"
        ),
        Div(
            H3("Quick Actions"),
            Button(
                "Mark All Complete", 
                **{                                                         # type: ignore
                    "hx-post": "/api/tasks/complete-all",
                    "hx-confirm": "Mark all active tasks as complete?",
                    "hx-target": "#tasks-container",
                }
            ),
            Button(
                "Delete All Completed", 
                **{                                                         # type: ignore
                    "hx-delete": "/api/tasks/completed",
                    "hx-confirm": "Delete all completed tasks? This cannot be undone.",
                    "hx-target": "#tasks-container",
                }
            ),
            style="margin-top: 2rem;"
        )
    )    
    return shell(content)


async def render_tasks_list(backend: BackendClient, status: str = "all", priority: str = "all", sort: str = "created"):
    """Render filtered and sorted tasks list"""
    try:
        # Get tasks based on status filter
        if status == "active":
            tasks = await backend.get_tasks(completed=False)
        elif status == "completed":
            tasks = await backend.get_tasks(completed=True)
        else:
            tasks = await backend.get_tasks()
        # Filter by priority if specified
        if priority != "all":
            tasks = [t for t in tasks if t.get("priority") == priority]
        # Sort tasks
        if sort == "due_date":
            tasks.sort(key=lambda t: t.get("due_date") or "9999-12-31", reverse=False)
        elif sort == "title":
            tasks.sort(key=lambda t: t.get("title", "").lower())
        elif sort == "priority":
            priority_order = {"high": 0, "medium": 1, "low": 2}
            tasks.sort(key=lambda t: priority_order.get(t.get("priority", "medium"), 1))
        else:  # default to created date
            tasks.sort(key=lambda t: t.get("created_at", ""), reverse=True)
        if not tasks:
            return Div(P("No tasks found matching the current filters."))
        task_elements = [task_card(task) for task in tasks]
        return Div(
            P(f"Showing {len(tasks)} task(s)"),
            *task_elements
        )
    except Exception as e:
        return Div(f"Error loading tasks: {str(e)}", class_="error-message")
