"""
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
    

    
    @property
    def total_leads(self):
        """Всего лидов = звонки + сообщения"""
        return (self.calls or 0) + (self.messages or 0)
    
    @property
    def ctr(self):
        """CTR = (лиды / просмотры) * 100"""
        views = self.views or 0
        leads = self.total_leads
        return round((leads / views * 100) if views > 0 else 0, 2)
    
    @property
    def cpl(self):
        """CPL = бюджет / лиды"""
        budget = self.budget or 0.0
        leads = self.total_leads
        return round((budget / leads) if leads > 0 else 0, 2)
    
    @property
    def cpc(self):
        """CPC = бюджет / (звонки + сообщения)"""
        budget = self.budget or 0.0
        contacts = (self.calls or 0) + (self.messages or 0)
        return round((budget / contacts) if contacts > 0 else 0, 2)
    
    @property
    def cpm(self):
        """CPM = бюджет / просмотры * 1000"""
        budget = self.budget or 0.0
        views = self.views or 0
        return round((budget / views * 1000) if views > 0 else 0, 2)
    
    @property
    def cpf(self):
        """CPF = бюджет / добавления в избранное"""
        budget = self.budget or 0.0
        favorites = self.favorites or 0
        return round((budget / favorites) if favorites > 0 else 0, 2)
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
