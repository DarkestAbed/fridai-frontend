# pages/notifications.py

from fasthtml.common import *
from utils.components import shell, success_message, error_message
from utils.backend import BackendClient
from datetime import datetime


def notifications_page(backend: BackendClient):
    """Notifications and cron management page"""
    
    # Manual trigger section
    trigger_section = Div(
        H3("Manual Trigger"),
        P("Manually trigger notification checks and email sending."),
        
        Button("Send Due Task Notifications", 
               **{"hx-post": "/app/notifications/trigger",
                  "hx-target": "#trigger-response",
                  "hx-swap": "innerHTML"}),
        Button("Test Email Configuration", 
               **{"hx-post": "/app/notifications/test-email",
                  "hx-target": "#trigger-response",
                  "hx-swap": "innerHTML"}),
        
        Div(id="trigger-response"),
        class_="form-section"
    )
    
    # Notification settings
    settings_section = Div(
        H3("Notification Settings"),
        Form(
            Div(
                Label("Enable Email Notifications:"),
                Input(type="checkbox", name="email_enabled", checked=True),
                style="margin-bottom: 1rem;"
            ),
            
            Div(
                Label("Notification Lead Time (hours):"),
                Input(type="number", name="lead_time", value="24", min="1", max="168"),
                style="margin-bottom: 1rem;"
            ),
            
            Div(
                Label("Email Address:"),
                Input(type="email", name="notification_email", placeholder="your@email.com"),
                style="margin-bottom: 1rem;"
            ),
            
            Div(
                Label("Notification Frequency:"),
                Select(
                    Option("Every hour", value="hourly"),
                    Option("Every 6 hours", value="6hourly"),
                    Option("Daily", value="daily", selected=True),
                    name="frequency"
                ),
                style="margin-bottom: 1rem;"
            ),
            
            Button("Save Settings", type="submit"),
            
            **{"hx-put": "/app/notifications/settings",
               "hx-target": "#settings-response",
               "hx-swap": "innerHTML"}
        ),
        Div(id="settings-response"),
        class_="form-section"
    )
    
    content = Section(
        H2("Notification Management"),
        P("Configure and manage task notifications and email alerts."),
        trigger_section,
        
        Hr(),
        
        settings_section,
        
        Hr(),
        
        H3("Notification History"),
        Div("Loading notification logs...", 
            id="notification-logs",
            **{"hx-get": "/api/notifications/logs",
               "hx-trigger": "load",
               "hx-swap": "innerHTML"}),
        
        Hr(),
        
        H3("System Status"),
        Div("Checking system status...", 
            id="system-status",
            **{"hx-get": "/app/notifications/status",
               "hx-trigger": "load",
               "hx-swap": "innerHTML"}),
    )
    
    return shell(content)


async def trigger_notifications(backend: BackendClient):
    """Manually trigger notifications"""
    try:
        result = await backend.trigger_notifications()
        
        notifications_sent = result.get('notifications_sent', 0)
        tasks_processed = result.get('tasks_processed', 0)
        
        if notifications_sent > 0:
            return success_message(
                f"Successfully sent {notifications_sent} notification(s) for {tasks_processed} task(s)!"
            )
        else:
            return success_message(
                f"Processed {tasks_processed} task(s), no notifications needed at this time."
            )
    except Exception as e:
        return error_message(f"Failed to trigger notifications: {str(e)}")


async def test_email_config(backend: BackendClient):
    """Test email configuration"""
    try:
        # This would be a backend endpoint that sends a test email
        result = await backend._request('POST', '/api/notifications/test')
        
        return success_message("Test email sent successfully! Check your inbox.")
    except Exception as e:
        return error_message(f"Email test failed: {str(e)}")


async def render_notification_logs(backend: BackendClient):
    """Render notification history logs"""
    try:
        logs = await backend.get_notification_logs()
        
        if not logs:
            return P("No notification logs available yet.")
        
        log_elements = []
        for log in logs[:50]:  # Limit to last 50 logs
            timestamp = log.get('timestamp', '')
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                formatted_time = timestamp
            
            status = log.get('status', 'unknown')
            message = log.get('message', 'No message')
            task_title = log.get('task_title', 'Unknown task')
            
            status_color = {
                'success': '#28a745',
                'error': '#dc3545',
                'warning': '#ffc107',
                'info': '#17a2b8'
            }.get(status, '#6c757d')
            
            log_elements.append(
                Div(
                    Div(
                        Strong(formatted_time),
                        Span(status.upper(), 
                             style=f"background-color: {status_color}; color: white; padding: 0.2rem 0.5rem; border-radius: 3px; font-size: 0.8rem; margin-left: 1rem;")
                    ),
                    P(f"Task: {task_title}"),
                    P(message, style="color: #666; font-size: 0.9rem;"),
                    style="border-bottom: 1px solid #eee; padding: 1rem 0;"
                )
            )
        
        return Div(
            P(f"Showing last {len(log_elements)} notification log(s)"),
            *log_elements
        )
        
    except Exception as e:
        return error_message(f"Failed to load notification logs: {str(e)}")


async def render_system_status(backend: BackendClient):
    """Render system status information"""
    try:
        # Get current settings
        settings = await backend.get_settings()
        
        email_enabled = settings.get('email_notifications', False)
        last_check = settings.get('last_notification_check', 'Never')
        
        # Try to get some basic stats
        try:
            tasks = await backend.get_tasks(completed=False)
            due_soon = await backend.get_next_tasks(24)
        except:
            tasks = []
            due_soon = []
        
        status_items = [
            Div(
                Strong("Email Notifications: "),
                Span("Enabled" if email_enabled else "Disabled", 
                     style=f"color: {'#28a745' if email_enabled else '#dc3545'};")
            ),
            Div(
                Strong("Last Check: "),
                Span(last_check)
            ),
            Div(
                Strong("Active Tasks: "),
                Span(str(len(tasks)))
            ),
            Div(
                Strong("Due in 24h: "),
                Span(str(len(due_soon)), 
                     style=f"color: {'#dc3545' if len(due_soon) > 5 else '#28a745'};")
            )
        ]
        return Div(
            *status_items,
            style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;"
        )        
    except Exception as e:
        return error_message(f"Failed to load system status: {str(e)}")
