"""
Сервис для аналитики
"""

from database.repository import ItemRepository


class AnalyticsService:
    """Сервис для аналитики"""
    
    def __init__(self, item_repo: ItemRepository):
        self.item_repo = item_repo
    
    def get_dashboard_data(self, project_id: int) -> dict:
        """Получение данных для дашборда"""
        items = self.item_repo.get_by_project(project_id)
        
        return {
            "total_items": len(items),
            "active_items": len([i for i in items if i.status == "active"]),
            "total_views": sum(i.views for i in items),
            "total_calls": sum(i.calls for i in items),
        }
