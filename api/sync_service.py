"""
Сервис синхронизации данных с Avito API
"""

from typing import Optional, Dict, List, Any
from database.repository import ItemRepository


class SyncService:
    """Сервис для синхронизации данных с Avito API"""

    def __init__(self, db, avito_api, event_bus=None):
        self.db = db
        self.avito_api = avito_api
        self.event_bus = event_bus
        self.user_id_avito = None
        self.token = None

    def set_access_token(self, token: str):
        """Устанавливает токен доступа"""
        self.token = token
        self.avito_api.set_access_token(token)

    def set_user(self, user_id_avito: str):
        """Устанавливает ID пользователя"""
        self.user_id_avito = user_id_avito

    def sync_all_items(self, user_id_avito: str) -> int:
        """
        Загружает все объявления пользователя из Avito и сохраняет их в БД.
        Возвращает количество загруженных объявлений.
        """
        try:
            print(f"🔄 Начинаю синхронизацию для user_id={user_id_avito}...")
            response = self.avito_api.get_items()            
            # Если ответ содержит ошибку, выведем её
            if isinstance(response, dict) and response.get('error'):
                print(f"❌ Ошибка API: {response}")
                return 0

            items = response.get("resources", [])
            if not items:
                print("ℹ️ Нет объявлений для синхронизации.")
                return 0

            item_repo = ItemRepository(self.db)

            count = 0
            for item_data in items:
                item = {
                    'item_id': item_data.get('id'),
                    'title': item_data.get('title'),
                    'price': item_data.get('price'),
                    'status': item_data.get('status'),
                    'user_id_avito': user_id_avito,
                }
                # Проверяем существование
                existing = item_repo.get_by_item_id(item_data.get('id'))
                if existing:
                    item_repo.update(item_data.get('id'), item)
                else:
                    item_repo.create(item)
                count += 1

            print(f"✅ Синхронизировано {count} объявлений.")
            return count
        except Exception as e:
            print(f"❌ Ошибка синхронизации: {e}")
            return 0

    # Здесь могут быть другие методы (например, sync_stats, sync_projects и т.д.)
    # Если они были в вашем файле, добавьте их обратно ниже