"""
Модуль для работы с Avito API
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import os
from core.session import Session   # <-- добавлен импорт


class AvitoAuth:
    """Класс для авторизации в Avito API"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri or "http://localhost:8080"
        self.token_url = "https://api.avito.ru/token"
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
    
    def get_valid_token(self) -> Optional[str]:
        """Возвращает действительный токен"""
        return self.access_token


class AvitoAPI:
    """Клиент для работы с Avito API"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.avito.ru/"
        self.auth = AvitoAuth(client_id, client_secret)
    
    def set_access_token(self, token: str):
        """Устанавливает токен доступа для API запросов"""
        self.auth.access_token = token
        print("✅ Токен установлен в AvitoAPI")
    
    def _get_headers(self) -> Dict[str, str]:
        """Формирует заголовки для запросов"""
        token = Session.access_token if hasattr(Session, 'access_token') else None
        if not token:
            raise Exception("❌ Нет токена. Сначала войдите через UI")
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    
    
    
    def get_items(self, status: str = None, page: int = 1, per_page: int = 50) -> Dict:
        """
        Получение списка объявлений авторизованного пользователя.
        """
        endpoint = "core/v1/items"
        params = {
            "page": page,
            "per_page": min(per_page, 100)
        }
        if status:
            params["status"] = status

        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка API при получении объявлений: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"   Ответ сервера: {e.response.text}")
            return {"resources": []}



    
    def get_item_stats(self, user_id: str, item_id: str) -> Dict:
        """Получение статистики по объявлению"""
        endpoint = f"core/v1/accounts/{user_id}/items/{item_id}/stats"
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка получения статистики: {e}")
            return {}
    
    def get_items_stats(self, user_id: str, item_ids: List[str]) -> Dict:
        """Получение статистики по нескольким объявлениям"""
        endpoint = f"core/v1/accounts/{user_id}/items/stats"
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                headers=self._get_headers(),
                json={"item_ids": item_ids}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка получения статистики: {e}")
            return {}
    
    def create_item(self, user_id: str, item_data: Dict) -> Dict:
        """Создание объявления"""
        endpoint = f"core/v1/accounts/{user_id}/items"
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                headers=self._get_headers(),
                json=item_data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка создания: {e}")
            return {}
    
    def update_item(self, user_id: str, item_id: str, item_data: Dict) -> Dict:
        """Обновление объявления"""
        endpoint = f"core/v1/accounts/{user_id}/items/{item_id}"
        try:
            response = requests.put(
                f"{self.base_url}{endpoint}",
                headers=self._get_headers(),
                json=item_data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка обновления: {e}")
            return {}
    
    def delete_item(self, user_id: str, item_id: str) -> bool:
        """Удаление объявления"""
        endpoint = f"core/v1/accounts/{user_id}/items/{item_id}"
        try:
            response = requests.delete(
                f"{self.base_url}{endpoint}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка удаления: {e}")
            return False
    
    def get_token_client_credentials(self) -> Optional[str]:
        """Получение токена через Client Credentials"""
        try:
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            response = requests.post("https://api.avito.ru/token", data=data)
            response.raise_for_status()
            tokens = response.json()
            self.auth.access_token = tokens.get("access_token")
            return self.auth.access_token
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка получения токена: {e}")
            return None
    
    def get_my_items(self, user_id: str):
        """Получение своих объявлений (для Client Credentials)"""
        # Проверяем токен заранее
        token = self.get_token_client_credentials()
        if not token:
            token = getattr(Session, 'access_token', None)
            if not token:
                raise Exception("❌ Нет токена. Сначала войдите через UI")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        try:
            response = requests.get(
                f"{self.base_url}core/v1/accounts/{user_id}/items",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка: {e}")
            return {"items": []}