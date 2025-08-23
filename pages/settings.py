# pages/settings.py

from fasthtml.common import *
from utils.components import shell, form_field, success_message, error_message
from utils.backend import BackendClient


def settings_page(backend: BackendClient):
    """Application settings and configuration page"""
    content = Section(
        H2("Settings & Configuration"),
        P("Manage your application preferences and system configuration."),
        # General Settings
        Div(
            H3("General Settings"),
            Form(
                form_field("Default Task Priority", Select(
                    Option("Low", value="low"),
                    Option("Medium", value="medium", selected=True),
                    Option("High", value="high"),
                    name="default_priority"
                )),
                form_field("Time Zone", Select(
                    Option("UTC", value="UTC"),
                    Option(
                        "America/Santiago",
                        value="America/Santiago",
                        selected=True,
                    ),
                    Option("America/New_York", value="America/New_York"),
                    Option("America/Los_Angeles", value="America/Los_Angeles"),
                    Option("Europe/London", value="Europe/London"),
                    Option("Asia/Tokyo", value="Asia/Tokyo"),
                    name="timezone"
                )),
                form_field("Date Format", Select(
                    Option("YYYY-MM-DD", value="%Y-%m-%d", selected=True),
                    Option("DD/MM/YYYY", value="%d/%m/%Y"),
                    name="date_format"
                )),
                Button("Save General Settings", type="submit"),
                **{
                    "hx-put": "/app/settings/general",
                    "hx-target": "#general-settings-response",
                    "hx-swap": "innerHTML"
                }
            ),
            Div(id="general-settings-response"),
            class_="form-section"
        ),
        Hr(),
        # Email Configuration
        Div(
            H3("Email Configuration"),
            Form(
                form_field(
                    "SMTP Server",
                    Input(
                        type="text",
                        name="smtp_server",
                        placeholder="smtp.gmail.com"
                    )
                ),
                form_field(
                    "SMTP Port",
                    Input(
                        type="number", name="smtp_port", value="587"
                    )
                ),
                form_field(
                    "Email Address",
                    Input(
                        type="email",
                        name="email_address",
                        placeholder="your@email.com"
                    )
                ),
                form_field(
                    "Email Password",
                    Input(
                        type="password",
                        name="email_password",
                        placeholder="App password"
                    )
                ),
                Div(
                    Label("Use TLS:"),
                    Input(type="checkbox", name="use_tls", checked=True),
                    style="margin-bottom: 1rem;"
                ),
                
                Button("Save Email Settings", type="submit"),
                Button(
                    "Test Connection", type="button", 
                    **{                                             # type: ignore
                        "hx-post": "/app/settings/test-email",
                        "hx-target": "#email-settings-response",
                    }
                ),
                **{
                    "hx-put": "/app/settings/email",
                    "hx-target": "#email-settings-response",
                    "hx-swap": "innerHTML"
                }
            ),
            Div(id="email-settings-response"),
            class_="form-section"
        ),
        Hr(),
        # Notification Templates
        Div(
            H3("Notification Templates"),
            P("Customize email templates for different notification types."),
            
            Div(
                H4("Due Task Notification Template"),
                Form(
                    form_field(
                        "Subject",
                        Input(
                            type="text",
                            name="due_subject", 
                            value="🔔 Task Due: {task_title}",
                            style="width: 100%;"
                        )
                    ),
                    form_field(
                        "Email Body",
                        Textarea(
                            name="due_body",
                            rows="8",
                            style="width: 100%;",
                            placeholder="""
Hello!

Your task "{task_title}" is due on {due_date}.

Description: {task_description}
Priority: {task_priority}
Category: {task_category}

Please complete it as soon as possible.

Best regards,
Your Task Manager"""
                        )
                    ),
                    Button("Save Template", type="submit"),
                    **{
                        "hx-put": "/app/settings/template/due",
                        "hx-target": "#template-response",
                        "hx-swap": "innerHTML",
                    }
                ),
            ),
            Div(id="template-response"),
            class_="form-section"
        ),
        Hr(),
        # Data Management
        Div(
            H3("Data Management"),
            P("Import, export, and manage your task data."),
            Div(
                Button(
                    "Export All Tasks", 
                    **{                                     # type: ignore
                        "hx-get": "/api/export/tasks",
                        "hx-target": "#export-response"
                    }),
                Button(
                    "Export Categories", 
                    **{                                         # type: ignore
                        "hx-get": "/api/export/categories",
                        "hx-target": "#export-response",
                    }
                ),
                Button(
                    "Export Settings", 
                    **{                                         # type: ignore
                        "hx-get": "/api/export/settings",
                        "hx-target": "#export-response"
                    }
                ),
            ),
            Div(
                H4("Import Data"),
                Form(
                    Input(type="file", name="import_file", accept=".json,.csv"),
                    Button("Import", type="submit"),
                    **{
                        "hx-post": "/app/settings/import",
                        "hx-encoding": "multipart/form-data",
                        "hx-target": "#import-response",
                        "hx-swap": "innerHTML"
                    }
                ),
                P(
                    "Supported formats: JSON, CSV",
                    style="color: #666; font-size: 0.9rem;"
                )
            ),
            Div(id="export-response"),
            Div(id="import-response"),
            class_="form-section"
        ),
        Hr(),
        # System Information
        Div(
            H3("System Information"),
            Div(
                "Loading system info...", 
                id="system-info",
                **{                                                 # type: ignore
                    "hx-get": "/app/settings/system-info",
                    "hx-trigger": "load",
                    "hx-swap": "innerHTML"
                }
            ),
            class_="form-section"
        ),
        Hr(),
        # Danger Zone
        Div(
            H3("Danger Zone", style="color: #dc3545;"),
            P(
                "Irreversible actions. Please be careful!",
                style="color: #dc3545;",
            ),
            Button(
                "Delete All Completed Tasks", 
                style="background-color: #dc3545; color: white;",
                **{                                                 # type: ignore
                    "hx-delete": "/api/tasks/completed",
                    "hx-confirm": "This will permanently delete ALL completed tasks. This cannot be undone. Are you absolutely sure?",
                    "hx-target": "#danger-response"
                }
            ),
            Button(
                "Reset All Settings", 
                style="""
                    background-color: #fd7e14;
                    color: white;
                    margin-left: 0.5rem;
                """,
                **{                                             # type: ignore
                    "hx-post": "/app/settings/reset",
                    "hx-confirm": "This will reset all settings to defaults. Continue?",
                    "hx-target": "#danger-response"}),
            Button(
                "Delete All Data", 
                style="background-color: #6f42c1; color: white; margin-left: 0.5rem;",
                **{                                                 # type: ignore
                    "hx-delete": "/api/data/all",
                    "hx-confirm": "⚠️ FINAL WARNING ⚠️\n\nThis will delete ALL your data including:\n- All tasks\n- All categories\n- All tags\n- All settings\n\nThis action is IRREVERSIBLE.\n\nType 'DELETE EVERYTHING' to confirm.",
                    "hx-target": "#danger-response"
                }
            ),
            Div(id="danger-response"),
            style="""
                border: 2px solid #dc3545;
                padding: 1rem;
                border-radius: 4px;
                margin-top: 1rem;
            """
        )
    )
    return shell(content)


async def handle_general_settings(request, backend: BackendClient):
    """Handle general settings form submission"""
    try:
        form_data = await request.form()
        settings_data = {
            "default_priority": form_data.get("default_priority", "medium"),
            "timezone": form_data.get("timezone", "UTC"),
            "date_format": form_data.get("date_format", "%Y-%m-%d"),
        }
        await backend.update_settings(settings_data)
        return success_message("General settings saved successfully!")
    except Exception as e:
        return error_message(f"Failed to save settings: {str(e)}")


async def handle_email_settings(request, backend: BackendClient):
    """Handle email configuration form submission"""
    try:
        form_data = await request.form()
        email_settings = {
            "smtp_server": form_data.get("smtp_server", "").strip(),
            "smtp_port": int(form_data.get("smtp_port", 587)),
            "email_address": form_data.get("email_address", "").strip(),
            "email_password": form_data.get("email_password", "").strip(),
            "use_tls": form_data.get("use_tls") is not None,
            "email_notifications": True  # Enable notifications when configuring email
        }
        await backend.update_settings(email_settings)
        return success_message("Email settings saved successfully!")
    except Exception as e:
        return error_message(f"Failed to save email settings: {str(e)}")


async def handle_template_settings(request, backend: BackendClient, template_type: str):
    """Handle notification template form submission"""
    try:
        form_data = await request.form()
        template_data = {
            f"{template_type}_template_subject": form_data.get(f"{template_type}_subject", "").strip(),
            f"{template_type}_template_body": form_data.get(f"{template_type}_body", "").strip(),
        }
        await backend.update_settings(template_data)
        return success_message(f"{template_type.title()} notification template saved successfully!")
    except Exception as e:
        return error_message(f"Failed to save template: {str(e)}")


async def render_system_info(backend: BackendClient):
    """Render system information"""
    try:
        # Try to get system info from backend
        try:
            system_info = await backend._request('GET', '/api/system/info')
        except:
            # Fallback if endpoint doesn't exist
            system_info = {
                "status": "Backend connection successful",
                "version": "Unknown"
            }
        # Get current settings
        try:
            settings = await backend.get_settings()
        except:
            settings = {}
        # Get some basic stats
        try:
            tasks = await backend.get_tasks()
            categories = await backend.get_categories()
            tags = await backend.get_tags()
        except:
            tasks = []
            categories = []
            tags = []
        info_items = [
            ("Backend Status", system_info.get("status", "Connected")),
            ("API Version", system_info.get("version", "Unknown")),
            ("Total Tasks", str(len(tasks))),
            (
                "Active Tasks",
                str(len([t for t in tasks if not t.get('completed', False)]))
            ),
            ("Categories", str(len(categories))),
            ("Tags", str(len(tags))),
            (
                "Email Notifications",
                "Enabled" if settings.get('email_notifications') else "Disabled"
            ),
            (
                "Default Priority",
                settings.get('default_priority', 'medium').title()
            ),
            ("Timezone", settings.get('timezone', 'UTC')),
        ]
        info_elements = [
            Div(
                Strong(f"{label}: "),
                Span(value),
                style="margin-bottom: 0.5rem;"
            )
            for label, value in info_items
        ]
        return Div(
            *info_elements,
            style="""
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 0.5rem;
            """
        )
    except Exception as e:
        return error_message(f"Failed to load system information: {str(e)}")


async def handle_data_import(request, backend: BackendClient):
    """Handle file import"""
    try:
        # This is a placeholder - actual file handling would need more work
        return success_message("Import functionality would be implemented here.")
    except Exception as e:
        return error_message(f"Import failed: {str(e)}")


async def reset_settings(backend: BackendClient):
    """Reset all settings to defaults"""
    try:
        default_settings = {
            "default_priority": "medium",
            "timezone": "UTC",
            "date_format": "%Y-%m-%d",
            "email_notifications": False,
            "smtp_server": "",
            "smtp_port": 587,
            "email_address": "",
            "use_tls": True,
        }
        await backend.update_settings(default_settings)
        return success_message("All settings have been reset to defaults.")
    except Exception as e:
        return error_message(f"Failed to reset settings: {str(e)}")
