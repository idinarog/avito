import sqlite3

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        # Алиас для совместимости
        self.connection = self.conn

    def execute(self, query, params=None):
        if params:
            return self.conn.execute(query, params)
        return self.conn.execute(query)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

from .migration import MigrationManager
from .repository import UserRepository, ProjectRepository, ItemRepository

__all__ = [
    'DatabaseManager',
    'MigrationManager',
    'UserRepository',
    'ProjectRepository',
    'ItemRepository',
]
