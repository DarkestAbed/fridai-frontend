# pages/tags.py

from fasthtml.common import *

from app.i18n import t
from app.utils.components import (
    shell,
    form_field,
    error_message,
    success_message,
)
from app.utils.backend import BackendClient


def tags_page(backend: BackendClient):
    """Tags management page"""
    # Tag creation form
    form = Div(
        H3(t("tags.add_new")),
        Form(
            form_field(
                t("tags.field_name"),
                Input(type="text", name="name", required=True), required=True
            ),
            Button(t("tags.create_button"), type="submit"),
            **{
                "hx-post": "/app/tags/create",
                "hx-target": "#tag-form-response",
                "hx-swap": "innerHTML"
            }
        ),
        Div(id="tag-form-response"),
        **{"class": "form-section"}
    )
    content = Section(
        H2(t("tags.title")),
        P(t("tags.subtitle")),
        form,
        Hr(),
        H3(t("tags.existing")),
        Div(t("tags.loading"),
            id="tags-list",
            **{                                     # type: ignore
                "hx-get": "/api/tags",
                "hx-trigger": "load, refresh",
                "hx-swap": "innerHTML",
            }
        ),
        Hr(),
        H3(t("tags.cloud_title")),
        P(t("tags.cloud_subtitle")),
        Div(t("tags.loading_cloud"),
            id="tag-cloud",
            **{                                     # type: ignore
                "hx-get": "/app/tags/cloud",
                "hx-trigger": "load, refresh",
                "hx-swap": "innerHTML",
            },
        ),
    )
    return shell(content)


async def handle_tag_creation(request, backend: BackendClient):
    """Handle tag creation form submission"""
    try:
        form_data = await request.form()
        tag_data = {
            "name": form_data.get("name", "").strip(),
        }
        if not tag_data["name"]:
            return error_message(t("errors.tag_name_required"))
        new_tag = await backend.create_tag(tag_data)
        return Div(
            success_message(t("tags.created_success", name=new_tag['name'])),
            Script("""
                document.querySelector('form').reset();
                htmx.trigger('#tags-list', 'refresh');
                htmx.trigger('#tag-cloud', 'refresh');
            """)
        )
    except Exception as e:
        return error_message(t("errors.create_tag_failed", error=str(e)))


def render_tag_card(tag):
    """Render a tag as a card"""
    return Div(
        Span(
            tag.get('name', t("shared.unnamed")),
            style="""
            background-color: var(--secondary);
            color: var(--secondary-inverse);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            display: inline-block;
            margin-right: 10px;
            """
        ),
        Button(
            t("shared.delete"),
            **{                                                     # type: ignore
                "hx-delete": f"/api/tags/{tag.get('id')}",
                "hx-target": "closest .tag-card",
                "hx-swap": "outerHTML",
                "hx-confirm": t("tags.confirm_delete"),
            }
        ),
        **{"class": "tag-card task-item"},
        id=f"tag-{tag.get('id')}",
        style="margin: 0.5rem 0;"
    )


def render_tag_cloud(tags):
    """Render tags as a visual cloud"""
    if not tags:
        return P(t("empty_states.no_tags_cloud"))
    tag_elements = []
    for tag in tags:
        tag_elements.append(
            Span(
                tag.get('name', t("shared.unnamed")),
                style="""
                    background-color: var(--secondary);
                    color: var(--secondary-inverse);
                    padding: 0.3rem 0.8rem;
                    margin: 0.3rem;
                    border-radius: 15px;
                    display: inline-block;
                    font-size: 1rem;
                    cursor: pointer;
                """,
            )
        )
    return Div(*tag_elements, style="line-height: 2.5;")
