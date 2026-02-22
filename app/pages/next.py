# pages/next.py

from datetime import datetime
from fasthtml.common import *

from app.i18n import t
from app.utils.components import shell, task_card
from app.utils.backend import BackendClient


def next_page(backend: BackendClient):
    """Display tasks due in the next 48 hours"""
    # Time period selector
    time_selector = Div(
        H3(t("next.time_period")),
        Form(
            Select(
                Option(t("next.option_12h"), value="12"),
                Option(t("next.option_24h"), value="24"),
                Option(t("next.option_48h"), value="48", selected=True),
                Option(t("next.option_72h"), value="72"),
                Option(t("next.option_week"), value="168"),
                name="hours"
            ),
            Button(t("next.update_button"), type="submit"),
            **{
                "hx-get": "/api/tasks/next",
                "hx-target": "#upcoming-tasks",
                "hx-include": "[name='hours']",
            },
        ),
        **{"class": "form-section"}
    )
    content = Section(
        H2(t("next.title")),
        P(t("next.subtitle")),
        time_selector,
        Hr(),
        H3(t("next.due_soon")),
        Div(
            t("next.loading_upcoming"),
            id="upcoming-tasks",
            **{                                                 # type: ignore
                "hx-get": "/api/tasks/next?hours=48",
                "hx-trigger": "load",
                "hx-swap": "innerHTML",
            },
        ),
        Hr(),
        H3(t("next.overdue_title")),
        Div(
            t("next.loading_overdue"),
            id="overdue-tasks",
            **{                                                 # type: ignore
                "hx-get": "/app/next/overdue",
                "hx-trigger": "load",
                "hx-swap": "innerHTML",
            },
        ),
    )
    return shell(content)


async def render_upcoming_tasks(backend: BackendClient, hours: int = 48):
    """Render tasks due within specified hours"""
    try:
        tasks = await backend.get_next_tasks(hours)
        if not tasks:
            return Div(
                P(t("empty_states.no_tasks_due", hours=hours)),
                P(
                    t("empty_states.no_tasks_due_congrats"),
                    style="color: var(--ins-color);"
                )
            )

        # Build lookup maps
        categories = await backend.get_categories()
        tags = await backend.get_tags()
        cat_map = {c['id']: c['name'] for c in categories}
        tag_map = {tg['id']: tg['name'] for tg in tags}

        # Group tasks by time urgency
        now = datetime.now()
        urgent = []   # due within 6 hours
        soon = []     # due within 24 hours
        later = []    # due later

        for task in tasks:
            due_at_str = task.get('due_at')
            if not due_at_str:
                later.append(task)
                continue
            try:
                due_dt = datetime.fromisoformat(
                    str(due_at_str).replace('Z', '+00:00')
                )
                time_diff = due_dt - now
                if time_diff.total_seconds() < 6 * 3600:
                    urgent.append(task)
                elif time_diff.total_seconds() < 24 * 3600:
                    soon.append(task)
                else:
                    later.append(task)
            except Exception:
                later.append(task)

        sections = []
        if urgent:
            sections.extend([
                H4(t("next.due_very_soon"), style="color: var(--del-color);"),
                *[task_card(task, cat_map, tag_map) for task in urgent]
            ])
        if soon:
            sections.extend([
                H4(t("next.due_today"), style="color: var(--mark-color);"),
                *[task_card(task, cat_map, tag_map) for task in soon]
            ])
        if later:
            sections.extend([
                H4(t("next.due_later"), style="color: var(--muted-color);"),
                *[task_card(task, cat_map, tag_map) for task in later]
            ])

        return Div(
            P(t("next.found_count", count=len(tasks), hours=hours)),
            *sections
        )
    except Exception as e:
        from app.utils.components import error_message
        return error_message(t("errors.loading_upcoming_tasks", error=str(e)))


async def render_overdue_tasks(backend: BackendClient):
    """Render overdue tasks using the dedicated backend endpoint"""
    try:
        overdue_tasks = await backend.get_overdue_tasks()

        if not overdue_tasks:
            return P(t("empty_states.no_overdue"), style="color: var(--ins-color);")

        # Build lookup maps
        categories = await backend.get_categories()
        tags = await backend.get_tags()
        cat_map = {c['id']: c['name'] for c in categories}
        tag_map = {tg['id']: tg['name'] for tg in tags}

        now = datetime.now()
        task_elements = []
        for task in overdue_tasks:
            due_at_str = task.get('due_at')
            overdue_text = t("next.overdue_title")
            if due_at_str:
                try:
                    due_dt = datetime.fromisoformat(
                        str(due_at_str).replace('Z', '+00:00')
                    )
                    days = (now - due_dt).days
                    overdue_text = t("next.overdue_by_days", days=days)
                except Exception:
                    pass

            task_elements.append(
                Div(
                    P(
                        overdue_text,
                        style="color: var(--del-color); font-weight: bold; margin-bottom: 0.5rem;"
                    ),
                    task_card(task, cat_map, tag_map)
                )
            )

        return Div(
            P(
                t("next.overdue_count", count=len(overdue_tasks)),
                style="color: var(--del-color); font-weight: bold;"
            ),
            *task_elements
        )
    except Exception as e:
        from app.utils.components import error_message
        return error_message(t("errors.loading_overdue_tasks", error=str(e)))
