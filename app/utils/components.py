# utils/components.py

from datetime import datetime
from fasthtml import ft
# from fasthtml.common import *
from typing import Dict, Any


def nav():
    """Main navigation component with proper navbar styling"""
    return ft.Nav(
        ft.Div(
            ft.A(
                "Task Manager",
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
                    "Home",
                    href="/app",
                    # **{
                    #     "hx-get": "/app",
                    #     "hx-target": "#content",
                    # },
                ),
            ),
            ft.Li(
                ft.A(
                    "Tasks",
                    href="/app/tasks",
                    # **{
                    #     "hx-get": "/app/tasks",
                    #     "hx-target": "#content",
                    # },
                )
            ),
            ft.Li(
                ft.A(
                    "All Tasks",
                    href="/app/all",
                    # **{
                    #     "hx-get": "/app/all",
                    #     "hx-target": "#content"
                    # }
                )
            ),
            ft.Li(
                ft.A(
                    "Categories",
                    href="/app/categories",
                    # **{"hx-get": "/app/categories", "hx-target": "#content"}
                )
            ),
            ft.Li(
                ft.A(
                    "Tags",
                    href="/app/tags",
                    # **{"hx-get": "/app/tags", "hx-target": "#content"}
                )
            ),
            ft.Li(
                ft.A(
                    "Next 48h",
                    href="/app/next",
                    # **{"hx-get": "/app/next", "hx-target": "#content"}
                )
            ),
            ft.Li(
                ft.A(
                    "Notifications",
                    href="/app/notifications",
                    # **{"hx-get": "/app/notifications", "hx-target": "#content"}
                )
            ),
            ft.Li(
                ft.A(
                    "Settings",
                    href="/app/settings",
                    # **{"hx-get": "/app/settings", "hx-target": "#content"}
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
                        "aria-label": "Toggle theme"
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
    return ft.Html(
        ft.Head(
            ft.Title("Tasks UI"),
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
                """
                // Theme management
                function getStoredTheme() {
                    return localStorage.getItem('theme') || 'dark';
                }
                
                function setTheme(theme) {
                    if (theme === 'auto') {
                        // Remove data-theme to use system preference
                        document.documentElement.removeAttribute('data-theme');
                    } else {
                        document.documentElement.setAttribute('data-theme', theme);
                    }
                    localStorage.setItem('theme', theme);
                    updateThemeToggle(theme);
                }
                
                function updateThemeToggle(theme) {
                    const toggle = document.getElementById('theme-toggle');
                    if (toggle) {
                        if (theme === 'dark') {
                            toggle.textContent = '🌙';
                            toggle.setAttribute('aria-label', 'Switch to light mode');
                        } else if (theme === 'light') {
                            toggle.textContent = '☀️';
                            toggle.setAttribute('aria-label', 'Switch to dark mode');
                        } else {
                            toggle.textContent = '🌓';
                            toggle.setAttribute('aria-label', 'Switch to manual theme');
                        }
                    }
                }
                
                function toggleTheme() {
                    const currentTheme = getStoredTheme();
                    let newTheme;
                    
                    if (currentTheme === 'dark') {
                        newTheme = 'light';
                    } else if (currentTheme === 'light') {
                        newTheme = 'auto';
                    } else {
                        newTheme = 'dark';
                    }
                    
                    setTheme(newTheme);
                }
                
                // Initialize theme on page load
                document.addEventListener('DOMContentLoaded', function() {
                    const storedTheme = getStoredTheme();
                    setTheme(storedTheme);
                });
                
                // Set initial theme immediately (before DOMContentLoaded)
                (function() {
                    const theme = getStoredTheme();
                    if (theme !== 'auto') {
                        document.documentElement.setAttribute('data-theme', theme);
                    }
                })();
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
                """
                    // HTMX event handlers
                    document.body.addEventListener('htmx:responseError', function(evt) {
                        console.error('HTMX Error:', evt.detail);
                        const errorMsg = document.createElement('div');
                        errorMsg.className = 'error-message';
                        errorMsg.textContent = 'An error occurred. Please try again.';
                        errorMsg.style.position = 'fixed';
                        errorMsg.style.top = '20px';
                        errorMsg.style.right = '20px';
                        errorMsg.style.zIndex = '9999';
                        document.body.appendChild(errorMsg);
                        setTimeout(() => errorMsg.remove(), 5000);
                    });
                    
                    document.body.addEventListener('htmx:afterSwap', function(evt) {
                        console.log('Content swapped successfully');
                        // Re-initialize any components if needed
                    });
                    
                    // Preserve theme across HTMX navigations
                    document.body.addEventListener('htmx:configRequest', function(evt) {
                        evt.detail.headers['X-Theme'] = getStoredTheme();
                    });
                """
            ),
        ),
        **{"data-theme": "dark"}  # Set dark as default         # type: ignore
    )


def task_card(task: Dict[str, Any]) -> Any:
    """Render a task as a card component"""
    task_id = task.get('id', '')
    title = task.get('title', 'Untitled')
    description = task.get('description', '')
    completed = task.get('completed', False)
    priority = task.get('priority', 'medium')
    due_date = task.get('due_date')
    category = task.get('category', {})
    tags = task.get('tags', [])
    # Format due date
    due_text = ""
    if due_date:
        try:
            due_dt = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            due_text = f"Due: {due_dt.strftime('%Y-%m-%d %H:%M')}"
        except:
            due_text = f"Due: {due_date}"
    # Task classes
    task_classes = f"task-item priority-{priority}"
    if completed:
        task_classes += " task-completed"
    # Build task content
    content = [
        ft.H4(title, style="margin-bottom: 0.5rem;"),
    ]
    if description:
        content.append(ft.P(description))
    if category.get('name'):
        content.append(ft.P(f"Category: {category['name']}", class_="category"))
    if due_text:
        content.append(ft.P(due_text, style="color: var(--muted-color); font-size: 0.9rem;"))
    if tags:
        tag_elements = [ft.Span(tag.get('name', tag), class_="tag") for tag in tags]
        content.append(ft.Div(*tag_elements, style="margin: 0.5rem 0;"))    
    # Action buttons
    if not completed:
        actions = [
            ft.Button(
                "✓ Complete",
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
            "🗑 Delete",
            **{                                                     # type: ignore
                "hx-delete": f"/api/tasks/{task_id}",
                "hx-target": "closest .task-item",
                "hx-swap": "outerHTML",
                "hx-confirm": "Are you sure you want to delete this task?",
                "class": "secondary outline",
                "style": "font-size: 0.875rem;"
            }
        )
    )
    content.append(ft.Div(*actions, class_="task-actions"))
    return ft.Article(
        *content,
        **{"class": task_classes, "id": f"task-{task_id}"}          # type: ignore
    )


def loading_spinner():
    """Simple loading indicator"""
    return ft.Div(
        "Loading...",
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
