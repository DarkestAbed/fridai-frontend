# app.py

from fasthtml.common import *
from fastapi import Request
from os import getenv
from starlette.staticfiles import StaticFiles
from typing import Optional

# Import our modular pages
from app.pages.home import home_page
from app.pages.tasks import tasks_page, handle_task_form
from app.pages.all_tasks import all_tasks_page
from app.pages.categories import categories_page
from app.pages.tags import tags_page
from app.pages.next import next_page
from app.pages.notifications import notifications_page
from app.pages.settings import settings_page
from app.utils.backend import BackendClient


# Configuration
BACKEND_URL = getenv("BACKEND_URL", "http://localhost:8000")
# Initialize FastAPI app
app = FastHTML(title="Tasks Frontend")
# Static files
# app.mount("/static", StaticFiles(directory="static"), name="static")
# Initialize backend client
backend = BackendClient(BACKEND_URL)


# Routes
@app.get("/app")
def home():
    return home_page()


@app.get("/app/tasks")
def tasks():
    return tasks_page(backend)


@app.post("/app/tasks")
async def create_task(request: Request):
    return await handle_task_form(request, backend)


@app.get("/app/all")
def all_tasks():
    return all_tasks_page(backend)


@app.get("/app/categories")
def categories():
    return categories_page(backend)


@app.get("/app/tags")
def tags():
    return tags_page(backend)


@app.get("/app/next")
def next48h():
    return next_page(backend)


@app.get("/app/notifications")
def notifications():
    return notifications_page(backend)


@app.get("/app/settings")
def settings():
    return settings_page(backend)


# Additional route handlers for HTMX interactions
@app.post("/app/categories/create")
async def create_category_handler(request: Request):
    from app.pages.categories import handle_category_creation
    return await handle_category_creation(request, backend)


@app.post("/app/tags/create")
async def create_tag_handler(request: Request):
    from app.pages.tags import handle_tag_creation
    return await handle_tag_creation(request, backend)


@app.get("/app/tags/cloud")
async def tag_cloud_handler():
    from app.pages.tags import render_tag_cloud
    try:
        tags = await backend.get_tags()
        return render_tag_cloud(tags)
    except Exception as e:
        return Div(f"Error loading tag cloud: {str(e)}", class_="error-message")


@app.get("/app/next/overdue")
async def overdue_tasks_handler():
    from app.pages.next import render_overdue_tasks
    return await render_overdue_tasks(backend)


@app.post("/app/notifications/trigger")
async def trigger_notifications_handler():
    from app.pages.notifications import trigger_notifications
    return await trigger_notifications(backend)


@app.post("/app/notifications/test-email")
async def test_email_handler():
    from app.pages.notifications import test_email_config
    return await test_email_config(backend)


@app.get("/app/notifications/status")
async def notification_status_handler():
    from app.pages.notifications import render_system_status
    return await render_system_status(backend)


@app.put("/app/settings/general")
async def general_settings_handler(request: Request):
    from app.pages.settings import handle_general_settings
    return await handle_general_settings(request, backend)


@app.put("/app/settings/email")
async def email_settings_handler(request: Request):
    from app.pages.settings import handle_email_settings
    return await handle_email_settings(request, backend)


@app.put("/app/settings/template/{template_type}")
async def template_settings_handler(request: Request, template_type: str):
    from app.pages.settings import handle_template_settings
    return await handle_template_settings(request, backend, template_type)


@app.get("/app/settings/system-info")
async def system_info_handler():
    from app.pages.settings import render_system_info
    return await render_system_info(backend)


@app.post("/app/settings/import")
async def import_data_handler(request: Request):
    from app.pages.settings import handle_data_import
    return await handle_data_import(request, backend)


@app.post("/app/settings/reset")
async def reset_settings_handler():
    from app.pages.settings import reset_settings
    return await reset_settings(backend)


# API proxy endpoints for HTMX calls
@app.get("/api/tasks")
async def get_tasks(completed: Optional[bool] = None, limit: Optional[int] = None):
    """Proxy to backend for tasks list"""
    try:
        tasks = await backend.get_tasks(completed=completed)
        if limit:
            tasks = tasks[:limit]        
        # Return HTML for HTMX
        from app.utils.components import task_card
        if not tasks:
            return Div(P("No tasks found."))
        task_elements = [task_card(task) for task in tasks]
        return Div(*task_elements)
    except Exception as e:
        from app.utils.components import error_message
        return error_message(f"Error loading tasks: {str(e)}")


@app.get("/api/tasks/next")
async def get_next_tasks(hours: int = 48):
    """Get tasks due in next N hours"""
    try:
        from app.pages.next import render_upcoming_tasks
        return await render_upcoming_tasks(backend, hours)
    except Exception as e:
        from app.utils.components import error_message
        return error_message(f"Error loading upcoming tasks: {str(e)}")


@app.get("/api/categories")
async def get_categories():
    """Proxy to backend for categories list"""
    try:
        categories = await backend.get_categories()
        from app.pages.categories import render_category_card        
        if not categories:
            return Div(P("No categories found."))
        category_elements = [render_category_card(cat) for cat in categories]
        return Div(*category_elements)
    except Exception as e:
        from app.utils.components import error_message
        return error_message(f"Error loading categories: {str(e)}")


@app.get("/api/tags")
async def get_tags():
    """Proxy to backend for tags list"""
    try:
        tags = await backend.get_tags()
        from app.pages.tags import render_tag_card        
        if not tags:
            return Div(P("No tags found."))
        tag_elements = [render_tag_card(tag) for tag in tags]
        return Div(*tag_elements)
    except Exception as e:
        from app.utils.components import error_message
        return error_message(f"Error loading tags: {str(e)}")


@app.get("/api/notifications/logs")
async def get_notification_logs():
    """Get notification logs"""
    try:
        from app.pages.notifications import render_notification_logs
        return await render_notification_logs(backend)
    except Exception as e:
        from app.utils.components import error_message
        return error_message(f"Error loading logs: {str(e)}")


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """Proxy to backend for task deletion"""
    try:
        await backend.delete_task(task_id)
        return Div()  # Return empty div to replace the deleted task
    except Exception as e:
        from app.utils.components import error_message
        return error_message(f"Failed to delete task: {str(e)}")


@app.put("/api/tasks/{task_id}/complete")
async def complete_task(task_id: str):
    """Proxy to backend for task completion"""
    try:
        updated_task = await backend.complete_task(task_id)
        from app.utils.components import task_card
        return task_card(updated_task)
    except Exception as e:
        from app.utils.components import error_message
        return error_message(f"Failed to complete task: {str(e)}")


@app.delete("/api/categories/{category_id}")
async def delete_category(category_id: str):
    """Delete a category"""
    try:
        await backend.delete_category(category_id)
        return Div()  # Return empty div to replace deleted category
    except Exception as e:
        from app.utils.components import error_message
        return error_message(f"Failed to delete category: {str(e)}")


@app.delete("/api/tags/{tag_id}")
async def delete_tag(tag_id: str):
    """Delete a tag"""
    try:
        await backend.delete_tag(tag_id)
        return Div()  # Return empty div to replace deleted tag
    except Exception as e:
        from app.utils.components import error_message
        return error_message(f"Failed to delete tag: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
