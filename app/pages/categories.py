# pages/categories.py

from fasthtml.common import *

from app.utils.components import shell, form_field, error_message, success_message
from app.utils.backend import BackendClient


def categories_page(backend: BackendClient):
    """Categories management page"""
    # Category creation form
    form = Div(
        H3("Add New Category"),
        Form(
            form_field(
                "Category Name",
                Input(type="text", name="name", required=True), required=True
            ),
            form_field(
                "Description",
                Textarea(name="description", rows="3")
            ),
            form_field(
                "Color",
                Input(type="color", name="color", value="#3498db")
            ),
            Button("Create Category", type="submit"),       
            **{
                "hx-post": "/app/categories/create",
                "hx-target": "#category-form-response",
                "hx-swap": "innerHTML",
            },
        ),
        Div(id="category-form-response"),
        class_="form-section"
    )
    content = Section(
        H2("Category Management"),
        P("Organize your tasks with custom categories."),
        form,
        Hr(),
        H3("Existing Categories"),
        Div(
            "Loading categories...", 
            id="categories-list",
            **{                                     # type: ignore
                "hx-get": "/api/categories",
                "hx-trigger": "load",
                "hx-swap": "innerHTML",
            }
        ),
    )
    return shell(content)


async def handle_category_creation(request, backend: BackendClient):
    """Handle category creation form submission"""
    try:
        form_data = await request.form()
        category_data = {
            "name": form_data.get("name", "").strip(),
            "description": form_data.get("description", "").strip(),
            "color": form_data.get("color", "#3498db").strip(),
        }
        if not category_data["name"]:
            return error_message("Category name is required")
        new_category = await backend.create_category(category_data)
        return Div(
            success_message(
                f"Category '{new_category['name']}' created successfully!"
            ),
            Script(
                """
                document.querySelector('form').reset();
                htmx.trigger('#categories-list', 'refresh');
                """
            )
        )
    except Exception as e:
        return error_message(f"Failed to create category: {str(e)}")


def render_category_card(category):
    """Render a category as a card"""
    return Div(
        Div(
            style=f"""
                width: 20px;
                height: 20px;
                background-color: {category.get('color', '#3498db')};
                border-radius: 3px;
                display: inline-block;
                margin-right: 10px;
            """
        ),
        H4(
            category.get('name', 'Unnamed'),
            style="display: inline-block; margin: 0;"
        ),
        P(
            category.get('description', ''), style="margin: 0.5rem 0;"),
        P(
            f"Tasks: {category.get('task_count', 0)}",
            style="color: #666; font-size: 0.9rem;"
        ),
        Button(
            "Delete", 
            **{                                                         # type: ignore
                "hx-delete": f"/api/categories/{category.get('id')}",
                "hx-target": "closest .category-card",
                "hx-swap": "outerHTML",
                "hx-confirm": "Are you sure? This will remove the category from all tasks."
            },
        ),
        class_="category-card task-item",
        id=f"category-{category.get('id')}"
    )
