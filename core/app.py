"""
Главный класс приложения - синглтон
"""

import sys
import os
from typing import Optional

# Явно загружаем .env до всего остального
from dotenv import load_dotenv
# Ищем .env в корне проекта (на уровень выше core)
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

# Дополнительная проверка: выведем, что загрузили
print("📁 .env загружен из:", dotenv_path)
print("🔑 Client ID:", os.getenv("avito_client_id"))
print("🔐 Client Secret:", os.getenv("avito_client_secret")[:10] + "..." if os.getenv("avito_client_secret") else "None")

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from .config_manager import ConfigManager
from .event_bus import EventBus
from database.migration import MigrationManager
from database.repository import UserRepository, ProjectRepository, ItemRepository
from api.avito_api import AvitoAPI
from api.sync_service import SyncService
from services.item_service import ItemService
from services.project_service import ProjectService
from services.analytics_service import AnalyticsService
from services.notification_service import NotificationService


class Application:
    """
    Главный класс приложения - синглтон
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True

        print("🚀 Инициализация приложения...")

        # Конфигурация
        self.config = ConfigManager()

        # Шина событий
        self.event_bus = EventBus()

        # Компоненты (будут инициализированы позже)
        self.db = None
        self.user_repo = None
        self.project_repo = None
        self.item_repo = None
        self.avito_api = None
        self.sync_service = None
        self.item_service = None
        self.project_service = None
        self.analytics_service = None
        self.notification_service = None

        # Текущие данные
        self.current_user = None
        self.current_project = None
        self._qt_app = None

        print("✅ Конфигурация загружена")

    def init_database(self):
        """Инициализация базы данных"""
        print("📁 Инициализация базы данных...")

        db_path = self.config.get("db_path")
        migration = MigrationManager(db_path)
        self.db = migration.run_migrations()

        # Инициализация репозиториев
        self.user_repo = UserRepository(self.db)
        self.project_repo = ProjectRepository(self.db)
        self.item_repo = ItemRepository(self.db)

        print("✅ База данных готова")
        return self

    def init_services(self):
        """Инициализация сервисов"""
        print("🔧 Инициализация сервисов...")

        # Берём клиентские данные напрямую из переменных окружения (они уже загружены)
        client_id = os.getenv("avito_client_id")
        client_secret = os.getenv("avito_client_secret")

        # Если не нашли, пробуем через ConfigManager (на случай, если там есть)
        if not client_id or not client_secret:
            client_id, client_secret = self.config.get_avito_credentials()

        print(f"🔑 Используется Client ID: {client_id}")

        self.avito_api = AvitoAPI(client_id, client_secret)

        # Сервис синхронизации
        self.sync_service = SyncService(self.db, self.avito_api, self.event_bus)

        # Бизнес-сервисы
        self.item_service = ItemService(self.item_repo, self.sync_service, self.event_bus)
        self.project_service = ProjectService(self.project_repo, self.event_bus)
        self.analytics_service = AnalyticsService(self.item_repo)
        self.notification_service = NotificationService(self.config)

        print("✅ Все сервисы готовы")
        return self

    def init_app(self):
        """Полная инициализация приложения"""
        self.init_database()
        self.init_services()
        return self

    def set_access_token(self, token: str):
        """Устанавливает токен доступа для всех сервисов"""
        if self.sync_service:
            self.sync_service.set_access_token(token)
        if self.avito_api:
            self.avito_api.set_access_token(token)
        print("✅ Токен доступа установлен")

    def start(self):
        """Запуск приложения"""
        from ui.main_window import MainWindow
        from ui.login_dialog import LoginDialog

        # Создаем Qt приложение
        self._qt_app = QApplication(sys.argv)

        # Настройка стиля
        if self.config.get("theme") == "dark":
            self._qt_app.setStyle("Fusion")

        # Проверяем, есть ли сохраненный пользователь
        user_id = self.config.get("user/current_id")

        if user_id:
            user = self.user_repo.get_by_id(int(user_id))
            if user:
                self.current_user = user
                self.show_main_window()
                return self._qt_app.exec_()

        # Показываем окно входа
        login_dialog = LoginDialog(self)
        if login_dialog.exec_() == LoginDialog.Accepted:
            self.current_user = login_dialog.user
            self.config.set("user/current_id", self.current_user.id)
            self.show_main_window()
        else:
            sys.exit(0)

        return self._qt_app.exec_()

    def show_main_window(self):
        """Показывает главное окно"""
        from ui.main_window import MainWindow

        self.main_window = MainWindow(self)
        self.main_window.show()

        # Отправляем событие
        self.event_bus.emit("user_logged_in", self.current_user)

    def get_current_user(self):
        """Возвращает текущего пользователя"""
        return self.current_user

    def get_current_project(self):
        """Возвращает текущий проект"""
        return self.current_project

    def set_current_project(self, project):
        """Устанавливает текущий проект"""
        self.current_project = project
        self.event_bus.emit("project_changed", project)

    def quit(self):
        """Выход из приложения"""
        if self._qt_app:
            self._qt_app.quit()


# Глобальный экземпляр приложения
app = Application()