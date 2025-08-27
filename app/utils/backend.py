# utils/backend.py

import httpx
from typing import Optional, List, Dict, Any


class BackendClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make HTTP request to backend"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            if response.headers.get('content-type', '').startswith('application/json'):
                return response.json()
            return response.text
        except httpx.RequestError as e:
            raise Exception(f"Request failed: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
    
    # Task operations
    async def get_tasks(self, completed: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Get all tasks or filter by completion status"""
        params = {}
        if completed is not None:
            params['completed'] = str(completed).lower()
        return await self._request('GET', '/api/tasks', params=params)
    
    async def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get a specific task by ID"""
        return await self._request('GET', f'/api/tasks/{task_id}')
    
    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task"""
        return await self._request('POST', '/api/tasks', json=task_data)
    
    async def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing task"""
        return await self._request('PUT', f'/api/tasks/{task_id}', json=task_data)
    
    async def delete_task(self, task_id: str) -> None:
        """Delete a task"""
        await self._request('DELETE', f'/api/tasks/{task_id}')
    
    async def complete_task(self, task_id: str) -> Dict[str, Any]:
        """Mark a task as completed"""
        return await self._request('POST', f'/api/tasks/{task_id}/complete')
    
    async def get_next_tasks(self, hours: int = 48) -> List[Dict[str, Any]]:
        """Get tasks due in the next N hours"""
        return await self._request('GET', f'/api/tasks/next', params={'hours': hours})
    
    # Category operations
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories"""
        return await self._request('GET', '/api/categories')
    
    async def create_category(self, category_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new category"""
        return await self._request('POST', '/api/categories', json=category_data)
    
    async def delete_category(self, category_id: str) -> None:
        """Delete a category"""
        await self._request('DELETE', f'/api/categories/{category_id}')
    
    # Tag operations
    async def get_tags(self) -> List[Dict[str, Any]]:
        """Get all tags"""
        return await self._request('GET', '/api/tags')
    
    async def create_tag(self, tag_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new tag"""
        return await self._request('POST', '/api/tags', json=tag_data)
    
    async def delete_tag(self, tag_id: str) -> None:
        """Delete a tag"""
        await self._request('DELETE', f'/api/tags/{tag_id}')
    
    # Notification operations
    async def trigger_notifications(self) -> Dict[str, Any]:
        """Trigger notification cron job"""
        return await self._request('POST', '/api/cron/notifications')
    
    async def get_notification_logs(self) -> List[Dict[str, Any]]:
        """Get notification logs"""
        return await self._request('GET', '/api/notifications/logs')
    
    # Settings operations
    async def get_settings(self) -> Dict[str, Any]:
        """Get current settings"""
        return await self._request('GET', '/api/settings')
    
    async def update_settings(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update settings"""
        return await self._request('PUT', '/api/settings', json=settings_data)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
