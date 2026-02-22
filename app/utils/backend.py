# utils/backend.py

import httpx
from typing import Optional, List, Dict, Any


class BackendUnavailableError(Exception):
    """Raised when the backend cannot be reached."""
    pass


class BackendAPIError(Exception):
    """Raised when the backend returns an HTTP error status."""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


class BackendClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make HTTP request to backend."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            if response.headers.get('content-type', '').startswith('application/json'):
                return response.json()
            return response.text
        except httpx.ConnectError as e:
            raise BackendUnavailableError(
                f"Cannot connect to backend at {self.base_url}"
            ) from e
        except httpx.TimeoutException as e:
            raise BackendUnavailableError("Backend request timed out") from e
        except httpx.HTTPStatusError as e:
            raise BackendAPIError(
                e.response.status_code, e.response.text
            ) from e
        except httpx.RequestError as e:
            raise BackendUnavailableError(f"Request failed: {e}") from e

    # ── Task operations ──────────────────────────────────────────────

    async def get_tasks(
        self,
        status: Optional[str] = None,
        q: Optional[str] = None,
        tag: Optional[int] = None,
        overdue_only: bool = False,
        category: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get tasks with optional filters.

        Args:
            status: "pending" or "completed"
            q: search query (title/description ILIKE)
            tag: filter by tag ID
            overdue_only: only return overdue tasks
            category: filter by category ID
        """
        params: Dict[str, Any] = {}
        if status is not None:
            params['status'] = status
        if q is not None:
            params['q'] = q
        if tag is not None:
            params['tag'] = tag
        if overdue_only:
            params['overdue_only'] = 'true'
        if category is not None:
            params['category'] = category
        return await self._request('GET', '/api/tasks', params=params)

    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task."""
        return await self._request('POST', '/api/tasks', json=task_data)

    async def delete_task(self, task_id: str, force: bool = True) -> Any:
        """Delete a task. force=True allows deleting non-completed tasks."""
        params = {'force': 'true'} if force else {}
        return await self._request(
            'DELETE', f'/api/tasks/{task_id}', params=params
        )

    async def complete_task(self, task_id: str) -> Dict[str, Any]:
        """Toggle task status between pending/completed."""
        return await self._request('POST', f'/api/tasks/{task_id}/complete')

    async def get_next_tasks(self, hours: int = 48) -> List[Dict[str, Any]]:
        """Get tasks due in the next N hours."""
        return await self._request(
            'GET', '/api/tasks/next', params={'hours': hours}
        )

    async def get_overdue_tasks(self) -> List[Dict[str, Any]]:
        """Get overdue tasks via the dedicated endpoint."""
        return await self._request('GET', '/api/tasks/overdue')

    # ── Category operations ──────────────────────────────────────────

    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories."""
        return await self._request('GET', '/api/categories')

    async def create_category(self, category_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new category."""
        return await self._request(
            'POST', '/api/categories', json=category_data
        )

    async def delete_category(self, category_id: str) -> Any:
        """Delete a category."""
        return await self._request(
            'DELETE', f'/api/categories/{category_id}', params={'force': 'true'}
        )

    # ── Tag operations ───────────────────────────────────────────────

    async def get_tags(self) -> List[Dict[str, Any]]:
        """Get all tags."""
        return await self._request('GET', '/api/tags')

    async def create_tag(self, tag_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new tag."""
        return await self._request('POST', '/api/tags', json=tag_data)

    async def delete_tag(self, tag_id: str) -> Any:
        """Delete a tag."""
        return await self._request(
            'DELETE', f'/api/tags/{tag_id}', params={'force': 'true'}
        )

    # ── Notification operations ──────────────────────────────────────

    async def trigger_notifications(
        self, mode: str = "both"
    ) -> Dict[str, Any]:
        """Trigger notification cron job."""
        return await self._request(
            'POST', '/api/notifications/cron', params={'mode': mode}
        )

    async def test_notification(self) -> Dict[str, Any]:
        """Send a test notification via ntfy."""
        return await self._request('POST', '/api/notifications/test')

    async def get_notification_logs(
        self, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get notification logs."""
        return await self._request(
            'GET', '/api/notifications/logs', params={'limit': limit}
        )

    async def get_notification_template(
        self, key: str
    ) -> Dict[str, Any]:
        """Get a notification template by key ('due_soon' or 'overdue')."""
        return await self._request(
            'GET', f'/api/notifications/templates/{key}'
        )

    async def update_notification_template(
        self, key: str, markdown: str
    ) -> Dict[str, Any]:
        """Update a notification template."""
        return await self._request(
            'PATCH', f'/api/notifications/templates/{key}',
            json={'markdown': markdown},
        )

    # ── Settings/Config operations ───────────────────────────────────

    async def get_settings(self) -> Dict[str, Any]:
        """Get current settings from /api/config."""
        return await self._request('GET', '/api/config')

    async def update_settings(
        self, settings_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update settings via PATCH /api/config."""
        return await self._request(
            'PATCH', '/api/config', json=settings_data
        )

    # ── Views/Summary operations ─────────────────────────────────────

    async def get_views_summary(
        self, summary_type: str
    ) -> List[Dict[str, Any]]:
        """Get view summaries.

        summary_type: 'categories-summary', 'status-summary', or 'tags-summary'
        """
        return await self._request('GET', f'/api/views/{summary_type}')

    # ── Health ───────────────────────────────────────────────────────

    async def health_check(self) -> Dict[str, Any]:
        """Check backend health via /healthz."""
        return await self._request('GET', '/healthz')

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
