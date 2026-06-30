"""
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
