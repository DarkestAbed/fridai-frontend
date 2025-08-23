# pages/home.py

from fasthtml.common import *
from utils.components import shell


def home_page():
    """Home page with dashboard overview"""
    content = Section(
        H1("Task Management Dashboard"),
        P("Welcome to your personal task management system."),
        Div(
            Div(
                H3("Quick Actions"),
                Ul(
                    Li(A("Add New Task", href="/app/tasks")),
                    Li(A("View All Tasks", href="/app/all")),
                    Li(A("Check Next 48 Hours", href="/app/next")),
                    Li(A("Manage Categories", href="/app/categories")),
                ),
            ),
            Div(
                H3("Recent Activity"),
                Div(
                    "Loading recent tasks...", 
                    id="recent-tasks",
                    **{                                     # type: ignore
                        "hx-get": "/api/tasks?limit=5",
                        "hx-trigger": "load",
                        "hx-swap": "innerHTML"
                    }
                ),
            ),
            style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;"
        ),
        Div(
            H3("System Status"),
            P("All systems operational", style="color: green;"),
            Button(
                "Trigger Notifications", 
                **{                                                         # type: ignore
                    "hx-post": "/app/notifications/trigger",
                    "hx-target": "#notification-status",
                },
            ),
            Div(id="notification-status")
        )
    )
    return shell(content)
