#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Быстрая проверка работоспособности приложения после Этапа 1
Проверяет: импорты, БД, UI, API клиент
"""

import sys
import os
from pathlib import Path

# Цвета для вывода
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text:^60}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")


def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text):
    print(f"{RED}❌ {text}{RESET}")


def print_info(text):
    print(f"{BLUE}ℹ️ {text}{RESET}")


def test_imports():
    """Тест 1: Проверка импортов"""
    print_header("1. ПРОВЕРКА ИМПОРТОВ")
    
    modules = [
        ('PyQt5.QtWidgets', 'QApplication'),
        ('sqlalchemy', 'create_engine'),
        ('pandas', 'DataFrame'),
        ('openpyxl', 'Workbook'),
        ('apscheduler.schedulers.qt', 'QtScheduler'),
    ]
    
    all_ok = True
    for module, attr in modules:
        try:
            mod = __import__(module, fromlist=[attr])
            getattr(mod, attr)
            print_success(f"{module}.{attr}")
        except ImportError as e:
            print_error(f"{module}.{attr}: {e}")
            all_ok = False
    
    return all_ok


def test_database():
    """Тест 2: Проверка базы данных"""
    print_header("2. ПРОВЕРКА БАЗЫ ДАННЫХ")
    
    try:
        from database.models import DatabaseManager
        
        db = DatabaseManager("avito_commander.db")
        db.init_db()
        session = db.get_session()
        
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print_info(f"Таблицы в БД: {', '.join(tables)}")
        
        # Проверяем существование таблиц (с учетом ваших имен)
        required_tables = ['users', 'projects', 'items']  # ← заменил 'ads' на 'items'
        all_exist = True
        
        for table in required_tables:
            if table in tables:
                print_success(f"✅ Таблица {table} существует")
            else:
                print_error(f"❌ Таблица {table} отсутствует")
                all_exist = False
        
        session.close()
        return all_exist
        
    except Exception as e:
        print_error(f"Ошибка БД: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_app():
    """Тест 3: Проверка приложения (запуск без GUI)"""
    print_header("3. ПРОВЕРКА ПРИЛОЖЕНИЯ")
    
    try:
        from core.app import Application
        from core.config_manager import ConfigManager
        
        # Проверяем конфиг
        config = ConfigManager()
        print_success("ConfigManager загружен")
        
        # Проверяем, что .env читается
        client_id = config.get("avito_client_id")
        print_info(f"Client ID: {client_id[:20] if client_id else 'не найден'}...")
        
        # Создаем приложение без GUI
        app = Application()
        app.init_database()
        app.init_services()
        
        print_success("Application инициализирован")
        
        # Проверяем репозитории
        if app.user_repo:
            print_success("UserRepository OK")
        if app.project_repo:
            print_success("ProjectRepository OK")
        if app.item_repo:
            print_success("ItemRepository OK")
        if app.sync_service:
            print_success("SyncService OK")
        
        return True
        
    except Exception as e:
        print_error(f"Ошибка приложения: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_imports():
    """Тест 4: Проверка UI модулей"""
    print_header("4. ПРОВЕРКА UI МОДУЛЕЙ")
    
    ui_modules = [
        'ui.main_window',
        'ui.login_dialog',
        'ui.widgets.project_panel',
        'ui.widgets.items_panel',
        'ui.widgets.filter_panel',
    ]
    
    all_ok = True
    for module in ui_modules:
        try:
            __import__(module)
            print_success(f"{module}")
        except ImportError as e:
            # Некоторые виджеты могут отсутствовать пока
            if 'No module named' in str(e):
                print_info(f"{module} (ещё не создан)")
            else:
                print_error(f"{module}: {e}")
                all_ok = False
    
    return all_ok


def test_metrics():
    """Тест 5: Проверка метрик"""
    print_header("5. ПРОВЕРКА МЕТРИК")
    
    try:
        from core.metrics_calculator import MetricsCalculator
        from database.models import Ad
        
        # Создаем тестовое объявление
        test_ad = Ad()
        test_ad.views = 100
        test_ad.calls = 5
        test_ad.messages = 3
        test_ad.favorites = 2
        test_ad.budget = 500
        
        metrics = MetricsCalculator.calculate_for_ad(test_ad)
        
        expected = {
            'total_leads': 8,
            'ctr': 8.0,
            'cpl': 62.5,
            'cpc': 62.5,
            'cpm': 5000.0,
            'cpf': 250.0,
        }
        
        all_ok = True
        for key, expected_value in expected.items():
            actual = metrics.get(key)
            if actual == expected_value:
                print_success(f"{key}: {actual}")
            else:
                print_error(f"{key}: ожидалось {expected_value}, получено {actual}")
                all_ok = False
        
        return all_ok
        
    except ImportError:
        print_info("MetricsCalculator ещё не создан (будет в Этапе 3)")
        return True
    except Exception as e:
        print_error(f"Ошибка метрик: {e}")
        return False


def test_import_export():
    """Тест 6: Проверка импорта/экспорта"""
    print_header("6. ПРОВЕРКА ИМПОРТА/ЭКСПОРТА")
    
    try:
        import import_export.importer
        print_success("import_export.importer найден")
    except ImportError:
        print_info("import_export.importer ещё не создан (будет в Этапе 5)")
    
    try:
        import import_export.exporter
        print_success("import_export.exporter найден")
    except ImportError:
        print_info("import_export.exporter ещё не создан (будет в Этапе 5)")
    
    return True


def main():
    print(BOLD + """
    ╔═══════════════════════════════════════════════════════════╗
    ║         🧪 ПРОВЕРКА РАБОТОСПОСОБНОСТИ                  ║
    ║         Avito Commander 1.0 — После Этапа 1            ║
    ╚═══════════════════════════════════════════════════════════╝
    """ + RESET)
    
    tests = [
        ('Импорты', test_imports),
        ('База данных', test_database),
        ('Приложение', test_app),
        ('UI модули', test_ui_imports),
        ('Метрики', test_metrics),
        ('Импорт/Экспорт', test_import_export),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Ошибка в тесте '{name}': {e}")
            results.append((name, False))
    
    # Итоговый отчет
    print_header("📊 ИТОГОВЫЙ ОТЧЕТ")
    
    all_ok = True
    for name, result in results:
        if result:
            print_success(f"{name}: OK")
        else:
            print_error(f"{name}: ОШИБКА")
            all_ok = False
    
    print("\n" + "="*60)
    
    if all_ok:
        print(f"{GREEN}{BOLD}✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!{RESET}")
        print(f"{GREEN}Можно переходить к Этапу 2.{RESET}")
    else:
        print(f"{RED}{BOLD}❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ{RESET}")
        print(f"{YELLOW}Проверьте ошибки выше и исправьте их перед Этапом 2.{RESET}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()