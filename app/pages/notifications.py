# pages/notifications.py

from datetime import datetime
from fasthtml.common import *

from app.i18n import t
from app.utils.components import shell, success_message, error_message
from app.utils.backend import BackendClient


def notifications_page(backend: BackendClient):
    """Notifications and cron management page"""

    # Manual trigger section
    trigger_section = Div(
        H3(t("notifications.manual_trigger")),
        P(t("notifications.manual_trigger_subtitle")),
        Div(
            Button(
                t("notifications.send_due_notifications"),
                **{                                             # type: ignore
                    "hx-post": "/app/notifications/trigger",
                    "hx-target": "#trigger-response",
                    "hx-swap": "innerHTML",
                }
            ),
            Button(
                t("notifications.send_test"),
                **{                                             # type: ignore
                    "hx-post": "/app/notifications/test-ntfy",
                    "hx-target": "#trigger-response",
                    "hx-swap": "innerHTML",
                    "class": "secondary",
                    "style": "margin-left: 0.5rem;",
                }
            ),
            style="display: flex; gap: 0.5rem; flex-wrap: wrap;"
        ),
        Div(id="trigger-response", style="margin-top: 1rem;"),
        **{"class": "form-section"}
    )

    # Notification settings (real backend fields)
    settings_section = Div(
        H3(t("notifications.settings_title")),
        Form(
            Fieldset(
                Label(
                    Input(
                        type="checkbox",
                        name="notifications_enabled",
                        checked=True,
                        role="switch",
                    ),
                    t("notifications.enable_label")
                ),
            ),
            Div(
                Div(
                    Label(t("notifications.lead_time_label")),
                    Input(
                        type="number",
                        name="near_due_hours",
                        value="24",
                        min="1",
                        max="168",
                    ),
                ),
                Div(
                    Label(t("notifications.check_interval_label")),
                    Input(
                        type="number",
                        name="scheduler_interval_seconds",
                        value="60",
                        min="10",
                        max="86400",
                    ),
                ),
                **{"class": "grid"}                             # type: ignore
            ),
            Div(
                Label(t("notifications.ntfy_topics_label")),
                Textarea(
                    name="ntfy_topics",
                    rows="3",
                    placeholder=t("notifications.ntfy_topics_placeholder"),
                ),
                style="margin-bottom: 1rem;"
            ),
            Button(t("notifications.save_settings"), type="submit"),
            **{                                                 # type: ignore
                "hx-put": "/app/notifications/settings",
                "hx-target": "#settings-response",
                "hx-swap": "innerHTML",
            }
        ),
        Div(id="settings-response"),
        **{"class": "form-section"}
    )

    content = Section(
        H2(t("notifications.title")),
        P(t("notifications.subtitle")),
        trigger_section,
        Hr(),
        settings_section,
        Hr(),
        H3(t("notifications.history_title")),
        Div(
            t("notifications.loading_logs"),
            id="notification-logs",
            **{                                                 # type: ignore
                "hx-get": "/api/notifications/logs",
                "hx-trigger": "load",
                "hx-swap": "innerHTML",
            }
        ),
        Hr(),
        H3(t("notifications.system_status")),
        Div(
            t("notifications.loading_status"),
            id="system-status",
            **{                                                 # type: ignore
                "hx-get": "/app/notifications/status",
                "hx-trigger": "load",
                "hx-swap": "innerHTML",
            }
        ),
    )

    return shell(content)


async def trigger_notifications(backend: BackendClient):
    """Manually trigger notifications"""
    try:
        result = await backend.trigger_notifications(mode="both")
        sent = result.get('sent', 0)
        if sent > 0:
            return success_message(
                t("notifications.sent_success", count=sent)
            )
        return success_message(t("empty_states.no_notifications_needed"))
    except Exception as e:
        return error_message(t("errors.trigger_notifications_failed", error=str(e)))


async def test_ntfy_config(backend: BackendClient):
    """Test ntfy notification delivery"""
    try:
        result = await backend.test_notification()
        destinations = result.get('destinations', [])
        if destinations:
            return success_message(
                t("notifications.test_sent_success", count=len(destinations))
            )
        return error_message(t("errors.no_ntfy_topics"))
    except Exception as e:
        return error_message(t("errors.notification_test_failed", error=str(e)))


async def handle_notification_settings(request, backend: BackendClient):
    """Handle notification settings form submission"""
    try:
        form_data = await request.form()
        settings = {
            "notifications_enabled": form_data.get("notifications_enabled") is not None,
            "near_due_hours": int(form_data.get("near_due_hours", 24)),
            "scheduler_interval_seconds": int(
                form_data.get("scheduler_interval_seconds", 60)
            ),
            "ntfy_topics": form_data.get("ntfy_topics", "").strip(),
        }
        await backend.update_settings(settings)
        return success_message(t("notifications.settings_saved"))
    except Exception as e:
        return error_message(t("errors.save_settings_failed", error=str(e)))


async def render_notification_logs(backend: BackendClient):
    """Render notification history logs"""
    try:
        logs = await backend.get_notification_logs(limit=50)

        if not logs:
            return P(t("empty_states.no_notification_logs"))

        log_elements = []
        for log in logs:
            sent_at = log.get('sent_at', '')
            try:
                dt = datetime.fromisoformat(
                    str(sent_at).replace('Z', '+00:00')
                )
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                formatted_time = str(sent_at)

            kind = log.get('kind', 'unknown')
            destination = log.get('destination', '')

            log_elements.append(
                Div(
                    Div(
                        Strong(formatted_time),
                        Span(
                            kind.upper(),
                            style="background-color: var(--secondary); color: var(--secondary-inverse); padding: 0.2rem 0.5rem; border-radius: 3px; font-size: 0.8rem; margin-left: 1rem;"
                        )
                    ),
                    P(
                        t("notifications.destination_prefix") + " " + destination,
                        style="color: var(--muted-color); font-size: 0.9rem;"
                    ),
                    style="border-bottom: 1px solid var(--muted-border-color); padding: 1rem 0;"
                )
            )

        return Div(
            P(t("notifications.showing_logs", count=len(log_elements))),
            *log_elements
        )

    except Exception as e:
        return error_message(t("errors.loading_notification_logs", error=str(e)))


async def render_system_status(backend: BackendClient):
    """Render system status information"""
    try:
        settings = await backend.get_settings()
        notifications_enabled = settings.get('notifications_enabled', False)

        try:
            pending_tasks = await backend.get_tasks(status='pending')
            due_soon = await backend.get_next_tasks(24)
        except Exception:
            pending_tasks = []
            due_soon = []

        status_items = [
            Div(
                Strong(t("notifications.notifications_label") + " "),
                Span(
                    t("notifications.enabled") if notifications_enabled else t("notifications.disabled"),
                    style=f"color: {'var(--ins-color)' if notifications_enabled else 'var(--del-color)'};"
                )
            ),
            Div(
                Strong(t("notifications.check_interval_label_status") + " "),
                Span(t("notifications.check_interval_value", seconds=settings.get('scheduler_interval_seconds', 60)))
            ),
            Div(
                Strong(t("notifications.active_tasks_label") + " "),
                Span(str(len(pending_tasks)))
            ),
            Div(
                Strong(t("notifications.due_in_24h_label") + " "),
                Span(
                    str(len(due_soon)),
                    style=f"color: {'var(--del-color)' if len(due_soon) > 5 else 'var(--ins-color)'};"
                )
            )
        ]
        return Div(
            *status_items,
            style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;"
        )
    except Exception as e:
        return error_message(t("errors.loading_system_status", error=str(e)))
