# app.py

import logging
from contextlib import asynccontextmanager

from fasthtml import ft
from fasthtml.common import FastHTML
from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse
from os import getenv
from typing import Optional

from app.i18n import t, set_language
from app.pages.home import home_page
from app.pages.tasks import tasks_page, handle_task_form
from app.pages.all_tasks import all_tasks_page, render_tasks_list
from app.pages.categories import categories_page
from app.pages.tags import tags_page
from app.pages.next import next_page
from app.pages.notifications import notifications_page
from app.pages.settings import settings_page
from app.utils.backend import BackendClient, BackendUnavailableError
from app.utils.components import shell, error_message

logger = logging.getLogger("fridai.frontend")


# Configuration
BACKEND_URL = getenv("BACKEND_URL", "http://localhost:8000")
VERSION = "2.0.0-vibe"

# Initialize backend client (created before lifespan so routes can reference it)
backend = BackendClient(BACKEND_URL)


@asynccontextmanager
async def lifespan(app):
    """Manage startup and shutdown lifecycle."""
    logger.info("Frontend starting up...")
    try:
        health = await backend.health_check()
        logger.info(f"Backend connected: {health.get('status', 'unknown')}")
    except Exception as e:
        logger.warning(f"Backend not reachable at startup: {e}")

    # Load saved language from backend settings
    try:
        settings = await backend.get_settings()
        lang = settings.get("language", "en")
        set_language(lang)
        logger.info(f"Language set to: {lang}")
    except Exception as e:
        logger.warning(f"Could not load language setting, using default: {e}")

    yield
    logger.info("Frontend shutting down...")
    await backend.close()
    logger.info("Backend client closed")


# Initialize FastHTML app
app = FastHTML(title="FridAI", lifespan=lifespan)


# ── Helper to build lookup maps ──────────────────────────────────────

async def _build_lookup_maps():
    """Fetch categories and tags, return (cat_map, tag_map) dicts."""
    try:
        categories = await backend.get_categories()
    except Exception:
        categories = []
    try:
        tags = await backend.get_tags()
    except Exception:
        tags = []
    cat_map = {c['id']: c['name'] for c in categories}
    tag_map = {tg['id']: tg['name'] for tg in tags}
    return cat_map, tag_map


# ── Health endpoints ─────────────────────────────────────────────────

@app.get("/health")                                     # type: ignore
async def frontend_health():
    """Basic liveness probe."""
    return JSONResponse({"status": "alive", "service": "frontend"})


@app.get("/healthz")                                    # type: ignore
async def frontend_healthz():
    """Full health check including backend connectivity."""
    result = {
        "status": "healthy",
        "service": "frontend",
        "version": VERSION,
        "checks": {},
    }
    try:
        backend_health = await backend.health_check()
        result["checks"]["backend"] = {
            "status": "up",
            "backend_status": backend_health.get("status", "unknown"),
            "backend_version": backend_health.get("version", "unknown"),
        }
    except Exception as e:
        result["status"] = "degraded"
        result["checks"]["backend"] = {
            "status": "down",
            "error": str(e),
        }

    status_code = 200 if result["status"] == "healthy" else 503
    return JSONResponse(result, status_code=status_code)


# ── Root redirect ────────────────────────────────────────────────────

@app.get("/")                                           # type: ignore
async def root():
    return RedirectResponse(url="/app", status_code=302)


# ── Page routes (full HTML pages) ────────────────────────────────────

@app.get("/app")                                        # type: ignore
def home():
    try:
        return home_page()
    except Exception as e:
        return shell(error_message(t("errors.page_load_failed", error=str(e))))


@app.get("/app/tasks")                                  # type: ignore
def tasks():
    try:
        return tasks_page(backend)
    except Exception as e:
        return shell(error_message(t("errors.page_load_failed", error=str(e))))


@app.post("/app/tasks")                                 # type: ignore
async def create_task(request: Request):
    return await handle_task_form(request, backend)


@app.get("/app/all")                                    # type: ignore
def all_tasks():
    try:
        return all_tasks_page(backend)
    except Exception as e:
        return shell(error_message(t("errors.page_load_failed", error=str(e))))


@app.get("/app/categories")                             # type: ignore
def categories():
    try:
        return categories_page(backend)
    except Exception as e:
        return shell(error_message(t("errors.page_load_failed", error=str(e))))


@app.get("/app/tags")                                   # type: ignore
def tags():
    try:
        return tags_page(backend)
    except Exception as e:
        return shell(error_message(t("errors.page_load_failed", error=str(e))))


@app.get("/app/next")                                   # type: ignore
def next48h():
    try:
        return next_page(backend)
    except Exception as e:
        return shell(error_message(t("errors.page_load_failed", error=str(e))))


@app.get("/app/notifications")                          # type: ignore
def notifications():
    try:
        return notifications_page(backend)
    except Exception as e:
        return shell(error_message(t("errors.page_load_failed", error=str(e))))


@app.get("/app/settings")                               # type: ignore
def settings():
    try:
        return settings_page(backend)
    except Exception as e:
        return shell(error_message(t("errors.page_load_failed", error=str(e))))


# ── HTMX handler routes (return HTML fragments) ─────────────────────

@app.post("/app/categories/create")                     # type: ignore
async def create_category_handler(request: Request):
    from app.pages.categories import handle_category_creation
    return await handle_category_creation(request, backend)


@app.post("/app/tags/create")                           # type: ignore
async def create_tag_handler(request: Request):
    from app.pages.tags import handle_tag_creation
    return await handle_tag_creation(request, backend)


@app.get("/app/tags/cloud")                             # type: ignore
async def tag_cloud_handler():
    from app.pages.tags import render_tag_cloud
    try:
        tags = await backend.get_tags()
        return render_tag_cloud(tags)
    except Exception as e:
        return error_message(t("errors.loading_tag_cloud", error=str(e)))


@app.get("/app/next/overdue")                           # type: ignore
async def overdue_tasks_handler():
    from app.pages.next import render_overdue_tasks
    return await render_overdue_tasks(backend)


@app.post("/app/notifications/trigger")                 # type: ignore
async def trigger_notifications_handler():
    from app.pages.notifications import trigger_notifications
    return await trigger_notifications(backend)


@app.post("/app/notifications/test-ntfy")               # type: ignore
async def test_ntfy_handler():
    from app.pages.notifications import test_ntfy_config
    return await test_ntfy_config(backend)


@app.get("/app/notifications/status")                   # type: ignore
async def notification_status_handler():
    from app.pages.notifications import render_system_status
    return await render_system_status(backend)


@app.put("/app/notifications/settings")                 # type: ignore
async def notification_settings_handler(request: Request):
    from app.pages.notifications import handle_notification_settings
    return await handle_notification_settings(request, backend)


@app.put("/app/settings/general")                       # type: ignore
async def general_settings_handler(request: Request):
    from app.pages.settings import handle_general_settings
    return await handle_general_settings(request, backend)


@app.put("/app/settings/template/{template_type}")      # type: ignore
async def template_settings_handler(request: Request, template_type: str):
    from app.pages.settings import handle_template_settings
    return await handle_template_settings(request, backend, template_type)


@app.get("/app/settings/system-info")                   # type: ignore
async def system_info_handler():
    from app.pages.settings import render_system_info
    return await render_system_info(backend)


@app.post("/app/settings/reset")                        # type: ignore
async def reset_settings_handler():
    from app.pages.settings import reset_settings
    return await reset_settings(backend)


@app.get("/app/stats")                                  # type: ignore
async def quick_stats_handler():
    """Aggregate quick stats from backend views API."""
    try:
        status_summary = await backend.get_views_summary('status-summary')
        cats_summary = await backend.get_views_summary('categories-summary')
        tags_summary = await backend.get_views_summary('tags-summary')

        pending = sum(s['count'] for s in status_summary if s['key'] == 'pending')
        completed = sum(s['count'] for s in status_summary if s['key'] == 'completed')
        total_cats = len(cats_summary)
        total_tags = len(tags_summary)

        return ft.Div(
            ft.Div(
                ft.Strong(t("stats.tasks_label")),
                ft.Span(t("stats.tasks_value", pending=pending, completed=completed)),
            ),
            ft.Div(
                ft.Strong(t("stats.categories_label")),
                ft.Span(str(total_cats)),
            ),
            ft.Div(
                ft.Strong(t("stats.tags_label")),
                ft.Span(str(total_tags)),
            ),
            style="display: grid; gap: 0.5rem;"
        )
    except Exception as e:
        return error_message(t("errors.loading_stats", error=str(e)))


@app.get("/app/all/tasks")                              # type: ignore
async def filtered_tasks(
    status: Optional[str] = None,
    sort: Optional[str] = None,
):
    """Return filtered task list as HTML fragment (for HTMX swap)."""
    return await render_tasks_list(
        backend,
        status=status or "all",
        sort=sort or "due_at",
    )


# ── API proxy endpoints (return HTML fragments) ─────────────────────

@app.get("/api/tasks")                                  # type: ignore
async def get_tasks(
    status: Optional[str] = None,
    limit: Optional[int] = None,
):
    """Proxy to backend for tasks list"""
    try:
        tasks = await backend.get_tasks(status=status)
        if limit:
            tasks = tasks[:limit]
        cat_map, tag_map = await _build_lookup_maps()
        from app.utils.components import task_card
        if not tasks:
            return ft.Div(ft.P(t("empty_states.no_tasks")))
        task_elements = [task_card(task, cat_map, tag_map) for task in tasks]
        return ft.Div(*task_elements)
    except BackendUnavailableError:
        return error_message(t("errors.backend_unreachable"))
    except Exception as e:
        return error_message(t("errors.loading_tasks", error=str(e)))


@app.get("/api/tasks/next")                             # type: ignore
async def get_next_tasks(hours: int = 48):
    """Get tasks due in next N hours"""
    try:
        from app.pages.next import render_upcoming_tasks
        return await render_upcoming_tasks(backend, hours)
    except BackendUnavailableError:
        return error_message(t("errors.backend_unreachable"))
    except Exception as e:
        return error_message(t("errors.loading_upcoming_tasks", error=str(e)))


@app.get("/api/categories")                             # type: ignore
async def get_categories():
    """Proxy to backend for categories list"""
    try:
        categories = await backend.get_categories()
        from app.pages.categories import render_category_card
        if not categories:
            return ft.Div(ft.P(t("empty_states.no_categories")))
        category_elements = [render_category_card(cat) for cat in categories]
        return ft.Div(*category_elements)
    except BackendUnavailableError:
        return error_message(t("errors.backend_unreachable"))
    except Exception as e:
        return error_message(t("errors.loading_categories", error=str(e)))


@app.get("/api/tags")                                   # type: ignore
async def get_tags():
    """Proxy to backend for tags list"""
    try:
        tags = await backend.get_tags()
        from app.pages.tags import render_tag_card
        if not tags:
            return ft.Div(ft.P(t("empty_states.no_tags")))
        tag_elements = [render_tag_card(tag) for tag in tags]
        return ft.Div(*tag_elements)
    except BackendUnavailableError:
        return error_message(t("errors.backend_unreachable"))
    except Exception as e:
        return error_message(t("errors.loading_tags", error=str(e)))


@app.get("/api/notifications/logs")                     # type: ignore
async def get_notification_logs():
    """Get notification logs"""
    try:
        from app.pages.notifications import render_notification_logs
        return await render_notification_logs(backend)
    except BackendUnavailableError:
        return error_message(t("errors.backend_unreachable"))
    except Exception as e:
        return error_message(t("errors.loading_logs", error=str(e)))


@app.delete("/api/tasks/{task_id}")                     # type: ignore
async def delete_task(task_id: str):
    """Proxy to backend for task deletion"""
    try:
        await backend.delete_task(task_id, force=True)
        return ft.Div()  # Return empty div to replace the deleted task
    except BackendUnavailableError:
        return error_message(t("errors.backend_unreachable"))
    except Exception as e:
        return error_message(t("errors.delete_task_failed", error=str(e)))


@app.put("/api/tasks/{task_id}/complete")               # type: ignore
async def complete_task(task_id: str):
    """Proxy to backend for task completion"""
    try:
        updated_task = await backend.complete_task(task_id)
        cat_map, tag_map = await _build_lookup_maps()
        from app.utils.components import task_card
        return task_card(updated_task, cat_map, tag_map)
    except BackendUnavailableError:
        return error_message(t("errors.backend_unreachable"))
    except Exception as e:
        return error_message(t("errors.complete_task_failed", error=str(e)))


@app.delete("/api/categories/{category_id}")            # type: ignore
async def delete_category(category_id: str):
    """Delete a category"""
    try:
        await backend.delete_category(category_id)
        return ft.Div()
    except BackendUnavailableError:
        return error_message(t("errors.backend_unreachable"))
    except Exception as e:
        return error_message(t("errors.delete_category_failed", error=str(e)))


@app.delete("/api/tags/{tag_id}")                       # type: ignore
async def delete_tag(tag_id: str):
    """Delete a tag"""
    try:
        await backend.delete_tag(tag_id)
        return ft.Div()
    except BackendUnavailableError:
        return error_message(t("errors.backend_unreachable"))
    except Exception as e:
        return error_message(t("errors.delete_tag_failed", error=str(e)))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
