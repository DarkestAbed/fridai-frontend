# pages/tasks.py

from fastapi import Request
from fasthtml.common import *

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
        Header(H3("➕ Add New Task")),
        Form(
            Div(
                form_field(
                    "Title",
                    Input(
                        type="text",
                        name="title",
                        required=True,
                        placeholder="Enter task title..."
                    ),
                    required=True,
                ),
                form_field(
                    "Description",
                    Textarea(
                        name="description",
                        rows="3",
                        placeholder="Add a detailed description (optional)"
                    )
                ),
                **{"class": "grid"}
            ),
            
            Div(
                form_field(
                    "Priority",
                    Select(
                        Option("🟢 Low", value="low"),
                        Option("🟡 Medium", value="medium", selected=True),
                        Option("🔴 High", value="high"),
                        name="priority"
                    )
                ),
                form_field(
                    "Due Date",
                    Input(type="datetime-local", name="due_date"),
                ),
                **{"class": "grid"}
            ),
            
            Div(
                form_field(
                    "Category",
                    Input(
                        type="text",
                        name="category",
                        placeholder="Optional category name",
                        list="categories-list"
                    ),
                ),
                form_field(
                    "Tags",
                    Input(
                        type="text",
                        name="tags",
                        placeholder="Comma-separated tags",
                    ),
                ),
                **{"class": "grid"}
            ),
            
            # Datalist for categories autocomplete
            Datalist(id="categories-list"),
            
            Button(
                "Create Task",
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
            H2("Task Management"),
            P("Create and manage your tasks efficiently")
        ),
        
        form,
        
        Hr(),
        
        Article(
            Header(
                H3("✅ Active Tasks"),
                P(
                    "Tasks that need your attention",
                    style="color: var(--muted-color); margin: 0;"
                )
            ),
            Div(
                "Loading active tasks...",
                id="active-tasks",
                **{
                    "hx-get": "/api/tasks?completed=false",
                    "hx-trigger": "load",
                    "hx-swap": "innerHTML",
                    "aria-busy": "true"
                },
            ),
        ),
        
        Hr(),
        
        Details(
            Summary("📝 Recently Completed"),
            Div(
                "Loading completed tasks...",
                id="completed-tasks",
                **{
                    "hx-get": "/api/tasks?completed=true&limit=5",
                    "hx-trigger": "toggle once",
                    "hx-swap": "innerHTML",
                    "aria-busy": "true"
                }
            )
        ),
        
        Script("""
            // Load categories for autocomplete
            fetch('/api/categories')
                .then(response => response.json())
                .then(categories => {
                    const datalist = document.getElementById('categories-list');
                    if (datalist && categories) {
                        categories.forEach(cat => {
                            const option = document.createElement('option');
                            option.value = cat.name;
                            datalist.appendChild(option);
                        });
                    }
                })
                .catch(console.error);
        """)
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
            "priority": form_data.get("priority", "medium"),
        }
        
        # Handle due date
        due_date = form_data.get("due_date", "").strip()
        if due_date:
            task_data["due_date"] = due_date
        
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
                            t
                            for t in existing_tags
                            if t["name"].lower() == tag_name.lower()
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
            return error_message("Title is required")
        
        # Create the task
        new_task = await backend.create_task(task_data)
        
        # Return success message and refresh the active tasks
        return Div(
            success_message(f"✅ Task '{new_task['title']}' created successfully!"),
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
        return error_message(f"Failed to create task: {str(e)}")
