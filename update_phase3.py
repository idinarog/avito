#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для применения изменений Этапа 3:
- Создание класса MetricsCalculator
- Интеграция в AnalyticsService
- Обновление ItemService для автоматического расчета метрик
- Добавление методов для работы с метриками в UI
"""

import os
import sys
import shutil
from pathlib import Path


class Phase3Updater:
    """Класс для применения изменений Этапа 3"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
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
    
    def create_metrics_calculator(self) -> bool:
        """Создание файла core/metrics_calculator.py"""
        self.print_header("1. СОЗДАНИЕ METRICS_CALCULATOR.PY")
        
        file_path = self.project_root / "core" / "metrics_calculator.py"
        
        content = '''"""
Расчет бизнес-метрик для объявлений и проектов
Метрики: CTR, CPL, CPC, CPM, CPF и другие
"""

from typing import List, Dict, Any, Optional
from database.models import Ad, Project


class MetricsCalculator:
    """
    Класс для расчета всех бизнес-метрик
    """
    
    @staticmethod
    def calculate_for_ad(ad: Ad) -> Dict[str, Any]:
        """
        Расчет метрик для одного объявления
        
        Аргументы:
            ad: Объект объявления
            
        Возвращает:
            Словарь со всеми метриками
        """
        # Базовые данные
        views = ad.views or 0
        calls = ad.calls or 0
        messages = ad.messages or 0
        favorites = ad.favorites or 0
        budget = ad.budget or 0.0
        
        # Расчет лидов
        total_leads = calls + messages
        
        # Расчет метрик
        ctr = round((total_leads / views * 100) if views > 0 else 0, 2)
        cpl = round((budget / total_leads) if total_leads > 0 else 0, 2)
        cpc = round((budget / total_leads) if total_leads > 0 else 0, 2)
        cpm = round((budget / views * 1000) if views > 0 else 0, 2)
        cpf = round((budget / favorites) if favorites > 0 else 0, 2)
        
        return {
            # Данные объявления
            'id': ad.item_id_avito,
            'title': ad.title,
            'price': ad.price,
            'status': ad.status,
            
            # Статистика
            'views': views,
            'calls': calls,
            'messages': messages,
            'favorites': favorites,
            'budget': budget,
            
            # Метрики
            'total_leads': total_leads,
            'ctr': ctr,
            'cpl': cpl,
            'cpc': cpc,
            'cpm': cpm,
            'cpf': cpf,
        }
    
    @staticmethod
    def calculate_for_project(ads: List[Ad]) -> Dict[str, Any]:
        """
        Расчет агрегированной статистики по проекту
        
        Аргументы:
            ads: Список объявлений проекта
            
        Возвращает:
            Словарь с агрегированными метриками
        """
        if not ads:
            return {
                'total': 0,
                'active': 0,
                'inactive': 0,
                'blocked': 0,
                'total_views': 0,
                'total_calls': 0,
                'total_messages': 0,
                'total_favorites': 0,
                'total_leads': 0,
                'total_budget': 0,
                'avg_ctr': 0,
                'avg_cpl': 0,
                'avg_cpc': 0,
                'avg_cpm': 0,
                'avg_cpf': 0,
                'max_price': 0,
                'min_price': 0,
                'avg_price': 0,
            }
        
        total = len(ads)
        active = sum(1 for a in ads if a.status == 'active')
        inactive = sum(1 for a in ads if a.status == 'inactive')
        blocked = sum(1 for a in ads if a.status == 'blocked')
        
        total_views = sum(a.views or 0 for a in ads)
        total_calls = sum(a.calls or 0 for a in ads)
        total_messages = sum(a.messages or 0 for a in ads)
        total_favorites = sum(a.favorites or 0 for a in ads)
        total_leads = total_calls + total_messages
        total_budget = sum(a.budget or 0 for a in ads)
        
        # Цены
        prices = [a.price or 0 for a in ads]
        max_price = max(prices) if prices else 0
        min_price = min(prices) if prices else 0
        avg_price = round(sum(prices) / len(prices), 2) if prices else 0
        
        # Расчет средних метрик
        avg_ctr = round((total_leads / total_views * 100) if total_views > 0 else 0, 2)
        avg_cpl = round((total_budget / total_leads) if total_leads > 0 else 0, 2)
        avg_cpc = round((total_budget / total_leads) if total_leads > 0 else 0, 2)
        avg_cpm = round((total_budget / total_views * 1000) if total_views > 0 else 0, 2)
        avg_cpf = round((total_budget / total_favorites) if total_favorites > 0 else 0, 2)
        
        return {
            'total': total,
            'active': active,
            'inactive': inactive,
            'blocked': blocked,
            'total_views': total_views,
            'total_calls': total_calls,
            'total_messages': total_messages,
            'total_favorites': total_favorites,
            'total_leads': total_leads,
            'total_budget': total_budget,
            'avg_ctr': avg_ctr,
            'avg_cpl': avg_cpl,
            'avg_cpc': avg_cpc,
            'avg_cpm': avg_cpm,
            'avg_cpf': avg_cpf,
            'max_price': max_price,
            'min_price': min_price,
            'avg_price': avg_price,
        }
    
    @staticmethod
    def update_ad_metrics(ad: Ad) -> Ad:
        """
        Обновляет поля метрик в объекте объявления
        
        Аргументы:
            ad: Объект объявления
            
        Возвращает:
            Обновленный объект объявления
        """
        metrics = MetricsCalculator.calculate_for_ad(ad)
        
        ad.total_leads = metrics['total_leads']
        ad.ctr = metrics['ctr']
        ad.cpl = metrics['cpl']
        ad.cpc = metrics['cpc']
        ad.cpm = metrics['cpm']
        ad.cpf = metrics['cpf']
        
        return ad
    
    @staticmethod
    def format_metrics_for_display(metrics: Dict[str, Any]) -> Dict[str, str]:
        """
        Форматирует метрики для отображения в UI
        
        Аргументы:
            metrics: Словарь с метриками
            
        Возвращает:
            Словарь с отформатированными строками
        """
        return {
            'total_leads': f"{metrics.get('total_leads', 0)}",
            'ctr': f"{metrics.get('ctr', 0)}%",
            'cpl': f"{metrics.get('cpl', 0):.2f} ₽",
            'cpc': f"{metrics.get('cpc', 0):.2f} ₽",
            'cpm': f"{metrics.get('cpm', 0):.2f} ₽",
            'cpf': f"{metrics.get('cpf', 0):.2f} ₽",
            'total': f"{metrics.get('total', 0)}",
            'active': f"{metrics.get('active', 0)}",
            'inactive': f"{metrics.get('inactive', 0)}",
            'blocked': f"{metrics.get('blocked', 0)}",
            'total_views': f"{metrics.get('total_views', 0):,}",
            'total_calls': f"{metrics.get('total_calls', 0)}",
            'total_messages': f"{metrics.get('total_messages', 0)}",
            'total_favorites': f"{metrics.get('total_favorites', 0)}",
            'total_budget': f"{metrics.get('total_budget', 0):.2f} ₽",
            'avg_price': f"{metrics.get('avg_price', 0):.2f} ₽",
        }
'''
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.print_success(f"Создан {file_path}")
            return True
        except Exception as e:
            self.print_error(f"Ошибка создания файла: {e}")
            return False
    
    def update_analytics_service(self) -> bool:
        """Обновление services/analytics_service.py"""
        self.print_header("2. ОБНОВЛЕНИЕ ANALYTICS_SERVICE.PY")
        
        file_path = self.project_root / "services" / "analytics_service.py"
        
        if not file_path.exists():
            self.print_warning("analytics_service.py не найден, создаем...")
            return self.create_analytics_service()
        
        # Читаем существующий файл
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Добавляем импорт
        if 'from core.metrics_calculator import MetricsCalculator' not in content:
            content = content.replace(
                'from database.repository import ItemRepository',
                'from database.repository import ItemRepository\nfrom core.metrics_calculator import MetricsCalculator'
            )
        
        # Добавляем новые методы, если их нет
        new_methods = '''
    
    def get_item_metrics(self, item_id: int) -> Dict:
        """
        Получение метрик для одного объявления
        
        Аргументы:
            item_id: ID объявления в локальной БД
            
        Возвращает:
            Словарь с метриками
        """
        session = self.db.get_session()
        try:
            item = session.query(Item).filter(Item.id == item_id).first()
            if not item:
                return {}
            return MetricsCalculator.calculate_for_ad(item)
        finally:
            session.close()
    
    def get_project_metrics(self, project_id: int) -> Dict:
        """
        Получение агрегированных метрик по проекту
        
        Аргументы:
            project_id: ID проекта
            
        Возвращает:
            Словарь с агрегированными метриками
        """
        items = self.item_repo.get_by_project(project_id)
        return MetricsCalculator.calculate_for_project(items)
    
    def update_all_item_metrics(self, project_id: int) -> int:
        """
        Обновляет метрики для всех объявлений в проекте
        
        Аргументы:
            project_id: ID проекта
            
        Возвращает:
            Количество обновленных объявлений
        """
        session = self.db.get_session()
        try:
            items = session.query(Item).filter(Item.project_id == project_id).all()
            count = 0
            for item in items:
                MetricsCalculator.update_ad_metrics(item)
                count += 1
            session.commit()
            return count
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка обновления метрик: {e}")
            return 0
        finally:
            session.close()
'''
        
        # Проверяем, есть ли уже метод update_all_item_metrics
        if 'def update_all_item_metrics' not in content:
            # Находим конец класса и вставляем новые методы
            class_end = content.rfind('class AnalyticsService')
            if class_end != -1:
                # Вставляем перед последним методом или в конец класса
                insert_pos = content.rfind('    def ')
                if insert_pos != -1:
                    content = content[:insert_pos] + new_methods + content[insert_pos:]
                else:
                    content = content + new_methods
        
        # Сохраняем
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.print_success(f"Обновлен {file_path}")
            return True
        except Exception as e:
            self.print_error(f"Ошибка обновления файла: {e}")
            return False
    
    def create_analytics_service(self) -> bool:
        """Создание services/analytics_service.py"""
        file_path = self.project_root / "services" / "analytics_service.py"
        
        content = '''"""
Сервис для аналитики и метрик
"""

from typing import List, Dict, Any
from database.repository import ItemRepository
from core.metrics_calculator import MetricsCalculator


class AnalyticsService:
    """Сервис для работы с метриками и аналитикой"""
    
    def __init__(self, db, item_repo: ItemRepository):
        self.db = db
        self.item_repo = item_repo
    
    def get_item_metrics(self, item_id: int) -> Dict:
        """Получение метрик для одного объявления"""
        session = self.db.get_session()
        try:
            item = session.query(Item).filter(Item.id == item_id).first()
            if not item:
                return {}
            return MetricsCalculator.calculate_for_ad(item)
        finally:
            session.close()
    
    def get_project_metrics(self, project_id: int) -> Dict:
        """Получение агрегированных метрик по проекту"""
        items = self.item_repo.get_by_project(project_id)
        return MetricsCalculator.calculate_for_project(items)
    
    def update_all_item_metrics(self, project_id: int) -> int:
        """Обновляет метрики для всех объявлений в проекте"""
        session = self.db.get_session()
        try:
            items = session.query(Item).filter(Item.project_id == project_id).all()
            count = 0
            for item in items:
                MetricsCalculator.update_ad_metrics(item)
                count += 1
            session.commit()
            return count
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка обновления метрик: {e}")
            return 0
        finally:
            session.close()
'''
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.print_success(f"Создан {file_path}")
            return True
        except Exception as e:
            self.print_error(f"Ошибка создания файла: {e}")
            return False
    
    def update_item_service(self) -> bool:
        """Обновление services/item_service.py для автоматического расчета метрик"""
        self.print_header("3. ОБНОВЛЕНИЕ ITEM_SERVICE.PY")
        
        file_path = self.project_root / "services" / "item_service.py"
        
        if not file_path.exists():
            self.print_warning("item_service.py не найден")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Добавляем импорт MetricsCalculator
        if 'from core.metrics_calculator import MetricsCalculator' not in content:
            content = content.replace(
                'from database.repository import ItemRepository',
                'from database.repository import ItemRepository\nfrom core.metrics_calculator import MetricsCalculator'
            )
        
        # Добавляем метод для обновления метрик при сохранении
        update_method = '''
    
    def update_metrics_for_item(self, item_id: int) -> bool:
        """
        Обновляет метрики для одного объявления
        
        Аргументы:
            item_id: ID объявления
            
        Возвращает:
            True если успешно
        """
        session = self.db.get_session()
        try:
            item = session.query(Item).filter(Item.id == item_id).first()
            if not item:
                return False
            MetricsCalculator.update_ad_metrics(item)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка обновления метрик: {e}")
            return False
        finally:
            session.close()
'''
        
        if 'def update_metrics_for_item' not in content:
            # Вставляем метод перед последним методом
            insert_pos = content.rfind('    def ')
            if insert_pos != -1:
                content = content[:insert_pos] + update_method + content[insert_pos:]
            else:
                content = content + update_method
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.print_success(f"Обновлен {file_path}")
            return True
        except Exception as e:
            self.print_error(f"Ошибка обновления файла: {e}")
            return False
    
    def update_models(self) -> bool:
        """Обновление database/models.py (добавление свойств)"""
        self.print_header("4. ОБНОВЛЕНИЕ DATABASE/MODELS.PY")
        
        file_path = self.project_root / "database" / "models.py"
        
        if not file_path.exists():
            self.print_warning("models.py не найден")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем, есть ли уже свойства метрик
        if '@property' in content and 'def total_leads' in content:
            self.print_info("Свойства метрик уже существуют в models.py")
            return True
        
        # Добавляем свойства в класс Item
        properties = '''
    
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
'''
        
        # Находим класс Item и добавляем свойства
        if 'class Item(Base):' in content:
            # Ищем конец класса (следующий class или конец файла)
            item_class_end = content.find('class', content.find('class Item(Base):') + 10)
            if item_class_end == -1:
                item_class_end = len(content)
            
            # Вставляем свойства перед концом класса
            insert_pos = content.rfind('    # Связи', 0, item_class_end)
            if insert_pos == -1:
                insert_pos = content.rfind('    def', 0, item_class_end)
            if insert_pos == -1:
                insert_pos = item_class_end - 10
            
            content = content[:insert_pos] + properties + content[insert_pos:]
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.print_success(f"Обновлен {file_path}")
            return True
        except Exception as e:
            self.print_error(f"Ошибка обновления файла: {e}")
            return False
    
    def create_test_metrics(self) -> bool:
        """Создание тестового скрипта для проверки метрик"""
        self.print_header("5. СОЗДАНИЕ ТЕСТОВОГО СКРИПТА")
        
        file_path = self.project_root / "test_metrics.py"
        
        content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тестовый скрипт для проверки расчета метрик
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database.models import DatabaseManager, Ad
from core.metrics_calculator import MetricsCalculator


def test_metrics():
    """Тест расчета метрик"""
    print("🧪 Тестирование метрик")
    print("=" * 40)
    
    # Создаем тестовое объявление
    ad = Ad()
    ad.views = 100
    ad.calls = 5
    ad.messages = 3
    ad.favorites = 2
    ad.budget = 500.0
    ad.title = "Тестовое объявление"
    ad.price = 1000
    
    # Рассчитываем метрики
    metrics = MetricsCalculator.calculate_for_ad(ad)
    
    print("\\n📊 Метрики для тестового объявления:")
    print(f"  Просмотры: {metrics['views']}")
    print(f"  Звонки: {metrics['calls']}")
    print(f"  Сообщения: {metrics['messages']}")
    print(f"  Избранные: {metrics['favorites']}")
    print(f"  Бюджет: {metrics['budget']}")
    print(f"\\n  Всего лидов: {metrics['total_leads']}")
    print(f"  CTR: {metrics['ctr']}%")
    print(f"  CPL: {metrics['cpl']} ₽")
    print(f"  CPC: {metrics['cpc']} ₽")
    print(f"  CPM: {metrics['cpm']} ₽")
    print(f"  CPF: {metrics['cpf']} ₽")
    
    # Проверяем правильность расчетов
    expected = {
        'total_leads': 8,
        'ctr': 8.0,
        'cpl': 62.5,
        'cpc': 62.5,
        'cpm': 5000.0,
        'cpf': 250.0,
    }
    
    all_ok = True
    for key, value in expected.items():
        actual = metrics.get(key)
        if actual == value:
            print(f"✅ {key}: {actual} (OK)")
        else:
            print(f"❌ {key}: ожидалось {value}, получено {actual}")
            all_ok = False
    
    print("\\n" + "=" * 40)
    if all_ok:
        print("✅ Все метрики рассчитаны верно!")
    else:
        print("❌ Есть ошибки в расчетах")
    
    return all_ok


if __name__ == "__main__":
    test_metrics()
'''
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            os.chmod(file_path, 0o755)
            self.print_success(f"Создан {file_path}")
            return True
        except Exception as e:
            self.print_error(f"Ошибка создания файла: {e}")
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
        
        print(f"\n{self.BOLD}{self.GREEN}✅ Этап 3 завершен!{self.RESET}")
        print(f"\n{self.BOLD}📋 Дальнейшие действия:{self.RESET}")
        print(f"  1. Проверьте метрики: {self.BOLD}python test_metrics.py{self.RESET}")
        print(f"  2. Запустите общую проверку: {self.BOLD}python test_app.py{self.RESET}")
        print(f"  3. Если всё OK, переходите к Этапу 4 (UI - Две панели)")
    
    def run(self):
        """Запуск всех изменений"""
        print(self.BOLD + """
    ╔═══════════════════════════════════════════════════════════╗
    ║         📊 ЭТАП 3: РАСЧЕТ МЕТРИК                      ║
    ║         Avito Commander 1.0                            ║
    ╚═══════════════════════════════════════════════════════════╝
    """ + self.RESET)
        
        # 1. Создаем MetricsCalculator
        self.create_metrics_calculator()
        
        # 2. Обновляем AnalyticsService
        self.update_analytics_service()
        
        # 3. Обновляем ItemService
        self.update_item_service()
        
        # 4. Обновляем models.py
        self.update_models()
        
        # 5. Создаем тестовый скрипт
        self.create_test_metrics()
        
        # Итоговый отчет
        self.show_summary()


def main():
    updater = Phase3Updater()
    updater.run()


if __name__ == "__main__":
    main()
