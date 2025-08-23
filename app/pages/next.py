# pages/next.py

from datetime import datetime
from fasthtml.common import *

from app.utils.components import shell, task_card
from app.utils.backend import BackendClient


def next_page(backend: BackendClient):
    """Display tasks due in the next 48 hours"""
    # Time period selector
    time_selector = Div(
        H3("Time Period"),
        Form(
            Select(
                Option("Next 12 hours", value="12"),
                Option("Next 24 hours", value="24"),
                Option("Next 48 hours", value="48", selected=True),
                Option("Next 72 hours", value="72"),
                Option("Next week", value="168"),
                name="hours"
            ),
            Button("Update", type="submit"),
            **{
                "hx-get": "/app/next",
                "hx-target": "#upcoming-tasks",
                "hx-include": "[name='hours']",
            },
        ),
        class_="form-section"
    )
    content = Section(
        H2("Upcoming Tasks"),
        P("Tasks that are due soon, sorted by due date."),
        time_selector,
        Hr(),
        H3("Due Soon"),
        Div(
            "Loading upcoming tasks...", 
            id="upcoming-tasks",
            **{                                                 # type: ignore
                "hx-get": "/api/tasks/next?hours=48",
                "hx-trigger": "load",
                "hx-swap": "innerHTML",
            },
        ),
        Hr(),
        H3("Overdue Tasks"),
        Div(
            "Loading overdue tasks...", 
            id="overdue-tasks",
            **{                                                 # type: ignore
                "hx-get": "/app/next/overdue",
                "hx-trigger": "load",
                "hx-swap": "innerHTML",
            },
        ),
        Div(
            H3("Quick Actions"),
            Button(
                "Snooze All", 
                **{                                                     # type: ignore
                    "hx-post": "/app/next/snooze-all",
                    "hx-confirm": "Snooze all upcoming tasks by 24 hours?",
                    "hx-target": "#upcoming-tasks",
                }
            ),
            Button(
                "Mark Urgent as High Priority", 
                **{                                                     # type: ignore
                    "hx-post": "/app/next/mark-urgent",
                    "hx-target": "#upcoming-tasks",
                },
            ),
            style="margin-top: 2rem;"
        )
    )
    return shell(content)


async def render_upcoming_tasks(backend: BackendClient, hours: int = 48):
    """Render tasks due within specified hours"""
    try:
        tasks = await backend.get_next_tasks(hours)
        if not tasks:
            return Div(
                P(f"No tasks due in the next {hours} hours."),
                P(
                    "Great job staying on top of your schedule! 🎉",
                    style="color: #28a745;"
                )
            )
        # Group tasks by time urgency
        now = datetime.now()
        overdue = []
        urgent = []  # due within 6 hours
        soon = []    # due within 24 hours
        later = []   # due later
        for task in tasks:
            due_date_str = task.get('due_date')
            if not due_date_str:
                later.append(task)
                continue
            try:
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                time_diff = due_date - now
                if time_diff.total_seconds() < 0:
                    overdue.append(task)
                elif time_diff.total_seconds() < 6 * 3600:  # 6 hours
                    urgent.append(task)
                elif time_diff.total_seconds() < 24 * 3600:  # 24 hours
                    soon.append(task)
                else:
                    later.append(task)
            except:
                later.append(task)
        sections = []
        if overdue:
            sections.extend([
                H4("⚠️ Overdue", style="color: #dc3545;"),
                *[task_card(task) for task in overdue]
            ])
        if urgent:
            sections.extend([
                H4("🔥 Due Very Soon (< 6 hours)", style="color: #fd7e14;"),
                *[task_card(task) for task in urgent]
            ])
        if soon:
            sections.extend([
                H4("⏰ Due Today", style="color: #ffc107;"),
                *[task_card(task) for task in soon]
            ])
        if later:
            sections.extend([
                H4("📅 Due Later", style="color: #6c757d;"),
                *[task_card(task) for task in later]
            ])
        return Div(
            P(f"Found {len(tasks)} task(s) due in the next {hours} hours"),
            *sections
        )
    except Exception as e:
        return Div(f"Error loading upcoming tasks: {str(e)}", class_="error-message")


async def render_overdue_tasks(backend: BackendClient):
    """Render overdue tasks"""
    try:
        all_tasks = await backend.get_tasks(completed=False)
        now = datetime.now()
        overdue_tasks = []
        for task in all_tasks:
            due_date_str = task.get('due_date')
            if not due_date_str:
                continue
            try:
                due_date = datetime.fromisoformat(
                    due_date_str.replace('Z', '+00:00')
                )
                if due_date < now:
                    # Calculate how overdue
                    days_overdue = (now - due_date).days
                    task['days_overdue'] = days_overdue
                    overdue_tasks.append(task)
            except:
                continue
        if not overdue_tasks:
            return P("No overdue tasks! 🎉", style="color: #28a745;")
        # Sort by how overdue they are
        overdue_tasks.sort(key=lambda t: t.get('days_overdue', 0), reverse=True)
        task_elements = []
        for task in overdue_tasks:
            days = task.get('days_overdue', 0)
            overdue_text = f"Overdue by {days} day{'s' if days != 1 else ''}"
            # Add overdue indicator to task
            task_elem = task_card(task)
            # You could modify the task_card function to accept additional info
            task_elements.append(
                Div(
                    P(
                        overdue_text,
                        style="""
                        color: #dc3545;
                        font-weight: bold;
                        margin-bottom: 0.5rem;
                        """
                    ),
                    task_elem
                )
            )
        
        return Div(
            P(
                f"You have {len(overdue_tasks)} overdue task(s)",
                style="color: #dc3545; font-weight: bold;"
            ),
            *task_elements
        )
    except Exception as e:
        return Div(
            f"Error loading overdue tasks: {str(e)}",
            class_="error-message"
        )
