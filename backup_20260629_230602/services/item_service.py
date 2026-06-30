"""
Сервис для работы с объявлениями
"""

from typing import List, Dict, Optional
from PyQt5.QtCore import QObject

from database.repository import ItemRepository
from api.sync_service import SyncService
from core.event_bus import EventBus


class ItemService(QObject):
    """Сервис для управления объявлениями"""
    
    def __init__(self, item_repo: ItemRepository, sync_service: SyncService, event_bus: EventBus):
        super().__init__()
        self.item_repo = item_repo
        self.sync_service = sync_service
        self.event_bus = event_bus
    
    def load_items(self, project_id: int, filters: Dict = None) -> List[Dict]:
        """Загрузка объявлений с фильтрами"""
        items = self.item_repo.get_by_project(project_id)
        return [item.__dict__ for item in items]
    
    def sync_items(self, project_id: int) -> int:
        """Синхронизация объявлений"""
        return self.sync_service.sync_items(project_id)
    
    def get_stats(self, project_id: int) -> Dict:
        """Получение статистики"""
        items = self.item_repo.get_by_project(project_id)
        
        return {
            "total": len(items),
            "active": len([i for i in items if i.status == "active"]),
            "inactive": len([i for i in items if i.status == "inactive"]),
            "total_views": sum(i.views for i in items),
            "total_calls": sum(i.calls for i in items),
        }
