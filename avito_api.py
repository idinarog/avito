"""
Модуль для работы с Avito API
Содержит классы для авторизации и выполнения запросов к API Авито
"""

import requests  # Для отправки HTTP запросов
import json      # Для работы с JSON данными
import time      # Для работы со временем (таймауты)
from datetime import datetime, timedelta  # Для работы с датами
from typing import Optional, Dict, List, Any  # Для аннотаций типов
import os       # Для работы с файловой системой


class AvitoAuth:
    """
    Класс для авторизации в Avito API через OAuth 2.0
    Управляет получением и обновлением токенов доступа
    """
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Инициализация авторизации
        
        Аргументы:
            client_id: Идентификатор приложения (получаем в кабинете разработчика)
            client_secret: Секретный ключ приложения
            redirect_uri: URI для перенаправления после авторизации
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
        # Базовый URL для всех запросов к API Авито
        self.base_url = "https://api.avito.ru/"
        
        # URL для получения токена
        self.token_url = "https://api.avito.ru/token"
        
        # Храним токены в памяти
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None  # Время истечения токена
        
        # Пытаемся загрузить сохраненные токены при создании объекта
        self.load_tokens()
    
    def get_auth_url(self) -> str:
        """
        Генерирует URL для авторизации пользователя
        Пользователь должен перейти по этой ссылке в браузере
        
        Возвращает:
            Строку с URL для авторизации
        """
        # Параметры для OAuth запроса
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",  # Запрашиваем код авторизации
            "scope": "read write"     # Какие права запрашиваем
        }
        
        # Собираем URL с параметрами
        # Авито предоставляет отдельный URL для авторизации пользователя
        auth_url = "https://www.avito.ru/oauth/authorize"
        
        # Добавляем параметры к URL
        from urllib.parse import urlencode
        return f"{auth_url}?{urlencode(params)}"
    
    def get_tokens_from_code(self, authorization_code: str) -> bool:
        """
        Обменивает код авторизации на токены доступа
        
        Аргументы:
            authorization_code: Код, полученный после авторизации пользователя
            
        Возвращает:
            True если токены получены успешно, иначе False
        """
        # Подготавливаем данные для запроса
        data = {
            "grant_type": "authorization_code",  # Тип авторизации
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": authorization_code
        }
        
        try:
            # Отправляем POST запрос к серверу Авито
            response = requests.post(self.token_url, data=data)
            
            # Проверяем, успешно ли выполнен запрос
            if response.status_code == 200:
                # Преобразуем ответ из JSON в словарь Python
                tokens = response.json()
                
                # Сохраняем полученные токены
                self.access_token = tokens.get("access_token")
                self.refresh_token = tokens.get("refresh_token")
                
                # Вычисляем время истечения токена
                # Обычно токен действует 3600 секунд (1 час)
                expires_in = tokens.get("expires_in", 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                # Сохраняем токены в файл для использования в будущем
                self.save_tokens()
                return True
            else:
                print(f"Ошибка получения токенов: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"Ошибка при получении токенов: {str(e)}")
            return False
    
    def refresh_access_token(self) -> bool:
        """
        Обновляет access_token используя refresh_token
        Когда access_token истекает, используем refresh_token для получения нового
        
        Возвращает:
            True если токен обновлен успешно, иначе False
        """
        if not self.refresh_token:
            print("Нет refresh_token для обновления")
            return False
        
        # Подготавливаем данные для запроса
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token
        }
        
        try:
            response = requests.post(self.token_url, data=data)
            
            if response.status_code == 200:
                tokens = response.json()
                
                # Обновляем токены
                self.access_token = tokens.get("access_token")
                self.refresh_token = tokens.get("refresh_token")
                
                expires_in = tokens.get("expires_in", 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                # Сохраняем обновленные токены
                self.save_tokens()
                return True
            else:
                print(f"Ошибка обновления токена: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Ошибка при обновлении токена: {str(e)}")
            return False
    
    def is_token_valid(self) -> bool:
        """
        Проверяет, действителен ли текущий access_token
        
        Возвращает:
            True если токен действителен, иначе False
        """
        if not self.access_token:
            return False
        
        if not self.token_expires_at:
            return False
        
        # Даем запас в 60 секунд, чтобы не использовать токен на грани истечения
        return datetime.now() < (self.token_expires_at - timedelta(seconds=60))
    
    def save_tokens(self):
        """
        Сохраняет токены в файл tokens.json
        Это позволяет не вводить данные заново при перезапуске программы
        """
        tokens_data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None
        }
        
        try:
            with open("tokens.json", "w", encoding="utf-8") as f:
                json.dump(tokens_data, f, indent=4, ensure_ascii=False)
            print("Токены сохранены в tokens.json")
        except Exception as e:
            print(f"Ошибка сохранения токенов: {str(e)}")
    
    def load_tokens(self):
        """
        Загружает токены из файла tokens.json
        Используется при запуске программы для восстановления сессии
        """
        try:
            if os.path.exists("tokens.json"):
                with open("tokens.json", "r", encoding="utf-8") as f:
                    tokens_data = json.load(f)
                
                self.access_token = tokens_data.get("access_token")
                self.refresh_token = tokens_data.get("refresh_token")
                
                expires_at_str = tokens_data.get("expires_at")
                if expires_at_str:
                    self.token_expires_at = datetime.fromisoformat(expires_at_str)
                
                print("Токены загружены из tokens.json")
                return True
        except Exception as e:
            print(f"Ошибка загрузки токенов: {str(e)}")
        
        return False
    
    def get_valid_token(self) -> Optional[str]:
        """
        Возвращает действительный access_token
        Если токен истек - пытается обновить его автоматически
        
        Возвращает:
            Строку с токеном или None в случае ошибки
        """
        # Проверяем, действителен ли текущий токен
        if self.is_token_valid():
            return self.access_token
        
        # Если токен не действителен, пробуем обновить
        print("Токен истек, пробуем обновить...")
        if self.refresh_access_token():
            return self.access_token
        else:
            print("Не удалось обновить токен. Требуется повторная авторизация.")
            return None


class AvitoAPI:
    """
    Основной класс для работы с Avito API
    Содержит все методы для управления объявлениями
    """
    
    def __init__(self, auth: AvitoAuth):
        """
        Инициализация API клиента
        
        Аргументы:
            auth: Объект AvitoAuth для управления авторизацией
        """
        self.auth = auth
        self.base_url = "https://api.avito.ru/"
        
        # Максимальное количество объявлений в одном запросе
        self.per_page = 50
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Формирует заголовки для HTTP запросов
        Добавляет access_token для авторизации
        
        Возвращает:
            Словарь с заголовками
        """
        token = self.auth.get_valid_token()
        if not token:
            raise Exception("Нет действительного токена доступа")
        
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """
        Универсальный метод для выполнения HTTP запросов к API Авито
        
        Аргументы:
            method: HTTP метод (GET, POST, PUT, DELETE)
            endpoint: Конечная точка API (например, "/core/v1/items")
            data: Данные для отправки в теле запроса
            params: Параметры URL (например, для фильтрации)
            
        Возвращает:
            Ответ от API в виде словаря
            
        Вызывает исключение при ошибке
        """
        url = f"{self.base_url}{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        try:
            # Отправляем запрос в зависимости от метода
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, params=params)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, params=params)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=headers, json=data, params=params)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"Неподдерживаемый метод: {method}")
            
            # Проверяем статус ответа
            if response.status_code == 401:
                # Если токен не действителен, пробуем обновить и повторить запрос
                if self.auth.refresh_access_token():
                    # Повторяем запрос с новым токеном
                    headers = self._get_headers()
                    response = requests.request(method, url, headers=headers, json=data, params=params)
                else:
                    raise Exception("Требуется повторная авторизация")
            
            # Проверяем, успешно ли выполнен запрос
            if response.status_code >= 400:
                error_message = f"Ошибка API: {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_message += f" - {error_data['error']}"
                except:
                    pass
                raise Exception(error_message)
            
            # Возвращаем ответ в виде JSON
            if response.content:
                return response.json()
            else:
                return {}
                
        except requests.RequestException as e:
            raise Exception(f"Ошибка соединения с API: {str(e)}")
    
    # ============================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С ОБЪЯВЛЕНИЯМИ
    # ============================================================
    
    def get_items(self, user_id: str, status: str = None, page: int = 1, per_page: int = 50) -> Dict:
        """
        Получение списка объявлений пользователя
        
        Аргументы:
            user_id: ID пользователя в Avito
            status: Фильтр по статусу (active, inactive, blocked и т.д.)
            page: Номер страницы (начинается с 1)
            per_page: Количество объявлений на странице (макс 100)
            
        Возвращает:
            Словарь с объявлениями и информацией о пагинации
        """
        endpoint = f"/core/v1/accounts/{user_id}/items"
        
        params = {
            "page": page,
            "per_page": min(per_page, 100)  # Ограничиваем максимум 100
        }
        
        if status:
            params["status"] = status
        
        return self._make_request("GET", endpoint, params=params)
    
    def get_item(self, user_id: str, item_id: str) -> Dict:
        """
        Получение детальной информации об одном объявлении
        
        Аргументы:
            user_id: ID пользователя
            item_id: ID объявления
            
        Возвращает:
            Детальную информацию об объявлении
        """
        endpoint = f"/core/v1/accounts/{user_id}/items/{item_id}"
        return self._make_request("GET", endpoint)
    
    def create_item(self, user_id: str, item_data: Dict) -> Dict:
        """
        Создание нового объявления
        
        Аргументы:
            user_id: ID пользователя
            item_data: Данные объявления (заголовок, описание, цена и т.д.)
            
        Возвращает:
            Информацию о созданном объявлении
        """
        endpoint = f"/core/v1/accounts/{user_id}/items"
        return self._make_request("POST", endpoint, data=item_data)
    
    def update_item(self, user_id: str, item_id: str, item_data: Dict) -> Dict:
        """
        Обновление существующего объявления
        
        Аргументы:
            user_id: ID пользователя
            item_id: ID объявления
            item_data: Обновленные данные
            
        Возвращает:
            Обновленную информацию об объявлении
        """
        endpoint = f"/core/v1/accounts/{user_id}/items/{item_id}"
        return self._make_request("PUT", endpoint, data=item_data)
    
    def delete_item(self, user_id: str, item_id: str) -> bool:
        """
        Удаление объявления
        
        Аргументы:
            user_id: ID пользователя
            item_id: ID объявления
            
        Возвращает:
            True если удаление успешно
        """
        endpoint = f"/core/v1/accounts/{user_id}/items/{item_id}"
        try:
            self._make_request("DELETE", endpoint)
            return True
        except Exception as e:
            print(f"Ошибка удаления: {str(e)}")
            return False
    
    def update_item_status(self, user_id: str, item_id: str, status: str) -> Dict:
        """
        Изменение статуса объявления (активация/деактивация)
        
        Аргументы:
            user_id: ID пользователя
            item_id: ID объявления
            status: Новый статус ("active", "inactive")
            
        Возвращает:
            Обновленную информацию
        """
        endpoint = f"/core/v1/accounts/{user_id}/items/{item_id}"
        data = {"status": status}
        return self._make_request("PATCH", endpoint, data=data)
    
    # ============================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ СО СТАТИСТИКОЙ
    # ============================================================
    
    def get_item_stats(self, user_id: str, item_id: str) -> Dict:
        """
        Получение статистики по конкретному объявлению
        
        Аргументы:
            user_id: ID пользователя
            item_id: ID объявления
            
        Возвращает:
            Статистику: просмотры, звонки, избранные и т.д.
        """
        endpoint = f"/core/v1/accounts/{user_id}/items/{item_id}/stats"
        return self._make_request("GET", endpoint)
    
    def get_items_stats(self, user_id: str, item_ids: List[str]) -> Dict:
        """
        Получение статистики по нескольким объявлениям
        
        Аргументы:
            user_id: ID пользователя
            item_ids: Список ID объявлений
            
        Возвращает:
            Статистику по всем указанным объявлениям
        """
        endpoint = f"/core/v1/accounts/{user_id}/items/stats"
        data = {"item_ids": item_ids}
        return self._make_request("POST", endpoint, data=data)
    
    # ============================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С СООБЩЕНИЯМИ
    # ============================================================
    
    def get_messages(self, user_id: str, item_id: str = None, page: int = 1) -> Dict:
        """
        Получение списка сообщений по объявлению
        
        Аргументы:
            user_id: ID пользователя
            item_id: ID объявления (если None - все сообщения)
            page: Номер страницы
            
        Возвращает:
            Список сообщений
        """
        if item_id:
            endpoint = f"/core/v1/accounts/{user_id}/items/{item_id}/chats"
        else:
            endpoint = f"/core/v1/accounts/{user_id}/chats"
        
        params = {"page": page}
        return self._make_request("GET", endpoint, params=params)
    
    def send_message(self, user_id: str, chat_id: str, message: str) -> Dict:
        """
        Отправка сообщения в чат
        
        Аргументы:
            user_id: ID пользователя
            chat_id: ID чата
            message: Текст сообщения
            
        Возвращает:
            Информацию об отправленном сообщении
        """
        endpoint = f"/core/v1/accounts/{user_id}/chats/{chat_id}/messages"
        data = {"message": message}
        return self._make_request("POST", endpoint, data=data)