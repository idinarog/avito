#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для автоматического создания структуры проекта и файлов
Запустите: python3 setup_project.py
"""

import os
import sys
from pathlib import Path

# Содержимое файлов
FILES = {
    # ===== CORE =====
    "core/__init__.py": '''"""
Ядро приложения
"""
from .app import Application
from .config_manager import ConfigManager
from .event_bus import EventBus

__all__ = ['Application', 'ConfigManager', 'EventBus']
''',

    "core/config_manager.py": '''"""
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
''',

    "core/event_bus.py": '''"""
Шина событий для коммуникации между компонентами
"""

from typing import Dict, List, Callable, Any
from PyQt5.QtCore import QObject, pyqtSignal


class EventBus(QObject):
    """
    Центральная шина событий
    """
    
    # Сигналы для разных типов событий
    user_logged_in = pyqtSignal(object)  # user
    user_logged_out = pyqtSignal()
    project_changed = pyqtSignal(object)  # project
    items_updated = pyqtSignal()
    sync_started = pyqtSignal()
    sync_finished = pyqtSignal(int)  # count
    error_occurred = pyqtSignal(str)
    notification = pyqtSignal(str, str)  # title, message
    
    def __init__(self):
        super().__init__()
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, callback: Callable):
        """
        Подписаться на событие
        
        Аргументы:
            event_type: Тип события
            callback: Функция-обработчик
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Отписаться от события"""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)
    
    def emit(self, event_type: str, data: Any = None):
        """
        Отправить событие
        
        Аргументы:
            event_type: Тип события
            data: Данные события
        """
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Ошибка в обработчике {event_type}: {e}")
        
        # Отправляем через Qt сигналы
        if event_type == "user_logged_in":
            self.user_logged_in.emit(data)
        elif event_type == "user_logged_out":
            self.user_logged_out.emit()
        elif event_type == "project_changed":
            self.project_changed.emit(data)
        elif event_type == "items_updated":
            self.items_updated.emit()
        elif event_type == "sync_started":
            self.sync_started.emit()
        elif event_type == "sync_finished":
            self.sync_finished.emit(data)
        elif event_type == "error_occurred":
            self.error_occurred.emit(data)
        elif event_type == "notification":
            title, message = data
            self.notification.emit(title, message)
''',

    "core/app.py": '''"""
Главный класс приложения
"""

import sys
from typing import Optional

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
        
        # API клиент
        client_id, client_secret = self.config.get_avito_credentials()
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
            self.config.set("user/current_id", self.current_user['id'])
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
''',

    # ===== DATABASE =====
    "database/__init__.py": '''"""
Модуль базы данных
"""
from .models import Base, User, Project, Item, SyncLog, Favorite, Settings
from .repository import UserRepository, ProjectRepository, ItemRepository
from .migration import MigrationManager

__all__ = [
    'Base', 'User', 'Project', 'Item', 'SyncLog', 'Favorite', 'Settings',
    'UserRepository', 'ProjectRepository', 'ItemRepository',
    'MigrationManager'
]
''',

    "database/models.py": '''"""
Модели базы данных с использованием SQLAlchemy ORM
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    user_id_avito = Column(String(50), nullable=False)
    access_token = Column(String(500))
    refresh_token = Column(String(500))
    token_expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)
    
    # Связи
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("Settings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)
    
    # Связи
    user = relationship("User", back_populates="projects")
    items = relationship("Item", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"


class Item(Base):
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    item_id_avito = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    price = Column(Integer)
    status = Column(String(50))
    views = Column(Integer, default=0)
    calls = Column(Integer, default=0)
    favorites = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)
    
    # Связи
    project = relationship("Project", back_populates="items")
    
    def __repr__(self):
        return f"<Item(id={self.id}, title='{self.title[:30]}...')>"


class SyncLog(Base):
    __tablename__ = 'sync_log'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    item_id_avito = Column(String(50))
    action = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<SyncLog(id={self.id}, action='{self.action}', status='{self.status}')>"


class Favorite(Base):
    __tablename__ = 'favorites'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    item_id_avito = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Favorite(user_id={self.user_id}, item_id_avito='{self.item_id_avito}')>"


class Settings(Base):
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    theme = Column(String(20), default='dark')
    auto_sync = Column(Boolean, default=True)
    sync_interval = Column(Integer, default=3600)
    notifications = Column(Boolean, default=True)
    
    # Связи
    user = relationship("User", back_populates="settings")


class DatabaseManager:
    """Менеджер базы данных"""
    
    def __init__(self, db_path="avito_commander.db"):
        self.db_path = db_path
        self.engine = None
        self.Session = None
        
    def init_db(self):
        """Инициализация базы данных"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        print(f"✅ База данных инициализирована: {self.db_path}")
        return self
    
    def get_session(self):
        """Получить сессию для работы с БД"""
        if not self.Session:
            self.init_db()
        return self.Session()
    
    def close(self):
        """Закрыть соединение с БД"""
        if self.engine:
            self.engine.dispose()
''',

    "database/repository.py": '''"""
Репозиторий для работы с базой данных
"""

from sqlalchemy.exc import IntegrityError
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from .models import DatabaseManager, User, Project, Item, SyncLog, Favorite, Settings


class UserRepository:
    """Репозиторий для работы с пользователями"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def create(self, username: str, user_id_avito: str, 
               access_token: str = None, refresh_token: str = None) -> Optional[User]:
        """Создание нового пользователя"""
        session = self.db.get_session()
        try:
            user = User(
                username=username,
                user_id_avito=user_id_avito,
                access_token=access_token,
                refresh_token=refresh_token
            )
            session.add(user)
            session.commit()
            
            # Создаем настройки для пользователя
            settings = Settings(user_id=user['id'])
            session.add(settings)
            session.commit()
            
            print(f"✅ Пользователь создан: {username}")
            return user
        except IntegrityError:
            session.rollback()
            print(f"❌ Пользователь {username} уже существует")
            return None
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка создания пользователя: {e}")
            return None
        finally:
            session.close()
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        session = self.db.get_session()
        try:
            return session.query(User).filter(User.id == user_id).first()
        finally:
            session.close()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Получение пользователя по имени"""
        session = self.db.get_session()
        try:
            return session.query(User).filter(User.username == username).first()
        finally:
            session.close()
    
    def get_all_active(self) -> List[User]:
        """Получение всех активных пользователей"""
        session = self.db.get_session()
        try:
            return session.query(User).filter(User.is_active == True).all()
        finally:
            session.close()
    
    def update(self, user: User) -> bool:
        """Обновление пользователя"""
        session = self.db.get_session()
        try:
            session.merge(user)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка обновления: {e}")
            return False
        finally:
            session.close()


class ProjectRepository:
    """Репозиторий для работы с проектами"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def create(self, user_id: int, name: str, description: str = "") -> Optional[Project]:
        """Создание нового проекта"""
        session = self.db.get_session()
        try:
            project = Project(
                user_id=user_id,
                name=name,
                description=description
            )
            session.add(project)
            session.commit()
            print(f"✅ Проект создан: {name}")
            return project
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка создания проекта: {e}")
            return None
        finally:
            session.close()
    
    def get_by_user(self, user_id: int) -> List[Project]:
        """Получение всех проектов пользователя"""
        session = self.db.get_session()
        try:
            return session.query(Project).filter(
                Project.user_id == user_id,
                Project.is_active == True
            ).all()
        finally:
            session.close()


class ItemRepository:
    """Репозиторий для работы с объявлениями"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def save_from_api(self, project_id: int, item_data: Dict[str, Any]) -> Optional[Item]:
        """Сохранение объявления из API"""
        session = self.db.get_session()
        try:
            item = session.query(Item).filter(
                Item.project_id == project_id,
                Item.item_id_avito == item_data.get('id')
            ).first()
            
            if item:
                item.title = item_data.get('title', item.title)
                item.description = item_data.get('description', item.description)
                item.price = item_data.get('price', item.price)
                item.status = item_data.get('status', item.status)
                item.updated_at = datetime.now()
            else:
                item = Item(
                    project_id=project_id,
                    item_id_avito=item_data.get('id'),
                    title=item_data.get('title', 'Без названия'),
                    description=item_data.get('description', ''),
                    price=item_data.get('price', 0),
                    status=item_data.get('status', 'unknown')
                )
                session.add(item)
            
            session.commit()
            return item
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка сохранения объявления: {e}")
            return None
        finally:
            session.close()
    
    def get_by_project(self, project_id: int) -> List[Item]:
        """Получение всех объявлений проекта"""
        session = self.db.get_session()
        try:
            return session.query(Item).filter(
                Item.project_id == project_id,
                Item.is_active == True
            ).order_by(Item.created_at.desc()).all()
        finally:
            session.close()
    
    def delete(self, item_id: int) -> bool:
        """Мягкое удаление объявления"""
        session = self.db.get_session()
        try:
            item = session.query(Item).filter(Item.id == item_id).first()
            if item:
                item.is_active = False
                item.updated_at = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка удаления: {e}")
            return False
        finally:
            session.close()
''',

    "database/migration.py": '''"""
Управление миграциями базы данных
"""

import os
from pathlib import Path

from .models import DatabaseManager


class MigrationManager:
    """Менеджер миграций"""
    
    def __init__(self, db_path="avito_commander.db"):
        self.db_path = db_path
        
    def run_migrations(self):
        """Запуск всех миграций"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        is_new = not os.path.exists(self.db_path)
        db = DatabaseManager(self.db_path)
        db.init_db()
        
        if is_new:
            print("✅ Создана новая база данных")
        else:
            print("✅ База данных загружена")
        
        return db
''',

    # ===== API =====
    "api/__init__.py": '''"""
Модуль для работы с внешними API
"""
from .avito_api import AvitoAPI, AvitoAuth
from .sync_service import SyncService

__all__ = ['AvitoAPI', 'AvitoAuth', 'SyncService']
''',

    "api/avito_api.py": '''"""
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
    
    def _get_headers(self) -> Dict[str, str]:
        """Формирует заголовки для запросов"""
        token = self.auth.get_valid_token()
        if not token:
            token = "temp_token_for_testing"  # Заглушка для тестирования
        
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def get_items(self, user_id: str, status: str = None, page: int = 1, per_page: int = 50) -> Dict:
        """Получение списка объявлений"""
        # Заглушка для тестирования
        return {
            "items": [
                {
                    "id": "1",
                    "title": "Тестовое объявление 1",
                    "price": 1000,
                    "status": "active",
                    "stats": {"views": 10, "calls": 2, "favorites": 1}
                },
                {
                    "id": "2",
                    "title": "Тестовое объявление 2",
                    "price": 2000,
                    "status": "inactive",
                    "stats": {"views": 5, "calls": 0, "favorites": 0}
                }
            ],
            "total_pages": 1
        }
    
    def create_item(self, user_id: str, item_data: Dict) -> Dict:
        """Создание объявления"""
        return {"id": "3", "status": "created", **item_data}
    
    def update_item(self, user_id: str, item_id: str, item_data: Dict) -> Dict:
        """Обновление объявления"""
        return {"id": item_id, "status": "updated", **item_data}
    
    def delete_item(self, user_id: str, item_id: str) -> bool:
        """Удаление объявления"""
        return True
''',

    "api/sync_service.py": '''"""
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
    
    def sync_items(self, project_id: int) -> List[Dict]:
        """Синхронизация объявлений с Avito"""
        if not self.user_id:
            raise ValueError("User ID не установлен")
        
        self.event_bus.emit("sync_started")
        
        try:
            response = self.avito_api.get_items(self.user_id)
            items = response.get("items", [])
            
            count = 0
            for item_data in items:
                self.item_repo.save_from_api(project_id, item_data)
                count += 1
            
            self.last_sync_time = datetime.now()
            self.event_bus.emit("sync_finished", count)
            
            return items
            
        except Exception as e:
            self.event_bus.emit("error_occurred", str(e))
            raise
    
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
''',

    # ===== UI =====
    "ui/__init__.py": '''"""
Модуль пользовательского интерфейса
"""
from .main_window import MainWindow
from .login_dialog import LoginDialog

__all__ = ['MainWindow', 'LoginDialog']
''',

    "ui/login_dialog.py": '''"""
Диалог входа в приложение
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from core.app import Application


class LoginDialog(QDialog):
    """Диалог для входа пользователя"""
    
    def __init__(self, app: Application, parent=None):
        super().__init__(parent)
        self.app = app
        self.user = None
        
        self.setWindowTitle("Вход в Avito Commander")
        self.setFixedSize(450, 400)
        self.setModal(True)
        
        self.init_ui()
        self.load_saved_users()
    
    def init_ui(self):
        """Создание интерфейса"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
        title = QLabel("🔑 Avito Commander")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Подзаголовок
        subtitle = QLabel("Войдите в свой аккаунт")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Поле для имени пользователя
        layout.addWidget(QLabel("Имя пользователя:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите имя пользователя...")
        layout.addWidget(self.username_input)
        
        # Поле для User ID Avito
        layout.addWidget(QLabel("Ваш ID на Avito:"))
        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("Например: 123456789")
        layout.addWidget(self.user_id_input)
        
        # Комбобокс с сохраненными пользователями
        layout.addWidget(QLabel("Или выберите существующего:"))
        self.users_combo = QComboBox()
        self.users_combo.addItem("-- Выберите пользователя --")
        self.users_combo.currentIndexChanged.connect(self.on_user_selected)
        layout.addWidget(self.users_combo)
        
        layout.addSpacing(10)
        
        # Статус
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #FF6B6B;")
        layout.addWidget(self.status_label)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        self.login_btn = QPushButton("✅ Войти")
        self.login_btn.clicked.connect(self.login)
        self.login_btn.setFixedHeight(45)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A651;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #008845;
            }
        """)
        
        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setFixedHeight(45)
        
        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_saved_users(self):
        """Загружает сохраненных пользователей"""
        users = self.app.user_repo.get_all_active()
        for user in users:
            self.users_combo.addItem(f"{user['username"]} (ID: {user['user_id_avito']})", user['id'])
    
    def on_user_selected(self, index):
        """Обработчик выбора пользователя из списка"""
        if index > 0:
            user_id = self.users_combo.currentData()
            user = self.app.user_repo.get_by_id(user_id)
            if user:
                self.username_input.setText(user['username'])
                self.user_id_input.setText(user['user_id_avito'])
                self.status_label.setText("")
    
    def login(self):
        """Обработчик входа"""
        username = self.username_input.text().strip()
        user_id_avito = self.user_id_input.text().strip()
        
        if not username:
            self.status_label.setText("❌ Введите имя пользователя")
            return
        
        if not user_id_avito:
            self.status_label.setText("❌ Введите ваш ID на Avito")
            return
        
        user = self.app.user_repo.get_by_username(username)
        
        if user:
            if user['user_id_avito'] != user_id_avito:
                user['user_id_avito'] = user_id_avito
                self.app.user_repo.update(user)
            
            self.user = user
            self.status_label.setText("✅ Вход выполнен!")
            self.status_label.setStyleSheet("color: #00A651;")
            self.accept()
        else:
            self.user = self.app.user_repo.create(username, user_id_avito)
            if self.user:
                self.status_label.setText("✅ Пользователь создан!")
                self.status_label.setStyleSheet("color: #00A651;")
                self.accept()
            else:
                self.status_label.setText("❌ Ошибка создания пользователя")
''',

    "ui/main_window.py": '''"""
Главное окно приложения
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from core.app import Application


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self, app: Application):
        super().__init__()
        
        self.app = app
        
        self.setWindowTitle(f"Avito Commander - {app.get_current_user().username}")
        self.setGeometry(100, 100, 1400, 800)
        
        self.init_ui()
        self.connect_events()
        self.load_projects()
    
    def init_ui(self):
        """Создание интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        central_widget.setLayout(main_layout)
        
        # Верхняя панель
        self.create_top_panel(main_layout)
        
        # Таблица
        self.create_table(main_layout)
        
        # Нижняя панель
        self.create_bottom_panel(main_layout)
        
        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")
    
    def create_top_panel(self, parent_layout):
        """Создание верхней панели"""
        panel = QHBoxLayout()
        
        sync_btn = QPushButton("🔄 Синхронизировать")
        sync_btn.clicked.connect(self.sync_items)
        panel.addWidget(sync_btn)
        
        refresh_btn = QPushButton("↻ Обновить")
        refresh_btn.clicked.connect(self.load_items)
        panel.addWidget(refresh_btn)
        
        panel.addStretch()
        
        logout_btn = QPushButton("🚪 Выйти")
        logout_btn.clicked.connect(self.logout)
        panel.addWidget(logout_btn)
        
        parent_layout.addLayout(panel)
    
    def create_table(self, parent_layout):
        """Создание таблицы"""
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Название", "Цена", "Статус", "Просмотры", "Звонки", "Дата"
        ])
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSortingEnabled(True)
        
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(1, 350)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 80)
        self.table.setColumnWidth(6, 150)
        
        parent_layout.addWidget(self.table)
    
    def create_bottom_panel(self, parent_layout):
        """Создание нижней панели"""
        panel = QHBoxLayout()
        
        self.info_label = QLabel("Всего: 0 объявлений")
        panel.addWidget(self.info_label)
        
        panel.addStretch()
        
        edit_btn = QPushButton("✏️ Редактировать")
        edit_btn.clicked.connect(self.edit_item)
        panel.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ Удалить")
        delete_btn.clicked.connect(self.delete_item)
        panel.addWidget(delete_btn)
        
        parent_layout.addLayout(panel)
    
    def connect_events(self):
        """Подключение событий"""
        self.app.event_bus.items_updated.connect(self.load_items)
        self.app.event_bus.sync_finished.connect(self.on_sync_finished)
        self.app.event_bus.error_occurred.connect(self.on_error)
    
    def load_projects(self):
        """Загрузка проектов"""
        user = self.app.get_current_user()
        if user:
            print(f"Пользователь: {user['username"]}")
            self.load_items()
    
    def load_items(self):
        """Загрузка объявлений"""
        self.table.setRowCount(0)
        
        # Тестовые данные
        test_items = [
            {"id": "1", "title": "Тестовое объявление 1", "price": 1000, "status": "active", "views": 10, "calls": 2, "date": "2024-01-01"},
            {"id": "2", "title": "Тестовое объявление 2", "price": 2000, "status": "inactive", "views": 5, "calls": 0, "date": "2024-01-02"},
            {"id": "3", "title": "Тестовое объявление 3", "price": 1500, "status": "active", "views": 8, "calls": 1, "date": "2024-01-03"},
        ]
        
        for item in test_items:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(item["id"]))
            self.table.setItem(row, 1, QTableWidgetItem(item["title"]))
            self.table.setItem(row, 2, QTableWidgetItem(f"{item['price']:,} ₽"))
            self.table.setItem(row, 3, QTableWidgetItem(item["status"]))
            self.table.setItem(row, 4, QTableWidgetItem(str(item["views"])))
            self.table.setItem(row, 5, QTableWidgetItem(str(item["calls"])))
            self.table.setItem(row, 6, QTableWidgetItem(item["date"]))
        
        self.info_label.setText(f"Всего: {len(test_items)} объявлений")
        self.status_bar.showMessage(f"Загружено {len(test_items)} объявлений")
    
    def sync_items(self):
        """Синхронизация с Avito"""
        self.status_bar.showMessage("🔄 Синхронизация...")
        QTimer.singleShot(2000, self.on_sync_finished)
    
    def on_sync_finished(self, count=10):
        """Обработчик завершения синхронизации"""
        self.status_bar.showMessage(f"✅ Синхронизировано {count} объявлений")
        self.load_items()
    
    def on_error(self, error):
        """Обработчик ошибок"""
        self.status_bar.showMessage(f"❌ {error}")
        QMessageBox.critical(self, "Ошибка", error)
    
    def edit_item(self):
        """Редактирование объявления"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            item_id = self.table.item(current_row, 0).text()
            title = self.table.item(current_row, 1).text()
            QMessageBox.information(self, "Редактирование", f"Редактирование объявления {item_id}: {title}")
    
    def delete_item(self):
        """Удаление объявления"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            item_id = self.table.item(current_row, 0).text()
            reply = QMessageBox.question(
                self,
                "Удаление",
                f"Удалить объявление {item_id}?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.table.removeRow(current_row)
                self.status_bar.showMessage(f"🗑️ Объявление {item_id} удалено")
    
    def logout(self):
        """Выход из аккаунта"""
        reply = QMessageBox.question(
            self,
            "Выход",
            "Выйти из аккаунта?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.app.config.set("user/current_id", None)
            self.app.quit()
            self.close()
''',

    "ui/widgets/__init__.py": '''"""
Виджеты интерфейса
"""
''',

    "ui/dialogs/__init__.py": '''"""
Диалоговые окна
"""
''',

    # ===== SERVICES =====
    "services/__init__.py": '''"""
Сервисы приложения
"""
from .item_service import ItemService
from .project_service import ProjectService
from .analytics_service import AnalyticsService
from .notification_service import NotificationService

__all__ = ['ItemService', 'ProjectService', 'AnalyticsService', 'NotificationService']
''',

    "services/item_service.py": '''"""
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
''',

    "services/project_service.py": '''"""
Сервис для работы с проектами
"""

from typing import Optional
from database.repository import ProjectRepository
from core.event_bus import EventBus


class ProjectService:
    """Сервис для управления проектами"""
    
    def __init__(self, project_repo: ProjectRepository, event_bus: EventBus):
        self.project_repo = project_repo
        self.event_bus = event_bus
    
    def create_project(self, user_id: int, name: str, description: str = "") -> Optional[dict]:
        """Создание нового проекта"""
        project = self.project_repo.create(user_id, name, description)
        if project:
            self.event_bus.emit("project_changed", project)
            return project.__dict__
        return None
''',

    "services/analytics_service.py": '''"""
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
''',

    "services/notification_service.py": '''"""
Сервис для уведомлений
"""

from PyQt5.QtCore import QObject


class NotificationService(QObject):
    """Сервис для отправки уведомлений"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
    
    def send(self, title: str, message: str, is_important: bool = False):
        """Отправка уведомления"""
        print(f"[УВЕДОМЛЕНИЕ] {title}: {message}")
''',

    # ===== UTILS =====
    "utils/__init__.py": '''"""
Утилиты
"""
''',

    # ===== MAIN =====
    "main.py": '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Точка входа в приложение Avito Commander
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.app import Application


def main():
    """Главная функция"""
    print("""
    ╔═══════════════════════════════════════════╗
    ║     Avito Commander v0.2.0              ║
    ║     Управление объявлениями Avito       ║
    ╚═══════════════════════════════════════════╝
    """)
    
    app = Application()
    app.init_app()
    sys.exit(app.start())


if __name__ == "__main__":
    main()
''',

    # ===== .env =====
    ".env": '''# Avito API
AVITO_CLIENT_ID=your_client_id_here
AVITO_CLIENT_SECRET=your_client_secret_here
AVITO_REDIRECT_URI=http://localhost:8080

# Telegram Bot (опционально)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
''',

    # ===== requirements.txt =====
    "requirements.txt": '''PyQt5>=5.15.0
SQLAlchemy>=1.4.0
requests>=2.28.0
python-dotenv>=1.0.0
python-dateutil>=2.8.0
''',
}


def create_structure():
    """Создает структуру папок и файлов"""
    print("📁 Создание структуры проекта...")
    
    # Создаем папки
    dirs = [
        "core",
        "database",
        "api",
        "ui/widgets",
        "ui/dialogs",
        "services",
        "utils",
        "assets",
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {dir_path}/")
    
    # Создаем файлы
    print("\n📄 Создание файлов...")
    
    for file_path, content in FILES.items():
        # Создаем папку для файла если её нет
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Записываем содержимое
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ {file_path}")
    
    print("\n✅ Структура проекта создана успешно!")
    print("\n📌 Дальнейшие действия:")
    print("  1. Установите зависимости: pip install -r requirements.txt")
    print("  2. Настройте .env файл (укажите client_id и client_secret)")
    print("  3. Запустите приложение: python main.py")


if __name__ == "__main__":
    create_structure()