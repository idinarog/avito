"""
Управление конфигурацией приложения
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from PyQt5.QtCore import QSettings


class ConfigManager:
    """
    Менеджер конфигурации
    """
    
    def __init__(self):
        # Загружаем .env файл
        env_path = Path('.env')
        if env_path.exists():
            load_dotenv(env_path)
        
        # Qt настройки
        self.qt_settings = QSettings("AvitoCommander", "AvitoCommander")
        
        # Загружаем конфиги
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Загружает конфигурацию"""
        return {
            # Avito API
            "avito_client_id": os.getenv("AVITO_CLIENT_ID", ""),
            "avito_client_secret": os.getenv("AVITO_CLIENT_SECRET", ""),
            "avito_redirect_uri": os.getenv("AVITO_REDIRECT_URI", "http://localhost:8080"),
            
            # База данных
            "db_path": self.qt_settings.value("database/path", "avito_commander.db"),
            
            # Telegram
            "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
            "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
            
            # Приложение
            "app_name": "Avito Commander",
            "app_version": "0.2.0",
            "theme": self.qt_settings.value("theme", "dark"),
            
            # Настройки синхронизации
            "auto_sync": self.qt_settings.value("sync/auto", True, type=bool),
            "sync_interval": self.qt_settings.value("sync/interval", 3600, type=int),
        }
    
    def get(self, key: str, default=None):
        """Получить значение конфигурации"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """Установить значение и сохранить в Qt Settings"""
        self.qt_settings.setValue(key, value)
        self.config[key] = value
    
    def get_avito_credentials(self) -> tuple:
        """Получить учетные данные для Avito"""
        return (
            self.get("avito_client_id"),
            self.get("avito_client_secret")
        )
    
    def get_telegram_credentials(self) -> tuple:
        """Получить учетные данные для Telegram"""
        return (
            self.get("telegram_bot_token"),
            self.get("telegram_chat_id")
        )
