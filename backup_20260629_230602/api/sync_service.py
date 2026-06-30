"""
Сервис синхронизации с Avito API
"""

from typing import List, Dict, Optional
from datetime import datetime

from database.repository import ItemRepository
from api.avito_api import AvitoAPI
from core.event_bus import EventBus


class SyncService:
    """Сервис для синхронизации данных с Avito"""
    
    def __init__(self, db, avito_api: AvitoAPI, event_bus: EventBus):
        self.db = db
        self.avito_api = avito_api
        self.event_bus = event_bus
        self.item_repo = ItemRepository(db)
        self.user_id = None
        self.last_sync_time = None
    
    def set_user(self, user_id: str):
        """Устанавливает ID пользователя"""
        self.user_id = user_id
    
    def set_access_token(self, token: str):
        """Устанавливает токен доступа"""
        self.avito_api.set_access_token(token)
    
    def sync_items(self, project_id: int) -> List[Dict]:
        """
        Синхронизация объявлений с Avito
        Загружает реальные данные из API
        """
        if not self.user_id:
            raise ValueError("User ID не установлен")
        
        self.event_bus.emit("sync_started")
        
        try:
            print(f"🔄 Загрузка объявлений для пользователя {self.user_id}...")
            
            # Получаем объявления из API
            response = self.avito_api.get_items(self.user_id)
            items = response.get("items", [])
            
            print(f"📦 Получено {len(items)} объявлений")
            
            # Получаем статистику для всех объявлений
            if items:
                item_ids = [str(item.get("id")) for item in items if item.get("id")]
                if item_ids:
                    stats_response = self.avito_api.get_items_stats(self.user_id, item_ids)
                    stats_map = stats_response.get("stats", {})
                    
                    # Обогащаем объявления статистикой
                    for item in items:
                        item_id = str(item.get("id"))
                        if item_id in stats_map:
                            item["stats"] = stats_map[item_id]
            
            # Сохраняем в БД
            count = 0
            for item_data in items:
                self.item_repo.save_from_api(project_id, item_data)
                count += 1
            
            self.last_sync_time = datetime.now()
            self.event_bus.emit("sync_finished", count)
            
            print(f"✅ Синхронизировано {count} объявлений")
            return items
            
        except Exception as e:
            error_msg = f"Ошибка синхронизации: {str(e)}"
            print(f"❌ {error_msg}")
            self.event_bus.emit("error_occurred", error_msg)
            raise
    
    def get_item_stats(self, item_id: str) -> Dict:
        """Получение статистики для одного объявления"""
        if not self.user_id:
            return {}
        
        try:
            return self.avito_api.get_item_stats(self.user_id, item_id)
        except Exception as e:
            print(f"❌ Ошибка получения статистики: {e}")
            return {}
    
    def create_item(self, user_id: str, item_data: Dict) -> Dict:
        """Создание объявления через API"""
        return self.avito_api.create_item(user_id, item_data)
    
    def update_item(self, user_id: str, item_id: str, item_data: Dict) -> Dict:
        """Обновление объявления через API"""
        return self.avito_api.update_item(user_id, item_id, item_data)
    
    def delete_item(self, user_id: str, item_id: str) -> bool:
        """Удаление объявления через API"""
        return self.avito_api.delete_item(user_id, item_id)
    
    def get_last_sync_time(self) -> Optional[datetime]:
        """Возвращает время последней синхронизации"""
        return self.last_sync_time