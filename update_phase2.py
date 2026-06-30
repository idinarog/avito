#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для применения изменений Этапа 2:
- Расширение таблицы items (новые поля для метрик)
- Создание таблицы sync_logs
- Создание таблицы settings (если отсутствует)
- Проверка структуры БД
"""

import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime


class Phase2Updater:
    """Класс для применения изменений Этапа 2"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.db_path = self.project_root / "avito_commander.db"
        self.errors = []
        self.steps = []
        
        # Цвета для вывода
        self.GREEN = '\033[92m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.BLUE = '\033[94m'
        self.RESET = '\033[0m'
        self.BOLD = '\033[1m'
    
    def print_header(self, text):
        print(f"\n{self.BOLD}{self.BLUE}{'='*60}{self.RESET}")
        print(f"{self.BOLD}{self.BLUE}{text:^60}{self.RESET}")
        print(f"{self.BOLD}{self.BLUE}{'='*60}{self.RESET}\n")
    
    def print_success(self, text):
        print(f"{self.GREEN}✅ {text}{self.RESET}")
        self.steps.append(f"✅ {text}")
    
    def print_error(self, text):
        print(f"{self.RED}❌ {text}{self.RESET}")
        self.errors.append(f"❌ {text}")
    
    def print_info(self, text):
        print(f"{self.BLUE}ℹ️ {text}{self.RESET}")
    
    def print_warning(self, text):
        print(f"{self.YELLOW}⚠️ {text}{self.RESET}")
    
    def get_connection(self):
        """Получение подключения к БД"""
        return sqlite3.connect(self.db_path)
    
    def get_existing_columns(self, table_name: str) -> list:
        """Получение списка колонок в таблице"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        
        conn.close()
        return columns
    
    def add_column_if_not_exists(self, table_name: str, column_name: str, column_type: str, default: str = None):
        """Добавляет колонку, если она не существует"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Проверяем, существует ли колонка
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        if column_name in existing_columns:
            self.print_info(f"Колонка {column_name} уже существует в {table_name}")
            conn.close()
            return True
        
        # Добавляем колонку
        try:
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            if default is not None:
                sql += f" DEFAULT {default}"
            cursor.execute(sql)
            conn.commit()
            self.print_success(f"Добавлена колонка {column_name} ({column_type}) в {table_name}")
            conn.close()
            return True
        except Exception as e:
            self.print_error(f"Ошибка добавления колонки {column_name}: {e}")
            conn.close()
            return False
    
    def create_table_if_not_exists(self, table_name: str, create_sql: str):
        """Создает таблицу, если она не существует"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Проверяем, существует ли таблица
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if cursor.fetchone():
            self.print_info(f"Таблица {table_name} уже существует")
            conn.close()
            return True
        
        try:
            cursor.execute(create_sql)
            conn.commit()
            self.print_success(f"Создана таблица {table_name}")
            conn.close()
            return True
        except Exception as e:
            self.print_error(f"Ошибка создания таблицы {table_name}: {e}")
            conn.close()
            return False
    
    def extend_items_table(self) -> bool:
        """Расширение таблицы items новыми полями"""
        self.print_header("1. РАСШИРЕНИЕ ТАБЛИЦЫ ITEMS")
        
        # Проверяем существование таблицы
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='items'")
        if not cursor.fetchone():
            self.print_error("Таблица items не найдена!")
            conn.close()
            return False
        conn.close()
        
        # Список новых полей
        new_columns = [
            ("messages", "INTEGER", "0"),           # Сообщения
            ("budget", "FLOAT", "0.0"),             # Бюджет
            ("total_leads", "INTEGER", "0"),        # Всего лидов
            ("ctr", "FLOAT", "0.0"),                # CTR
            ("cpl", "FLOAT", "0.0"),                # CPL
            ("cpc", "FLOAT", "0.0"),                # CPC
            ("cpm", "FLOAT", "0.0"),                # CPM
            ("cpf", "FLOAT", "0.0"),                # CPF
        ]
        
        all_ok = True
        for column_name, column_type, default in new_columns:
            if not self.add_column_if_not_exists("items", column_name, column_type, default):
                all_ok = False
        
        # Проверяем, какие колонки были добавлены
        existing = self.get_existing_columns("items")
        self.print_info(f"Всего колонок в items: {len(existing)}")
        
        return all_ok
    
    def create_sync_logs_table(self) -> bool:
        """Создание таблицы sync_logs"""
        self.print_header("2. СОЗДАНИЕ ТАБЛИЦЫ SYNC_LOGS")
        
        create_sql = """
        CREATE TABLE sync_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            message TEXT,
            records_processed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
        """
        
        return self.create_table_if_not_exists("sync_logs", create_sql)
    
    def create_settings_table(self) -> bool:
        """Создание таблицы settings (если отсутствует)"""
        self.print_header("3. СОЗДАНИЕ ТАБЛИЦЫ SETTINGS")
        
        create_sql = """
        CREATE TABLE settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            theme TEXT DEFAULT 'dark',
            auto_sync INTEGER DEFAULT 1,
            sync_interval INTEGER DEFAULT 3600,
            notifications INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        
        return self.create_table_if_not_exists("settings", create_sql)
    
    def create_favorites_table(self) -> bool:
        """Создание таблицы favorites (если отсутствует)"""
        self.print_header("4. СОЗДАНИЕ ТАБЛИЦЫ FAVORITES")
        
        create_sql = """
        CREATE TABLE favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id_avito TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, item_id_avito)
        )
        """
        
        return self.create_table_if_not_exists("favorites", create_sql)
    
    def verify_structure(self) -> bool:
        """Проверка структуры БД после изменений"""
        self.print_header("5. ПРОВЕРКА СТРУКТУРЫ БД")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Получаем все таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📋 Таблицы в БД: {', '.join(tables)}")
        
        # Проверяем колонки в items
        columns = self.get_existing_columns("items")
        required_columns = [
            'id', 'project_id', 'item_id_avito', 'title', 'price', 'status',
            'views', 'calls', 'favorites', 'messages', 'budget',
            'total_leads', 'ctr', 'cpl', 'cpc', 'cpm', 'cpf'
        ]
        
        all_ok = True
        print("\n📊 Колонки в таблице items:")
        for col in required_columns:
            if col in columns:
                print(f"  ✅ {col}")
            else:
                print(f"  ❌ {col} (отсутствует)")
                all_ok = False
        
        conn.close()
        return all_ok
    
    def create_backup(self) -> bool:
        """Создание резервной копии БД"""
        self.print_header("📦 СОЗДАНИЕ РЕЗЕРВНОЙ КОПИИ БД")
        
        if not self.db_path.exists():
            self.print_error("База данных не найдена")
            return False
        
        backup_path = self.db_path.parent / f"avito_commander_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Создаем резервную копию
            backup_conn = sqlite3.connect(backup_path)
            conn.backup(backup_conn)
            
            backup_conn.close()
            conn.close()
            
            self.print_success(f"Резервная копия создана: {backup_path}")
            return True
            
        except Exception as e:
            self.print_error(f"Ошибка создания резервной копии: {e}")
            return False
    
    def show_summary(self):
        """Показывает итоговый отчет"""
        self.print_header("📊 ИТОГОВЫЙ ОТЧЕТ")
        
        print(f"\n{self.BOLD}Выполненные шаги:{self.RESET}")
        for step in self.steps:
            print(f"  {step}")
        
        if self.errors:
            print(f"\n{self.RED}Ошибки:{self.RESET}")
            for error in self.errors:
                print(f"  {error}")
        
        print(f"\n{self.BOLD}{self.GREEN}✅ Этап 2 завершен!{self.RESET}")
        print(f"\n{self.BOLD}📋 Дальнейшие действия:{self.RESET}")
        print(f"  1. Запустите проверку: {self.BOLD}python test_app.py{self.RESET}")
        print(f"  2. Если всё OK, переходите к Этапу 3 (Расчет метрик)")
        print(f"  3. При возникновении проблем: восстановитесь из бэкапа БД")
    
    def run(self):
        """Запуск всех изменений"""
        print(self.BOLD + """
    ╔═══════════════════════════════════════════════════════════╗
    ║         🗄️ ЭТАП 2: РАСШИРЕНИЕ БАЗЫ ДАННЫХ             ║
    ║         Avito Commander 1.0                            ║
    ╚═══════════════════════════════════════════════════════════╝
    """ + self.RESET)
        
        # Проверяем наличие БД
        if not self.db_path.exists():
            self.print_error(f"База данных не найдена: {self.db_path}")
            self.print_info("Запустите приложение один раз, чтобы создать БД")
            return
        
        # Создаем резервную копию
        if not self.create_backup():
            self.print_warning("Продолжаем без резервной копии...")
        
        # Расширяем таблицу items
        if not self.extend_items_table():
            self.print_error("Ошибка расширения таблицы items")
            return
        
        # Создаем новые таблицы
        self.create_sync_logs_table()
        self.create_settings_table()
        self.create_favorites_table()
        
        # Проверяем структуру
        self.verify_structure()
        
        # Итоговый отчет
        self.show_summary()


def main():
    updater = Phase2Updater()
    updater.run()


if __name__ == "__main__":
    main()
