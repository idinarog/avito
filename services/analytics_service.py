"""
Сервис для аналитики и метрик
"""

from typing import List, Dict, Any, Optional
from database.repository import ItemRepository
from core.metrics_calculator import MetricsCalculator


class AnalyticsService:
    """Сервис для работы с метриками и аналитикой"""
    
    def __init__(self, item_repo: ItemRepository):
        self.item_repo = item_repo
        self.db = None  # Для совместимости
    
    def get_item_metrics(self, item_id: int) -> Dict[str, Any]:
        """
        Получение метрик для одного объявления
        
        Аргументы:
            item_id: ID объявления в локальной БД
            
        Возвращает:
            Словарь с метриками
        """
        item = self.item_repo.get_by_id(item_id)
        if not item:
            return {}
        return MetricsCalculator.calculate_for_ad(item)
    
    def get_project_metrics(self, project_id: int) -> Dict[str, Any]:
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
        items = self.item_repo.get_by_project(project_id)
        count = 0
        for item in items:
            MetricsCalculator.update_item_metrics(item)
            # Сохраняем изменения в БД
            self.item_repo.save_from_api(item.project_id, {
                'id': item.item_id_avito,
                'total_leads': getattr(item, 'total_leads', 0),
                'ctr': getattr(item, 'ctr', 0),
                'cpl': getattr(item, 'cpl', 0),
                'cpc': getattr(item, 'cpc', 0),
                'cpm': getattr(item, 'cpm', 0),
                'cpf': getattr(item, 'cpf', 0),
            })
            count += 1
        return count
    
    def get_dashboard_data(self, project_id: int) -> Dict[str, Any]:
        """
        Получение данных для дашборда
        
        Аргументы:
            project_id: ID проекта
            
        Возвращает:
            Словарь с данными для дашборда
        """
        items = self.item_repo.get_by_project(project_id)
        
        if not items:
            return {
                'total_items': 0,
                'active_items': 0,
                'total_views': 0,
                'total_calls': 0,
                'total_leads': 0,
                'avg_ctr': 0,
            }
        
        total_items = len(items)
        active_items = sum(1 for i in items if i.status == 'active')
        total_views = sum(i.views or 0 for i in items)
        total_calls = sum(i.calls or 0 for i in items)
        total_messages = sum(getattr(i, 'messages', 0) or 0 for i in items)
        total_leads = total_calls + total_messages
        avg_ctr = round((total_leads / total_views * 100) if total_views > 0 else 0, 2)
        
        return {
            'total_items': total_items,
            'active_items': active_items,
            'total_views': total_views,
            'total_calls': total_calls,
            'total_leads': total_leads,
            'avg_ctr': avg_ctr,
        }