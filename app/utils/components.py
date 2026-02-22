# utils/components.py

from datetime import datetime
from fasthtml import ft
from typing import Dict, Any, Optional

from app.i18n import t


def nav():
    """Main navigation component with proper navbar styling"""
    return ft.Nav(
        ft.Div(
            ft.A(
                t("nav.brand"),
                href="/app",
                **{
                    "class": "contrast",
                    "style": "font-weight: bold; font-size: 1.2rem;"
                }
            ),
            style="flex: 1;"
        ),
        ft.Ul(
            ft.Li(
                ft.A(
                    t("nav.home"),
                    href="/app",
                ),
            ),
            ft.Li(
                ft.A(
                    t("nav.tasks"),
                    href="/app/tasks",
                )
            ),
            ft.Li(
                ft.A(
                    t("nav.all_tasks"),
                    href="/app/all",
                )
            ),
            ft.Li(
                ft.A(
                    t("nav.categories"),
                    href="/app/categories",
                )
            ),
            ft.Li(
                ft.A(
                    t("nav.tags"),
                    href="/app/tags",
                )
            ),
            ft.Li(
                ft.A(
                    t("nav.next_48h"),
                    href="/app/next",
                )
            ),
            ft.Li(
                ft.A(
                    t("nav.notifications"),
                    href="/app/notifications",
                )
            ),
            ft.Li(
                ft.A(
                    t("nav.settings"),
                    href="/app/settings",
                )
            ),
            ft.Li(
                ft.Button(
                    "🌙",
                    id="theme-toggle",
                    **{                                                 # type: ignore
                        "class": "contrast",
                        "style": "padding: 0.5rem; min-width: auto;",
                        "onclick": "toggleTheme()",
                        "aria-label": t("nav.theme_toggle_label")
                    }
                )
            )
        ),
        **{                                                             # type: ignore
            "class": "container-fluid",
            "style": """
                        display: flex;
                        align-items: center;
                        padding: 1rem 2rem;
                        background-color: var(--card-background-color);
                        border-bottom: 1px solid var(--muted-border-color)
                    ;""",
        }
    )


def shell(content):
    """Main page shell with navigation, PicoCSS, and dark mode support"""
    htmx = ft.Script(src="https://unpkg.com/htmx.org@1.9.12")
    pico = ft.Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css")

    # Pre-render JS strings from i18n
    js_switch_to_light = t("nav.switch_to_light")
    js_switch_to_dark = t("nav.switch_to_dark")
    js_switch_to_manual = t("nav.switch_to_manual")
    js_htmx_error = t("errors.htmx_error")

    return ft.Html(
        ft.Head(
            ft.Title(t("shared.app_title")),
            ft.Meta(charset="utf-8"),
            ft.Meta(
                name="viewport",
                content="width=device-width, initial-scale=1"
            ),
            pico,
            htmx,
            ft.Style(
                """
                /* Custom styles on top of PicoCSS */
                :root {
                    --spacing: 1rem;
                }

                /* Navigation styles */
                nav ul {
                    list-style: none;
                    padding: 0;
                    margin: 0;
                    display: flex;
                    gap: 1rem;
                    align-items: center;
                }

                nav ul li {
                    margin: 0;
                }

                nav ul li a {
                    text-decoration: none;
                    padding: 0.5rem 1rem;
                    border-radius: var(--border-radius);
                    transition: background-color 0.2s;
                }

                nav ul li a:hover {
                    background-color: var(--secondary-hover);
                }

                /* Task card styles */
                .task-item {
                    border: 1px solid var(--muted-border-color);
                    padding: var(--spacing);
                    margin: 0.5rem 0;
                    border-radius: var(--border-radius);
                    background-color: var(--card-background-color);
                    transition: box-shadow 0.2s;
                }

                .task-item:hover {
                    box-shadow: var(--card-box-shadow);
                }

                .task-completed {
                    opacity: 0.6;
                }

                .task-completed h4 {
                    text-decoration: line-through;
                }

                .task-actions {
                    margin-top: var(--spacing);
                    display: flex;
                    gap: 0.5rem;
                }

                .task-actions button {
                    font-size: 0.875rem;
                    padding: 0.25rem 0.75rem;
                }

                /* Priority indicators */
                .priority-high {
                    border-left: 4px solid var(--del-color);
                }

                .priority-medium {
                    border-left: 4px solid var(--mark-color);
                }

                .priority-low {
                    border-left: 4px solid var(--ins-color);
                }

                /* Tags and categories */
                .tag {
                    background-color: var(--secondary);
                    color: var(--secondary-inverse);
                    padding: 0.2rem 0.5rem;
                    border-radius: var(--border-radius);
                    font-size: 0.8rem;
                    margin: 0.1rem;
                    display: inline-block;
                }

                .category {
                    color: var(--muted-color);
                    font-style: italic;
                }

                /* Form sections */
                .form-section {
                    background-color: var(--card-background-color);
                    padding: var(--spacing);
                    margin: var(--spacing) 0;
                    border-radius: var(--border-radius);
                    border: 1px solid var(--muted-border-color);
                }

                /* Messages */
                .error-message {
                    color: var(--del-color);
                    background-color: var(--del-color);
                    background-color: color-mix(in srgb, var(--del-color) 10%, transparent);
                    padding: var(--spacing);
                    border-radius: var(--border-radius);
                    margin: 0.5rem 0;
                    border: 1px solid var(--del-color);
                }

                .success-message {
                    color: var(--ins-color);
                    background-color: color-mix(in srgb, var(--ins-color) 10%, transparent);
                    padding: var(--spacing);
                    border-radius: var(--border-radius);
                    margin: 0.5rem 0;
                    border: 1px solid var(--ins-color);
                }

                /* Category and tag cards */
                .category-card, .tag-card {
                    background-color: var(--card-background-color);
                    border: 1px solid var(--muted-border-color);
                    padding: var(--spacing);
                    margin: 0.5rem 0;
                    border-radius: var(--border-radius);
                }

                /* Container adjustments */
                #content {
                    padding: 2rem;
                    max-width: 1200px;
                    margin: 0 auto;
                }

                /* Responsive adjustments */
                @media (max-width: 768px) {
                    nav {
                        flex-direction: column;
                        align-items: flex-start;
                    }

                    nav ul {
                        flex-wrap: wrap;
                        margin-top: 1rem;
                    }

                    nav ul li a {
                        padding: 0.25rem 0.5rem;
                        font-size: 0.9rem;
                    }
                }

                /* Loading spinner */
                .loading {
                    text-align: center;
                    padding: 2rem;
                    color: var(--muted-color);
                }

                /* Grid layouts */
                .grid-2 {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: var(--spacing);
                }

                /* Theme toggle animation */
                #theme-toggle {
                    transition: transform 0.3s;
                }

                #theme-toggle:hover {
                    transform: rotate(20deg);
                }
            """
            ),
            ft.Script(
                f"""
                // Theme management
                function getStoredTheme() {{
                    return localStorage.getItem('theme') || 'dark';
                }}

                function setTheme(theme) {{
                    if (theme === 'auto') {{
                        // Remove data-theme to use system preference
                        document.documentElement.removeAttribute('data-theme');
                    }} else {{
                        document.documentElement.setAttribute('data-theme', theme);
                    }}
                    localStorage.setItem('theme', theme);
                    updateThemeToggle(theme);
                }}

                function updateThemeToggle(theme) {{
                    const toggle = document.getElementById('theme-toggle');
                    if (toggle) {{
                        if (theme === 'dark') {{
                            toggle.textContent = '🌙';
                            toggle.setAttribute('aria-label', '{js_switch_to_light}');
                        }} else if (theme === 'light') {{
                            toggle.textContent = '☀️';
                            toggle.setAttribute('aria-label', '{js_switch_to_dark}');
                        }} else {{
                            toggle.textContent = '🌓';
                            toggle.setAttribute('aria-label', '{js_switch_to_manual}');
                        }}
                    }}
                }}

                function toggleTheme() {{
                    const currentTheme = getStoredTheme();
                    let newTheme;

                    if (currentTheme === 'dark') {{
                        newTheme = 'light';
                    }} else if (currentTheme === 'light') {{
                        newTheme = 'auto';
                    }} else {{
                        newTheme = 'dark';
                    }}

                    setTheme(newTheme);
                }}

                // Initialize theme on page load
                document.addEventListener('DOMContentLoaded', function() {{
                    const storedTheme = getStoredTheme();
                    setTheme(storedTheme);
                }});

                // Set initial theme immediately (before DOMContentLoaded)
                (function() {{
                    const theme = getStoredTheme();
                    if (theme !== 'auto') {{
                        document.documentElement.setAttribute('data-theme', theme);
                    }}
                }})();
                """
            ),
        ),
        ft.Body(
            nav(),
            ft.Main(
                ft.Div(content, id="content"),
                **{"class": "container-fluid"}          # type: ignore
            ),
            ft.Script(
                f"""
                    // HTMX event handlers
                    document.body.addEventListener('htmx:responseError', function(evt) {{
                        console.error('HTMX Error:', evt.detail);
                        const errorMsg = document.createElement('div');
                        errorMsg.className = 'error-message';
                        errorMsg.textContent = '{js_htmx_error}';
                        errorMsg.style.position = 'fixed';
                        errorMsg.style.top = '20px';
                        errorMsg.style.right = '20px';
                        errorMsg.style.zIndex = '9999';
                        document.body.appendChild(errorMsg);
                        setTimeout(() => errorMsg.remove(), 5000);
                    }});

                    document.body.addEventListener('htmx:afterSwap', function(evt) {{
                        evt.detail.elt.removeAttribute('aria-busy');
                    }});

                    // Preserve theme across HTMX navigations
                    document.body.addEventListener('htmx:configRequest', function(evt) {{
                        evt.detail.headers['X-Theme'] = getStoredTheme();
                    }});
                """
            ),
        ),
        **{"data-theme": "dark"}  # Set dark as default         # type: ignore
    )


def task_card(
    task: Dict[str, Any],
    category_map: Optional[Dict[int, str]] = None,
    tag_map: Optional[Dict[int, str]] = None,
) -> Any:
    """Render a task as a card component.

    Args:
        task: Task dict from backend (fields: id, title, description, status,
              due_at, category_id, tag_ids).
        category_map: Optional {id: name} lookup for categories.
        tag_map: Optional {id: name} lookup for tags.
    """
    task_id = task.get('id', '')
    title = task.get('title', t("task_card.untitled"))
    description = task.get('description', '')
    is_completed = task.get('status') == 'completed'
    due_at = task.get('due_at')
    category_id = task.get('category_id')
    tag_ids = task.get('tag_ids', [])
    # Format due date
    due_text = ""
    if due_at:
        try:
            due_dt = datetime.fromisoformat(str(due_at).replace('Z', '+00:00'))
            due_text = f"{t('shared.due_prefix')} {due_dt.strftime('%Y-%m-%d %H:%M')}"
        except Exception:
            due_text = f"{t('shared.due_prefix')} {due_at}"
    # Task classes
    task_classes = "task-item"
    if is_completed:
        task_classes += " task-completed"
    # Build task content
    content = [
        ft.H4(title, style="margin-bottom: 0.5rem;"),
    ]
    if description:
        content.append(ft.P(description))
    if category_id is not None:
        cat_name = (
            category_map.get(category_id, f"#{category_id}")
            if category_map
            else f"#{category_id}"
        )
        content.append(ft.P(f"{t('shared.category_prefix')} {cat_name}", **{"class": "category"}))
    if due_text:
        content.append(ft.P(due_text, style="color: var(--muted-color); font-size: 0.9rem;"))
    if tag_ids:
        if tag_map:
            tag_elements = [
                ft.Span(tag_map.get(tid, f"#{tid}"), **{"class": "tag"})
                for tid in tag_ids
            ]
        else:
            tag_elements = [
                ft.Span(f"#{tid}", **{"class": "tag"}) for tid in tag_ids
            ]
        content.append(ft.Div(*tag_elements, style="margin: 0.5rem 0;"))
    # Action buttons
    if not is_completed:
        actions = [
            ft.Button(
                t("task_card.complete_button"),
                **{                                                 # type: ignore
                    "hx-put": f"/api/tasks/{task_id}/complete",
                    "hx-target": "closest .task-item",
                    "hx-swap": "outerHTML",
                    "class": "outline",
                    "style": "font-size: 0.875rem;"
                }
            ),
        ]
    else:
        actions = []
    actions.append(
        ft.Button(
            t("shared.delete"),
            **{                                                     # type: ignore
                "hx-delete": f"/api/tasks/{task_id}",
                "hx-target": "closest .task-item",
                "hx-swap": "outerHTML",
                "hx-confirm": t("task_card.delete_confirm"),
                "class": "secondary outline",
                "style": "font-size: 0.875rem;"
            }
        )
    )
    content.append(ft.Div(*actions, **{"class": "task-actions"}))
    return ft.Article(
        *content,
        **{"class": task_classes, "id": f"task-{task_id}"}          # type: ignore
    )


def loading_spinner():
    """Simple loading indicator"""
    return ft.Div(
        t("shared.loading"),
        **{"class": "loading", "aria-busy": "true"}                 # type: ignore
    )


def error_message(message: str):
    """Error message component"""
    return ft.Div(
        message,
        **{                                         # type: ignore
            "class": "error-message",
            "role": "alert"
        }
    )


def success_message(message: str):
    """Success message component"""
    return ft.Div(
        message,
        **{                                         # type: ignore
            "class": "success-message",
            "role": "status"
        }
    )


def form_field(label: str, input_element, required: bool = False):
    """Standardized form field wrapper"""
    label_text = label + (" *" if required else "")
    return ft.Div(
        ft.Label(label_text, **{"for": input_element.attrs.get('name', '')}),
        input_element,
        style="margin-bottom: var(--spacing);"
    )
