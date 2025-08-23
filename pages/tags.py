# pages/tags.py

from fasthtml.common import *
from utils.components import shell, form_field, error_message, success_message
from utils.backend import BackendClient


def tags_page(backend: BackendClient):
    """Tags management page"""
    # Tag creation form
    form = Div(
        H3("Add New Tag"),
        Form(
            form_field(
                "Tag Name",
                Input(type="text", name="name", required=True), required=True
            ),
            form_field(
                "Color",
                Input(type="color", name="color", value="#28a745")
            ),
            Button("Create Tag", type="submit"),
            **{
                "hx-post": "/app/tags/create",
                "hx-target": "#tag-form-response",
                "hx-swap": "innerHTML"
            }
        ),
        Div(id="tag-form-response"),
        class_="form-section"
    )
    content = Section(
        H2("Tag Management"),
        P("Label and organize your tasks with custom tags."),
        form,
        Hr(),
        H3("Existing Tags"),
        Div("Loading tags...", 
            id="tags-list",
            **{                                     # type: ignore
                "hx-get": "/api/tags",
                "hx-trigger": "load",
                "hx-swap": "innerHTML",
            }
        ),
        Hr(),
        H3("Tag Cloud"),
        P("Visual representation of your most used tags"),
        Div("Loading tag cloud...", 
            id="tag-cloud",
            **{                                     # type: ignore
                "hx-get": "/app/tags/cloud",
                "hx-trigger": "load",
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
            "color": form_data.get("color", "#28a745").strip(),
        }
        if not tag_data["name"]:
            return error_message("Tag name is required")
        new_tag = await backend.create_tag(tag_data)
        return Div(
            success_message(f"Tag '{new_tag['name']}' created successfully!"),
            Script("""
                document.querySelector('form').reset();
                htmx.trigger('#tags-list', 'refresh');
                htmx.trigger('#tag-cloud', 'refresh');
            """)
        )
    except Exception as e:
        return error_message(f"Failed to create tag: {str(e)}")


def render_tag_card(tag):
    """Render a tag as a card"""
    return Div(
        Span(
            tag.get('name', 'Unnamed'),
            style=f"""
            background-color: {tag.get('color', '#28a745')};
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            display: inline-block;
            margin-right: 10px;
            """
        ),
        P(
            f"Used in {tag.get('task_count', 0)} task(s)",
            style="color: #666; font-size: 0.9rem; margin: 0.5rem 0;"
        ),
        Button(
            "Delete", 
            **{                                                     # type: ignore
                "hx-delete": f"/api/tags/{tag.get('id')}",
                "hx-target": "closest .tag-card",
                "hx-swap": "outerHTML",
                "hx-confirm": "Are you sure? This will remove the tag from all tasks.",
            }
        ),
        class_="tag-card task-item",
        id=f"tag-{tag.get('id')}",
        style="margin: 0.5rem 0;"
    )


def render_tag_cloud(tags):
    """Render tags as a visual cloud"""
    if not tags:
        return P("No tags available yet.")
    # Sort by usage count
    sorted_tags = sorted(
        tags,
        key=lambda t: t.get('task_count', 0),
        reverse=True,
    )
    max_count = (
        max(tag.get('task_count', 1) for tag in sorted_tags)
        if sorted_tags
        else 1
    )
    tag_elements = []
    for tag in sorted_tags:
        count = tag.get('task_count', 0)
        # Scale font size based on usage (1rem to 2rem)
        font_size = 1 + (count / max_count) if max_count > 0 else 1        
        tag_elements.append(
            Span(
                tag.get('name', 'Unnamed'),
                style=f"""
                    background-color: {tag.get('color', '#28a745')};
                    color: white;
                    padding: 0.3rem 0.8rem;
                    margin: 0.3rem;
                    border-radius: 15px;
                    display: inline-block;
                    font-size: {font_size}rem;
                    cursor: pointer;
                """,
                **{                                                 # type: ignore
                    "hx-get": f"/app/tasks?tag={tag.get('id')}",
                    "hx-target": "#content"
                }
            )
        )
    return Div(*tag_elements, style="line-height: 2.5;")
