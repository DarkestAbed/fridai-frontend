# pages/tasks.py

from fastapi import Request
from fasthtml.common import *

from app.i18n import t
from app.utils.components import (
    shell,
    form_field,
    error_message,
    success_message,
)
from app.utils.backend import BackendClient


def tasks_page(backend: BackendClient):
    """Tasks page with creation form and active tasks list"""
    # Task creation form
    form = Article(
        Header(H3(t("tasks.add_new_task"))),
        Form(
            Div(
                form_field(
                    t("tasks.field_title"),
                    Input(
                        type="text",
                        name="title",
                        required=True,
                        placeholder=t("tasks.field_title_placeholder")
                    ),
                    required=True,
                ),
                form_field(
                    t("tasks.field_description"),
                    Textarea(
                        name="description",
                        rows="3",
                        placeholder=t("tasks.field_description_placeholder")
                    )
                ),
                **{"class": "grid"}
            ),

            form_field(
                t("tasks.field_due_date"),
                Input(**{"type": "datetime-local", "name": "due_date", "step": "60"}),
            ),

            Div(
                form_field(
                    t("tasks.field_category"),
                    Input(
                        type="text",
                        name="category",
                        placeholder=t("tasks.field_category_placeholder")
                    ),
                ),
                form_field(
                    t("tasks.field_tags"),
                    Input(
                        type="text",
                        name="tags",
                        placeholder=t("tasks.field_tags_placeholder"),
                    ),
                ),
                **{"class": "grid"}
            ),

            Button(
                t("tasks.create_button"),
                type="submit",
                **{"class": "primary", "style": "width: 100%;"}
            ),
            **{
                "hx-post": "/app/tasks",
                "hx-target": "#task-form-response",
                "hx-swap": "innerHTML",
            },
        ),
        Div(id="task-form-response"),
    )

    content = Section(
        Hgroup(
            H2(t("tasks.title")),
            P(t("tasks.subtitle"))
        ),

        form,

        Hr(),

        Article(
            Header(
                H3(t("tasks.active_tasks")),
                P(
                    t("tasks.active_tasks_subtitle"),
                    style="color: var(--muted-color); margin: 0;"
                )
            ),
            Div(
                t("tasks.loading_active"),
                id="active-tasks",
                **{
                    "hx-get": "/api/tasks?status=pending",
                    "hx-trigger": "load, refresh",
                    "hx-swap": "innerHTML",
                    "aria-busy": "true"
                },
            ),
        ),

        Hr(),

        Details(
            Summary(t("tasks.recently_completed")),
            Div(
                t("tasks.loading_completed"),
                id="completed-tasks",
                **{
                    "hx-get": "/api/tasks?status=completed&limit=5",
                    "hx-trigger": "toggle once",
                    "hx-swap": "innerHTML",
                    "aria-busy": "true"
                }
            )
        ),

    )

    return shell(content)


async def handle_task_form(request: Request, backend: BackendClient):
    """Handle task creation form submission"""
    try:
        form_data = await request.form()

        # Extract form data
        task_data = {
            "title": form_data.get("title", "").strip(),
            "description": form_data.get("description", "").strip(),
        }

        # Handle due date (backend field is due_at)
        due_date = form_data.get("due_date", "").strip()
        if due_date:
            task_data["due_at"] = due_date

        # Handle category
        category_name = form_data.get("category", "").strip()
        if category_name:
            # Try to find existing category or create new one
            try:
                categories = await backend.get_categories()
                category = next(
                    (
                        c
                        for c in categories
                        if c["name"].lower() == category_name.lower()
                    ),
                    None
                )
                if not category:
                    category = await backend.create_category(
                        {"name": category_name}
                    )
                task_data["category_id"] = category["id"]
            except Exception as e:
                print(f"Category handling error: {e}")

        # Handle tags
        tags_input = form_data.get("tags", "").strip()
        if tags_input:
            tag_names = [
                tag.strip() for tag in tags_input.split(",") if tag.strip()
            ]
            tag_ids = []

            try:
                existing_tags = await backend.get_tags()
                for tag_name in tag_names:
                    tag = next(
                        (
                            tg
                            for tg in existing_tags
                            if tg["name"].lower() == tag_name.lower()
                        ),
                        None
                    )
                    if not tag:
                        tag = await backend.create_tag({"name": tag_name})
                    tag_ids.append(tag["id"])

                if tag_ids:
                    task_data["tag_ids"] = tag_ids
            except Exception as e:
                print(f"Tag handling error: {e}")

        # Validate required fields
        if not task_data["title"]:
            return error_message(t("errors.title_required"))

        # Create the task
        new_task = await backend.create_task(task_data)

        # Return success message and refresh the active tasks
        return Div(
            success_message(t("tasks.created_success", title=new_task['title'])),
            Script("""
                // Clear the form
                document.querySelector('form').reset();

                // Refresh active tasks
                htmx.trigger('#active-tasks', 'refresh');

                // Auto-hide success message after 3 seconds
                setTimeout(() => {
                    document.querySelector('.success-message').style.display = 'none';
                }, 3000);
            """)
        )

    except Exception as e:
        return error_message(t("errors.create_task_failed", error=str(e)))
