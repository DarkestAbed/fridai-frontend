# pages/home.py

from fasthtml.common import *

from app.utils.components import shell


def home_page():
    """Home page with dashboard overview"""
    content = Section(
        Hgroup(
            H1("Task Management Dashboard"),
            P("Welcome to your personal task management system")
        ),
        Div(
            Article(
                Header(H3("📋 Quick Actions")),
                Nav(
                    Ul(
                        Li(
                            A(
                                "➕ Add New Task",
                                href="/app/tasks",
                                # **{
                                #     "hx-get": "/app/tasks",
                                #     "hx-target": "#content"
                                # }
                            )
                        ),
                        Li(
                            A(
                                "📊 View All Tasks", 
                                href="/app/all",
                                # **{
                                #     "hx-get": "/app/all",
                                #     "hx-target": "#content"
                                # }
                            )
                        ),
                        Li(
                            A(
                                "⏰ Check Next 48 Hours",
                                href="/app/next",
                                # **{
                                #     "hx-get": "/app/next",
                                #     "hx-target": "#content"
                                # }
                            )
                        ),
                        Li(
                            A(
                                "🏷️ Manage Categories",
                                href="/app/categories",
                                # **{
                                #     "hx-get": "/app/categories",
                                #     "hx-target": "#content"
                                # }
                            )
                        ),
                    )
                )
            ),
            Article(
                Header(H3("📅 Recent Activity")),
                Div(
                    "Loading recent tasks...",
                    id="recent-tasks",
                    **{                                         # type: ignore
                        "hx-get": "/api/tasks?limit=5",
                        "hx-trigger": "load",
                        "hx-swap": "innerHTML",
                        "aria-busy": "true"
                    }
                )
            ),
            **{                                                 # type: ignore
                "class": "grid",
                "style": "gap: 2rem;"
            }
        ),
        Article(
            Header(H3("🔔 System Status")),
            Div(
                P(
                    "✅ All systems operational",
                    **{                                         # type: ignore
                        "style": "color: var(--ins-color); font-weight: bold;"
                    }
                ),
                Div(
                    Button(
                        "📧 Trigger Notifications",
                        **{                                     # type: ignore
                            "hx-post": "/app/notifications/trigger",
                            "hx-target": "#notification-status",
                            "class": "contrast"
                        }
                    ),
                    Button(
                        "🔄 Refresh Status",
                        **{                                     # type: ignore
                            "onclick": "location.reload()",
                            "class": "secondary",
                            "style": "margin-left: 0.5rem;"
                        }
                    ),
                    style="margin-top: 1rem;"
                ),
                Div(id="notification-status", style="margin-top: 1rem;")
            )
        ),
        Details(
            Summary("📈 Quick Stats"),
            Div(
                id="quick-stats",
                **{                                     # type: ignore
                    "hx-get": "/api/stats/summary",
                    "hx-trigger": "toggle once",
                    "aria-busy": "true"
                },
                style="padding: 1rem;"
            )
        )
    )    
    return shell(content)
