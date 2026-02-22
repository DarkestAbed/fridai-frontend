# pages/home.py

from fasthtml.common import *

from app.i18n import t
from app.utils.components import shell


def home_page():
    """Home page with dashboard overview"""
    content = Section(
        Hgroup(
            H1(t("home.title")),
            P(t("home.subtitle"))
        ),
        Div(
            Article(
                Header(H3(t("home.quick_actions"))),
                Nav(
                    Ul(
                        Li(A(t("home.add_new_task"), href="/app/tasks")),
                        Li(A(t("home.view_all_tasks"), href="/app/all")),
                        Li(A(t("home.check_next_48h"), href="/app/next")),
                        Li(A(t("home.manage_categories"), href="/app/categories")),
                    )
                )
            ),
            Article(
                Header(H3(t("home.recent_activity"))),
                Div(
                    t("home.loading_recent"),
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
            Header(H3(t("home.system_status"))),
            Div(
                P(
                    t("home.all_systems_operational"),
                    **{                                         # type: ignore
                        "style": "color: var(--ins-color); font-weight: bold;"
                    }
                ),
                Div(
                    Button(
                        t("home.trigger_notifications"),
                        **{                                     # type: ignore
                            "hx-post": "/app/notifications/trigger",
                            "hx-target": "#notification-status",
                            "class": "contrast"
                        }
                    ),
                    Button(
                        t("home.refresh_status"),
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
            Summary(t("home.quick_stats")),
            Div(
                id="quick-stats",
                **{                                     # type: ignore
                    "hx-get": "/app/stats",
                    "hx-trigger": "toggle once",
                    "aria-busy": "true"
                },
                style="padding: 1rem;"
            )
        )
    )
    return shell(content)
