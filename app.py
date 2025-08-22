# app.py

import os

from fasthtml.common import *
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles


BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

app = FastAPI(title="Tasks Frontend")
htmx = Script(src="https://unpkg.com/htmx.org@1.9.12")
sakura = Link(rel="stylesheet", href="https://unpkg.com/sakura.css/css/sakura.css")

app.mount("/static", StaticFiles(directory="static"), name="static")


def nav():
    return Nav(Ul(
        Li(A("Home", href="/app")),
        Li(A("Tasks", href="/app/tasks")),
        Li(A("All", href="/app/all")),
        Li(A("Categories", href="/app/categories")),
        Li(A("Tags", href="/app/tags")),
        Li(A("Next 48h", href="/app/next")),
        Li(A("Notifications", href="/app/notifications")),
        Li(A("Settings", href="/app/settings")),
    ))


def shell(content):
    return Html(Head(Title("Tasks UI"), sakura, htmx, Link(rel="manifest", href="/static/manifest.webmanifest")),
                Body(nav(), Div(content, id="content")))


@app.get("/app")
def home():
    return shell(Section(H1("Welcome"), P("Use the navigation to explore the app.")))


@app.get("/app/tasks")
def tasks():
    form = Form(
        Input(type="text", name="title", placeholder="Task title"),
        Button("Add", type="submit"),
        action=f"{BACKEND}/api/tasks", method="post", target="_blank"
    )
    return shell(Section(H2("Tasks"), form, P("Use API directly for now. This is a thin UI.")))


@app.get("/app/all")
def all_tasks():
    return shell(Section(H2("All Tasks"), P("List view could be implemented with HTMX swaps.")))


@app.get("/app/categories")
def categories():
    return shell(Section(H2("Categories"), P("Create/list categories using backend API.")))


@app.get("/app/tags")
def tags():
    return shell(Section(H2("Tags"), P("Create/list tags using backend API.")))


@app.get("/app/next")
def next48h():
    return shell(Section(H2("Next 48h"), P("Fetch from /api/tasks/next?hours=48")))


@app.get("/app/notifications")
def notifications():
    return shell(Section(H2("Notifications"), P("Trigger backend cron and view logs.")))


@app.get("/app/settings")
def settings():
    return shell(Section(H2("Settings"), P("Edit runtime config and templates via API.")))
