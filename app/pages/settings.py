# pages/settings.py

from fasthtml.common import *

from app.utils.components import (
    shell,
    form_field,
    success_message,
    error_message,
)
from app.utils.backend import BackendClient


def settings_page(backend: BackendClient):
    """Application settings and configuration page"""
    content = Section(
        Hgroup(
            H2("⚙️ Settings & Configuration"),
            P("Manage your application preferences and system configuration")
        ),
        
        # Theme Settings
        Article(
            Header(H3("🎨 Appearance")),
            Div(
                H4("Theme Settings"),
                P("Choose your preferred color scheme", style="color: var(--muted-color);"),
                Div(
                    Button(
                        "🌙 Dark",
                        id="theme-dark",
                        onclick="setTheme('dark')",
                        **{"class": "outline", "style": "flex: 1;"}
                    ),
                    Button(
                        "☀️ Light",
                        id="theme-light",
                        onclick="setTheme('light')",
                        **{"class": "outline", "style": "flex: 1;"}
                    ),
                    Button(
                        "🌓 Auto (System)",
                        id="theme-auto",
                        onclick="setTheme('auto')",
                        **{"class": "outline", "style": "flex: 1;"}
                    ),
                    **{"class": "grid", "style": "gap: 0.5rem; margin-top: 1rem;"}
                ),
                Div(
                    P(
                        "Current theme: ",
                        Strong(id="current-theme", style="color: var(--primary);"),
                        style="margin-top: 1rem;"
                    ),
                    Small(
                        "The 'Auto' option follows your system's dark/light mode preference",
                        style="color: var(--muted-color);"
                    )
                ),
                Script("""
                    // Update current theme display
                    function updateCurrentThemeDisplay() {
                        const theme = localStorage.getItem('theme') || 'dark';
                        const themeDisplay = document.getElementById('current-theme');
                        if (themeDisplay) {
                            const themeText = theme.charAt(0).toUpperCase() + theme.slice(1);
                            themeDisplay.textContent = themeText;
                        }
                        
                        // Update button states
                        document.querySelectorAll('[id^="theme-"]').forEach(btn => {
                            btn.classList.remove('primary');
                            btn.classList.add('outline');
                        });
                        
                        const activeBtn = document.getElementById('theme-' + theme);
                        if (activeBtn) {
                            activeBtn.classList.remove('outline');
                            activeBtn.classList.add('primary');
                        }
                    }
                    
                    // Update on load
                    document.addEventListener('DOMContentLoaded', updateCurrentThemeDisplay);
                    
                    // Override setTheme to update display
                    const originalSetTheme = window.setTheme;
                    window.setTheme = function(theme) {
                        originalSetTheme(theme);
                        updateCurrentThemeDisplay();
                    };
                """)
            )
        ),
        
        Hr(),
        
        # General Settings
        Article(
            Header(H3("⚡ General Settings")),
            Form(
                Div(
                    form_field("Default Task Priority", Select(
                        Option("🟢 Low", value="low"),
                        Option("🟡 Medium", value="medium", selected=True),
                        Option("🔴 High", value="high"),
                        name="default_priority"
                    )),
                    form_field("Time Zone", Select(
                        Option("UTC", value="UTC"),
                        Option("America/Santiago", value="America/Santiago", selected=True),
                        Option("America/New_York", value="America/New_York"),
                        Option("America/Los_Angeles", value="America/Los_Angeles"),
                        Option("Europe/London", value="Europe/London"),
                        Option("Europe/Paris", value="Europe/Paris"),
                        Option("Asia/Tokyo", value="Asia/Tokyo"),
                        Option("Asia/Shanghai", value="Asia/Shanghai"),
                        Option("Australia/Sydney", value="Australia/Sydney"),
                        name="timezone"
                    )),
                    **{"class": "grid"}
                ),
                form_field("Date Format", Select(
                    Option("YYYY-MM-DD", value="%Y-%m-%d", selected=True),
                    Option("DD/MM/YYYY", value="%d/%m/%Y"),
                    Option("MM/DD/YYYY", value="%m/%d/%Y"),
                    Option("DD.MM.YYYY", value="%d.%m.%Y"),
                    name="date_format"
                )),
                Button("💾 Save General Settings", type="submit", **{"class": "primary"}),
                **{
                    "hx-put": "/app/settings/general",
                    "hx-target": "#general-settings-response",
                    "hx-swap": "innerHTML"
                }
            ),
            Div(id="general-settings-response")
        ),
        
        Hr(),
        
        # Email Configuration
        Article(
            Header(H3("📧 Email Configuration")),
            Form(
                Div(
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
                            type="number",
                            name="smtp_port",
                            value="587",
                            min="1",
                            max="65535"
                        )
                    ),
                    **{"class": "grid"}
                ),
                Div(
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
                            placeholder="App password or SMTP password"
                        )
                    ),
                    **{"class": "grid"}
                ),
                Fieldset(
                    Label(
                        Input(type="checkbox", name="use_tls", checked=True, role="switch"),
                        "Use TLS encryption"
                    ),
                    Label(
                        Input(type="checkbox", name="email_notifications", role="switch"),
                        "Enable email notifications"
                    )
                ),
                Div(
                    Button("💾 Save Email Settings", type="submit", **{"class": "primary"}),
                    Button(
                        "🧪 Test Connection",
                        type="button",
                        **{
                            "hx-post": "/app/settings/test-email",
                            "hx-target": "#email-settings-response",
                            "class": "secondary"
                        }
                    ),
                    **{"class": "grid", "style": "gap: 0.5rem;"}
                ),
                **{
                    "hx-put": "/app/settings/email",
                    "hx-target": "#email-settings-response",
                    "hx-swap": "innerHTML"
                }
            ),
            Div(id="email-settings-response")
        ),
        
        Hr(),
        
        # Notification Templates
        Article(
            Header(
                H3("📝 Notification Templates"),
                P("Customize email templates for different notification types", style="color: var(--muted-color);")
            ),
            Details(
                Summary("Due Task Notification Template"),
                Form(
                    form_field(
                        "Subject Template",
                        Input(
                            type="text",
                            name="due_subject",
                            value="🔔 Task Due: {task_title}",
                            style="width: 100%;"
                        )
                    ),
                    form_field(
                        "Email Body Template",
                        Textarea(
                            name="due_body",
                            rows="10",
                            style="width: 100%; font-family: monospace;",
                            value="""Hello!

Your task "{task_title}" is due on {due_date}.

Description: {task_description}
Priority: {task_priority}
Category: {task_category}

Please complete it as soon as possible.

Best regards,
Your Task Manager"""
                        )
                    ),
                    Small(
                        "Available variables: {task_title}, {task_description}, {due_date}, {task_priority}, {task_category}",
                        style="color: var(--muted-color); display: block; margin-bottom: 1rem;"
                    ),
                    Button("💾 Save Template", type="submit", **{"class": "primary"}),
                    **{
                        "hx-put": "/app/settings/template/due",
                        "hx-target": "#template-response",
                        "hx-swap": "innerHTML",
                    }
                ),
                Div(id="template-response")
            )
        ),
        
        Hr(),
        
        # Data Management
        Article(
            Header(
                H3("💾 Data Management"),
                P("Import, export, and manage your task data", style="color: var(--muted-color);")
            ),
            
            Details(
                Summary("📥 Export Data"),
                Div(
                    P("Download your data in JSON format", style="color: var(--muted-color);"),
                    Div(
                        Button(
                            "📋 Export All Tasks",
                            **{
                                "hx-get": "/api/export/tasks",
                                "hx-target": "#export-response",
                                "class": "outline"
                            }
                        ),
                        Button(
                            "🏷️ Export Categories",
                            **{
                                "hx-get": "/api/export/categories",
                                "hx-target": "#export-response",
                                "class": "outline"
                            }
                        ),
                        Button(
                            "⚙️ Export Settings",
                            **{
                                "hx-get": "/api/export/settings",
                                "hx-target": "#export-response",
                                "class": "outline"
                            }
                        ),
                        **{"class": "grid", "style": "gap: 0.5rem; margin-top: 1rem;"}
                    )
                )
            ),
            
            Details(
                Summary("📤 Import Data"),
                Form(
                    P("Upload JSON or CSV files to import data", style="color: var(--muted-color);"),
                    Input(
                        type="file",
                        name="import_file",
                        accept=".json,.csv",
                        required=True
                    ),
                    Button("📤 Import File", type="submit", **{"class": "primary", "style": "margin-top: 1rem; width: 100%;"}),
                    **{
                        "hx-post": "/app/settings/import",
                        "hx-encoding": "multipart/form-data",
                        "hx-target": "#import-response",
                        "hx-swap": "innerHTML"
                    }
                ),
                Small(
                    "⚠️ Importing data may overwrite existing records",
                    style="color: var(--mark-color); display: block; margin-top: 0.5rem;"
                )
            ),
            
            Div(id="export-response", style="margin-top: 1rem;"),
            Div(id="import-response", style="margin-top: 1rem;")
        ),
        
        Hr(),
        
        # System Information
        Article(
            Header(H3("📊 System Information")),
            Div(
                "Loading system info...",
                id="system-info",
                **{
                    "hx-get": "/app/settings/system-info",
                    "hx-trigger": "load",
                    "hx-swap": "innerHTML",
                    "aria-busy": "true"
                }
            )
        ),
        
        Hr(),
        
        # Danger Zone
        Article(
            Header(
                Strong("⚠️ Danger Zone", style="color: var(--del-color);")
            ),
            P(
                "⚠️ These actions are irreversible. Please be very careful!",
                style="color: var(--del-color); font-weight: bold;"
            ),
            Details(
                Summary(
                    Strong("🗑️ Destructive Actions", style="color: var(--del-color);")
                ),
                Div(
                    P(
                        "Think twice before using these options. All deletions are permanent and cannot be undone.",
                        style="color: var(--muted-color); margin-bottom: 1rem;"
                    ),
                    Div(
                        Button(
                            "Delete All Completed Tasks",
                            **{
                                "hx-delete": "/api/tasks/completed",
                                "hx-confirm": "⚠️ WARNING: This will permanently delete ALL completed tasks.\n\nThis action cannot be undone.\n\nAre you absolutely sure?",
                                "hx-target": "#danger-response",
                                "class": "secondary"
                            }
                        ),
                        Button(
                            "Reset All Settings",
                            **{
                                "hx-post": "/app/settings/reset",
                                "hx-confirm": "This will reset all settings to their default values.\n\nYour tasks and data will NOT be affected.\n\nContinue?",
                                "hx-target": "#danger-response",
                                "class": "contrast"
                            }
                        ),
                        Button(
                            "⚠️ Delete All Data",
                            **{
                                "hx-delete": "/api/data/all",
                                "hx-confirm": "🚨 FINAL WARNING 🚨\n\nThis will PERMANENTLY delete:\n• All tasks\n• All categories\n• All tags\n• All settings\n• All notification logs\n\nThis action is COMPLETELY IRREVERSIBLE.\n\nAre you ABSOLUTELY CERTAIN you want to delete everything?",
                                "hx-target": "#danger-response",
                                "style": "background-color: var(--del-color); color: white;"
                            }
                        ),
                        **{"class": "grid", "style": "gap: 0.5rem; margin-top: 1rem;"}
                    ),
                    Div(id="danger-response", style="margin-top: 1rem;")
                )
            ),
            **{
                "style": "border: 2px solid var(--del-color); border-radius: var(--border-radius); padding: var(--spacing); background-color: color-mix(in srgb, var(--del-color) 5%, transparent);"
            }
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
        return success_message("✅ General settings saved successfully!")
    except Exception as e:
        return error_message(f"❌ Failed to save settings: {str(e)}")


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
            "email_notifications": form_data.get("email_notifications") is not None
        }
        
        await backend.update_settings(email_settings)
        return success_message("✅ Email settings saved successfully!")
    except Exception as e:
        return error_message(f"❌ Failed to save email settings: {str(e)}")


async def handle_template_settings(request, backend: BackendClient, template_type: str):
    """Handle notification template form submission"""
    try:
        form_data = await request.form()
        template_data = {
            f"{template_type}_template_subject": form_data.get(f"{template_type}_subject", "").strip(),
            f"{template_type}_template_body": form_data.get(f"{template_type}_body", "").strip(),
        }
        
        await backend.update_settings(template_data)
        return success_message(f"✅ {template_type.title()} notification template saved successfully!")
    except Exception as e:
        return error_message(f"❌ Failed to save template: {str(e)}")


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
        
        active_tasks = len([t for t in tasks if not t.get('completed', False)])
        completed_tasks = len(tasks) - active_tasks
        
        # Create info cards
        info_cards = [
            ("🔌 Backend Status", system_info.get("status", "Connected"), "var(--ins-color)"),
            ("📦 API Version", system_info.get("version", "Unknown"), "var(--primary)"),
            ("📋 Total Tasks", str(len(tasks)), "var(--primary)"),
            ("✅ Active Tasks", str(active_tasks), "var(--ins-color)"),
            ("☑️ Completed Tasks", str(completed_tasks), "var(--muted-color)"),
            ("🏷️ Categories", str(len(categories)), "var(--primary)"),
            ("🔖 Tags", str(len(tags)), "var(--primary)"),
            ("📧 Email Notifications", "Enabled" if settings.get('email_notifications') else "Disabled", 
             "var(--ins-color)" if settings.get('email_notifications') else "var(--muted-color)"),
            ("⚡ Default Priority", settings.get('default_priority', 'medium').title(), "var(--mark-color)"),
            ("🌍 Timezone", settings.get('timezone', 'UTC'), "var(--primary)"),
        ]
        
        info_elements = []
        for label, value, color in info_cards:
            info_elements.append(
                Div(
                    Small(label, style="display: block; color: var(--muted-color); margin-bottom: 0.25rem;"),
                    Strong(value, style=f"color: {color}; font-size: 1.1rem;"),
                    style="padding: 1rem; background-color: var(--card-background-color); border-radius: var(--border-radius); border: 1px solid var(--muted-border-color);"
                )
            )
        
        return Div(
            *info_elements,
            **{
                "class": "grid",
                "style": "gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));"
            }
        )
    except Exception as e:
        return error_message(f"❌ Failed to load system information: {str(e)}")


async def handle_data_import(request, backend: BackendClient):
    """Handle file import"""
    try:
        # This is a placeholder - actual file handling would need more work
        form_data = await request.form()
        file = form_data.get("import_file")
        
        if not file:
            return error_message("❌ No file selected")
        
        # Here you would process the file
        # For now, return a placeholder message
        return success_message("✅ Import functionality would process your file here.")
    except Exception as e:
        return error_message(f"❌ Import failed: {str(e)}")


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
            "email_password": "",
            "use_tls": True,
        }
        
        await backend.update_settings(default_settings)
        return success_message("✅ All settings have been reset to defaults.")
    except Exception as e:
        return error_message(f"❌ Failed to reset settings: {str(e)}")
