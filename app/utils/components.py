# utils/components.py

from fasthtml.common import *
from datetime import datetime
from typing import Dict, Any


def nav():
    """Main navigation component"""
    return Nav(
        Ul(
            Li(
                A(
                    "Home",
                    href="/app",
                    **{"hx-get": "/app", "hx-target": "#content"},
                ),
            ),
            Li(
                A(
                    "Tasks",
                    href="/app/tasks",
                    **{"hx-get": "/app/tasks", "hx-target": "#content"},
                ),
            ),
            Li(
                A(
                    "All Tasks",
                    href="/app/all",
                    **{"hx-get": "/app/all", "hx-target": "#content"},
                ),
            ),
            Li(
                A(
                    "Categories",
                    href="/app/categories",
                    **{"hx-get": "/app/categories", "hx-target": "#content"},
                ),
            ),
            Li(
                A(
                    "Tags",
                    href="/app/tags",
                    **{"hx-get": "/app/tags", "hx-target": "#content"},
                ),
            ),
            Li(
                A(
                    "Next 48h",
                    href="/app/next",
                    **{"hx-get": "/app/next", "hx-target": "#content"},
                ),
            ),
            Li(
                A(
                    "Notifications",
                    href="/app/notifications",
                    **{"hx-get": "/app/notifications", "hx-target": "#content"},
                ),
            ),
            Li(
                A(
                    "Settings",
                    href="/app/settings",
                    **{"hx-get": "/app/settings", "hx-target": "#content"},
                ),
            ),
        ),
        style="margin-bottom: 2rem;",
    )


def shell(content):
    """Main page shell with navigation and HTMX setup"""
    htmx = Script(src="https://unpkg.com/htmx.org@1.9.12")
    sakura = Link(rel="stylesheet", href="https://unpkg.com/sakura.css/css/sakura.css")
    return Html(
        Head(
            Title("Tasks UI"),
            sakura,
            htmx,
            # Link(rel="manifest", href="/static/manifest.webmanifest"),
            Style("""
                .task-item {
                    border: 1px solid #ddd;
                    padding: 1rem;
                    margin: 0.5rem 0;
                    border-radius: 4px;
                    background-color: #f9f9f9;
                }
                .task-completed {
                    opacity: 0.6;
                    text-decoration: line-through;
                }
                .task-actions {
                    margin-top: 0.5rem;
                }
                .task-actions button {
                    margin-right: 0.5rem;
                    font-size: 0.8rem;
                }
                .tag {
                    background-color: #e0e0e0;
                    color: #333;
                    padding: 0.2rem 0.5rem;
                    border-radius: 3px;
                    font-size: 0.8rem;
                    margin: 0.1rem;
                    display: inline-block;
                }
                .category {
                    color: #666;
                    font-style: italic;
                }
                .priority-high { border-left: 4px solid #ff4444; }
                .priority-medium { border-left: 4px solid #ffaa00; }
                .priority-low { border-left: 4px solid #44ff44; }
                .form-section {
                    background-color: #f5f5f5;
                    padding: 1rem;
                    margin: 1rem 0;
                    border-radius: 4px;
                }
                .error-message {
                    color: #ff4444;
                    background-color: #ffe6e6;
                    padding: 0.5rem;
                    border-radius: 4px;
                    margin: 0.5rem 0;
                }
                .success-message {
                    color: #44aa44;
                    background-color: #e6ffe6;
                    padding: 0.5rem;
                    border-radius: 4px;
                    margin: 0.5rem 0;
                }
            """)
        ),
        Body(
            nav(),
            Div(content, id="content"),
            Script("""
                // HTMX event handlers
                document.body.addEventListener('htmx:responseError', function(evt) {
                    console.error('HTMX Error:', evt.detail);
                    alert('An error occurred. Please try again.');
                });
                document.body.addEventListener('htmx:afterSwap', function(evt) {
                    console.log('Content swapped successfully');
                });
            """
            )
        )
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
        H4(title, style="margin-bottom: 0.5rem;"),
    ]
    if description:
        content.append(P(description))
    if category.get('name'):
        content.append(P(f"Category: {category['name']}", class_="category"))
    if due_text:
        content.append(P(due_text, style="color: #666; font-size: 0.9rem;"))
    if tags:
        tag_elements = [Span(tag.get('name', tag), class_="tag") for tag in tags]
        content.append(Div(*tag_elements, style="margin: 0.5rem 0;"))
    # Action buttons
    if not completed:
        actions = [
            Button(
                "Complete", 
                **{                                                     # type: ignore
                    "hx-put": f"/api/tasks/{task_id}/complete",
                    "hx-target": "closest .task-item",
                    "hx-swap": "outerHTML",
                }           
            ),
        ]
    else:
        actions = []
    actions.append(
        Button(
            "Delete", 
            **{                                                         # type: ignore
                "hx-delete": f"/api/tasks/{task_id}",
                "hx-target": "closest .task-item",
                "hx-swap": "outerHTML",
                "hx-confirm": "Are you sure you want to delete this task?"
            },
        )
    )    
    content.append(Div(*actions, class_="task-actions"))
    return Div(*content, class_=task_classes, id=f"task-{task_id}")


def loading_spinner():
    """Simple loading indicator"""
    return Div(
        "Loading...", 
        style="text-align: center; padding: 2rem; color: #666;"
    )


def error_message(message: str):
    """Error message component"""
    return Div(message, class_="error-message")


def success_message(message: str):
    """Success message component"""
    return Div(message, class_="success-message")


def form_field(label: str, input_element, required: bool = False):
    """Standardized form field wrapper"""
    label_text = label + (" *" if required else "")
    return Div(
        Label(label_text),
        input_element,
        style="margin-bottom: 1rem;"
    )
