# pages/settings.py

from fasthtml.common import *

from app.i18n import t, available_languages, get_language, set_language
from app.utils.components import (
    shell,
    form_field,
    success_message,
    error_message,
)
from app.utils.backend import BackendClient


def settings_page(backend: BackendClient):
    """Application settings and configuration page"""

    # Build language options
    current_lang = get_language()
    lang_options = []
    for code, display_name in available_languages():
        if code == current_lang:
            lang_options.append(Option(display_name, value=code, selected=True))
        else:
            lang_options.append(Option(display_name, value=code))

    content = Section(
        Hgroup(
            H2(t("settings.title")),
            P(t("settings.subtitle"))
        ),

        # ── Theme Settings ───────────────────────────────────────────
        Article(
            Header(H3(t("settings.appearance"))),
            Div(
                H4(t("settings.theme_settings")),
                P(t("settings.theme_subtitle"), style="color: var(--muted-color);"),
                Div(
                    Button(
                        t("settings.theme_dark"),
                        id="theme-dark",
                        onclick="setTheme('dark')",
                        **{"class": "outline", "style": "flex: 1;"}
                    ),
                    Button(
                        t("settings.theme_light"),
                        id="theme-light",
                        onclick="setTheme('light')",
                        **{"class": "outline", "style": "flex: 1;"}
                    ),
                    Button(
                        t("settings.theme_auto"),
                        id="theme-auto",
                        onclick="setTheme('auto')",
                        **{"class": "outline", "style": "flex: 1;"}
                    ),
                    **{"class": "grid", "style": "gap: 0.5rem; margin-top: 1rem;"}
                ),
                Div(
                    P(
                        t("settings.current_theme"),
                        Strong(id="current-theme", style="color: var(--primary);"),
                        style="margin-top: 1rem;"
                    ),
                    Small(
                        t("settings.auto_hint"),
                        style="color: var(--muted-color);"
                    )
                ),
                Script("""
                    function updateCurrentThemeDisplay() {
                        const theme = localStorage.getItem('theme') || 'dark';
                        const themeDisplay = document.getElementById('current-theme');
                        if (themeDisplay) {
                            themeDisplay.textContent = theme.charAt(0).toUpperCase() + theme.slice(1);
                        }
                        document.querySelectorAll('[id^="theme-"]').forEach(btn => {
                            btn.classList.remove('primary');
                            btn.classList.add('outline');
                        });
                        const activeBtn = document.getElementById('theme-' + theme);
                        if (activeBtn) {
                            activeBtn.classList.remove('outline');
                            activeBtn.classList.add('primary');
                        }
                    }
                    document.addEventListener('DOMContentLoaded', updateCurrentThemeDisplay);
                    const originalSetTheme = window.setTheme;
                    window.setTheme = function(theme) {
                        originalSetTheme(theme);
                        updateCurrentThemeDisplay();
                    };
                """)
            )
        ),

        Hr(),

        # ── General Settings ─────────────────────────────────────────
        Article(
            Header(H3(t("settings.general_title"))),
            Form(
                form_field(t("settings.timezone_label"), Select(
                    Option("UTC", value="UTC"),
                    Option("America/Santiago", value="America/Santiago", selected=True),
                    Option("America/New_York", value="America/New_York"),
                    Option("America/Los_Angeles", value="America/Los_Angeles"),
                    Option("Europe/London", value="Europe/London"),
                    Option("Europe/Paris", value="Europe/Paris"),
                    Option("Asia/Tokyo", value="Asia/Tokyo"),
                    Option("Asia/Shanghai", value="Asia/Shanghai"),
                    Option("Australia/Sydney", value="Australia/Sydney"),
                    name="timezone"
                )),
                form_field(t("settings.language_label"), Select(
                    *lang_options,
                    name="language"
                )),
                Button(t("settings.save_general"), type="submit", **{"class": "primary"}),
                **{
                    "hx-put": "/app/settings/general",
                    "hx-target": "#general-settings-response",
                    "hx-swap": "innerHTML"
                }
            ),
            Div(id="general-settings-response")
        ),

        Hr(),

        # ── Notification Templates ───────────────────────────────────
        Article(
            Header(
                H3(t("settings.templates_title")),
                P(t("settings.templates_subtitle"), style="color: var(--muted-color);")
            ),
            Details(
                Summary(t("settings.due_soon_template")),
                Form(
                    form_field(
                        t("settings.template_body_label"),
                        Textarea(
                            name="due_body",
                            rows="8",
                            style="width: 100%; font-family: monospace;",
                        )
                    ),
                    Small(
                        t("settings.due_soon_vars"),
                        style="color: var(--muted-color); display: block; margin-bottom: 1rem;"
                    ),
                    Button(t("settings.save_template"), type="submit", **{"class": "primary"}),
                    **{
                        "hx-put": "/app/settings/template/due_soon",
                        "hx-target": "#template-response",
                        "hx-swap": "innerHTML",
                    }
                ),
            ),
            Details(
                Summary(t("settings.overdue_template")),
                Form(
                    form_field(
                        t("settings.template_body_label"),
                        Textarea(
                            name="overdue_body",
                            rows="8",
                            style="width: 100%; font-family: monospace;",
                        )
                    ),
                    Small(
                        t("settings.overdue_vars"),
                        style="color: var(--muted-color); display: block; margin-bottom: 1rem;"
                    ),
                    Button(t("settings.save_template"), type="submit", **{"class": "primary"}),
                    **{
                        "hx-put": "/app/settings/template/overdue",
                        "hx-target": "#template-response",
                        "hx-swap": "innerHTML",
                    }
                ),
            ),
            Div(id="template-response")
        ),

        Hr(),

        # ── System Information ───────────────────────────────────────
        Article(
            Header(H3(t("settings.system_info"))),
            Div(
                t("settings.loading_system_info"),
                id="system-info",
                **{
                    "hx-get": "/app/settings/system-info",
                    "hx-trigger": "load",
                    "hx-swap": "innerHTML",
                    "aria-busy": "true"
                }
            )
        ),

        Hr(),

        # ── Danger Zone ──────────────────────────────────────────────
        Article(
            Header(
                Strong(t("settings.danger_zone"), style="color: var(--del-color);")
            ),
            P(
                t("settings.danger_warning"),
                style="color: var(--del-color);"
            ),
            Button(
                t("settings.reset_button"),
                **{
                    "hx-post": "/app/settings/reset",
                    "hx-confirm": t("settings.reset_confirm"),
                    "hx-target": "#danger-response",
                    "class": "contrast"
                }
            ),
            Div(id="danger-response", style="margin-top: 1rem;"),
            **{
                "style": "border: 2px solid var(--del-color); border-radius: var(--border-radius); padding: var(--spacing); background-color: color-mix(in srgb, var(--del-color) 5%, transparent);"
            }
        )
    )

    return shell(content)


async def handle_general_settings(request, backend: BackendClient):
    """Handle general settings form submission"""
    try:
        form_data = await request.form()
        new_lang = form_data.get("language", "en")
        settings_data = {
            "timezone": form_data.get("timezone", "America/Santiago"),
            "language": new_lang,
        }
        await backend.update_settings(settings_data)
        # Hot-reload the language for subsequent requests
        set_language(new_lang)
        return success_message(t("settings.general_saved"))
    except Exception as e:
        return error_message(t("errors.save_settings_failed", error=str(e)))


async def handle_template_settings(
    request, backend: BackendClient, template_type: str
):
    """Handle notification template form submission"""
    try:
        form_data = await request.form()
        # The form field name matches the template key suffix
        body_field = f"{template_type}_body"
        markdown = form_data.get(body_field, "").strip()

        if not markdown:
            return error_message(t("errors.template_body_empty"))

        await backend.update_notification_template(template_type, markdown)
        return success_message(
            t("settings.template_saved", type=template_type.replace('_', ' ').title())
        )
    except Exception as e:
        return error_message(t("errors.save_template_failed", error=str(e)))


async def render_system_info(backend: BackendClient):
    """Render system information using backend health check and views"""
    try:
        # Get backend health
        try:
            health = await backend.health_check()
        except Exception:
            health = {"status": "unreachable", "version": "unknown"}

        # Get current settings
        try:
            settings = await backend.get_settings()
        except Exception:
            settings = {}

        # Get stats from views
        try:
            status_summary = await backend.get_views_summary('status-summary')
            pending = sum(s['count'] for s in status_summary if s['key'] == 'pending')
            completed = sum(s['count'] for s in status_summary if s['key'] == 'completed')
            total = pending + completed
        except Exception:
            pending = completed = total = 0

        try:
            categories = await backend.get_categories()
            tags = await backend.get_tags()
        except Exception:
            categories = []
            tags = []

        notif_enabled = settings.get('notifications_enabled')
        info_cards = [
            (t("settings.info_backend_status"), health.get("status", "unknown"), "var(--ins-color)"),
            (t("settings.info_api_version"), health.get("version", "unknown"), "var(--primary)"),
            (t("settings.info_total_tasks"), str(total), "var(--primary)"),
            (t("settings.info_active_tasks"), str(pending), "var(--ins-color)"),
            (t("settings.info_completed"), str(completed), "var(--muted-color)"),
            (t("settings.info_categories"), str(len(categories)), "var(--primary)"),
            (t("settings.info_tags"), str(len(tags)), "var(--primary)"),
            (
                t("settings.info_notifications"),
                t("notifications.enabled") if notif_enabled else t("notifications.disabled"),
                "var(--ins-color)" if notif_enabled else "var(--muted-color)"
            ),
            (t("settings.info_timezone"), settings.get('timezone', 'UTC'), "var(--primary)"),
            (t("settings.info_language"), settings.get('language', 'en'), "var(--primary)"),
        ]

        info_elements = []
        for label, value, color in info_cards:
            info_elements.append(
                Div(
                    Small(
                        label,
                        style="display: block; color: var(--muted-color); margin-bottom: 0.25rem;"
                    ),
                    Strong(value, style=f"color: {color}; font-size: 1.1rem;"),
                    style="padding: 1rem; background-color: var(--card-background-color); border-radius: var(--border-radius); border: 1px solid var(--muted-border-color);"
                )
            )

        return Div(
            *info_elements,
            **{
                "class": "grid",
                "style": "gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));"
            }
        )
    except Exception as e:
        return error_message(t("errors.loading_system_info", error=str(e)))


async def reset_settings(backend: BackendClient):
    """Reset all settings to defaults"""
    try:
        default_settings = {
            "timezone": "America/Santiago",
            "theme": "light",
            "notifications_enabled": True,
            "near_due_hours": 24,
            "scheduler_interval_seconds": 60,
            "ntfy_topics": "",
            "language": "en",
        }
        await backend.update_settings(default_settings)
        set_language("en")
        return success_message(t("settings.reset_success"))
    except Exception as e:
        return error_message(t("errors.reset_settings_failed", error=str(e)))
