"""
Модуль для работы с Avito API
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import os


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
        """Устанавливает токен доступа"""
        self.auth.access_token = token
    
    def _get_headers(self) -> Dict[str, str]:
        """Формирует заголовки для запросов"""
        token = self.auth.get_valid_token()
        if not token:
            raise Exception("Токен доступа не установлен")
        
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def get_items(self, user_id: str, status: str = None, page: int = 1, per_page: int = 50) -> Dict:
        """
        Получение списка объявлений пользователя
        Документация: https://api.avito.ru/core/v1/accounts/{user_id}/items
        """
        endpoint = f"core/v1/accounts/{user_id}/items"
        
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
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Ошибка API: {response.status_code}")
                print(f"Ответ: {response.text}")
                return {"items": [], "total_pages": 1}
                
        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")
            return {"items": [], "total_pages": 1}
    
    def get_item_stats(self, user_id: str, item_id: str) -> Dict:
        """
        Получение статистики по объявлению
        Документация: https://api.avito.ru/core/v1/accounts/{user_id}/items/{item_id}/stats
        """
        endpoint = f"core/v1/accounts/{user_id}/items/{item_id}/stats"
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Ошибка получения статистики: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Ошибка запроса статистики: {e}")
            return {}
    
    def get_items_stats(self, user_id: str, item_ids: List[str]) -> Dict:
        """
        Получение статистики по нескольким объявлениям
        """
        endpoint = f"core/v1/accounts/{user_id}/items/stats"
        
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                headers=self._get_headers(),
                json={"item_ids": item_ids}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Ошибка получения статистики: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Ошибка запроса статистики: {e}")
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
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Ошибка создания: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")
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
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Ошибка обновления: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")
            return {}
    
    def delete_item(self, user_id: str, item_id: str) -> bool:
        """Удаление объявления"""
        endpoint = f"core/v1/accounts/{user_id}/items/{item_id}"
        
        try:
            response = requests.delete(
                f"{self.base_url}{endpoint}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"❌ Ошибка удаления: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")
            return False