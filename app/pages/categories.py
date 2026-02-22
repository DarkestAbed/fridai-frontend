# pages/categories.py

from fasthtml.common import *

from app.i18n import t
from app.utils.components import shell, form_field, error_message, success_message
from app.utils.backend import BackendClient


def categories_page(backend: BackendClient):
    """Categories management page"""
    # Category creation form
    form = Div(
        H3(t("categories.add_new")),
        Form(
            form_field(
                t("categories.field_name"),
                Input(type="text", name="name", required=True), required=True
            ),
            Button(t("categories.create_button"), type="submit"),
            **{
                "hx-post": "/app/categories/create",
                "hx-target": "#category-form-response",
                "hx-swap": "innerHTML",
            },
        ),
        Div(id="category-form-response"),
        **{"class": "form-section"}
    )
    content = Section(
        H2(t("categories.title")),
        P(t("categories.subtitle")),
        form,
        Hr(),
        H3(t("categories.existing")),
        Div(
            t("categories.loading"),
            id="categories-list",
            **{                                     # type: ignore
                "hx-get": "/api/categories",
                "hx-trigger": "load, refresh",
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
        }
        if not category_data["name"]:
            return error_message(t("errors.category_name_required"))
        new_category = await backend.create_category(category_data)
        return Div(
            success_message(
                t("categories.created_success", name=new_category['name'])
            ),
            Script(
                """
                document.querySelector('form').reset();
                htmx.trigger('#categories-list', 'refresh');
                """
            )
        )
    except Exception as e:
        return error_message(t("errors.create_category_failed", error=str(e)))


def render_category_card(category):
    """Render a category as a card"""
    return Div(
        H4(
            category.get('name', t("shared.unnamed")),
            style="margin: 0;"
        ),
        Button(
            t("shared.delete"),
            **{                                                         # type: ignore
                "hx-delete": f"/api/categories/{category.get('id')}",
                "hx-target": "closest .category-card",
                "hx-swap": "outerHTML",
                "hx-confirm": t("categories.confirm_delete")
            },
        ),
        **{"class": "category-card task-item"},
        id=f"category-{category.get('id')}"
    )
