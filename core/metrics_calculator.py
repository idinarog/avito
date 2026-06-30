"""
Расчет бизнес-метрик для объявлений и проектов
Метрики: CTR, CPL, CPC, CPM, CPF и другие
"""

from typing import List, Dict, Any, Optional
from database.models import Item, Project


class MetricsCalculator:
    """
    Класс для расчета всех бизнес-метрик
    """
    
    @staticmethod
    def calculate_for_ad(item: Item) -> Dict[str, Any]:
        """
        Расчет метрик для одного объявления
        
        Аргументы:
            item: Объект объявления (Item)
            
        Возвращает:
            Словарь со всеми метриками
        """
        # Базовые данные
        views = item.views or 0
        calls = item.calls or 0
        messages = getattr(item, 'messages', 0) or 0  # Если поля нет, используем 0
        favorites = item.favorites or 0
        budget = getattr(item, 'budget', 0.0) or 0.0
        
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
            'id': item.item_id_avito,
            'title': item.title,
            'price': item.price,
            'status': item.status,
            
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
    def calculate_for_project(items: List[Item]) -> Dict[str, Any]:
        """
        Расчет агрегированной статистики по проекту
        
        Аргументы:
            items: Список объявлений проекта
            
        Возвращает:
            Словарь с агрегированными метриками
        """
        if not items:
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
        
        total = len(items)
        active = sum(1 for i in items if i.status == 'active')
        inactive = sum(1 for i in items if i.status == 'inactive')
        blocked = sum(1 for i in items if i.status == 'blocked')
        
        total_views = sum(i.views or 0 for i in items)
        total_calls = sum(i.calls or 0 for i in items)
        total_messages = sum(getattr(i, 'messages', 0) or 0 for i in items)
        total_favorites = sum(i.favorites or 0 for i in items)
        total_leads = total_calls + total_messages
        total_budget = sum(getattr(i, 'budget', 0.0) or 0 for i in items)
        
        # Цены
        prices = [i.price or 0 for i in items]
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
    def update_item_metrics(item: Item) -> Item:
        """
        Обновляет поля метрик в объекте объявления
        
        Аргументы:
            item: Объект объявления
            
        Возвращает:
            Обновленный объект объявления
        """
        metrics = MetricsCalculator.calculate_for_ad(item)
        
        # Обновляем поля (если они есть в модели)
        if hasattr(item, 'total_leads'):
            item.total_leads = metrics['total_leads']
        if hasattr(item, 'ctr'):
            item.ctr = metrics['ctr']
        if hasattr(item, 'cpl'):
            item.cpl = metrics['cpl']
        if hasattr(item, 'cpc'):
            item.cpc = metrics['cpc']
        if hasattr(item, 'cpm'):
            item.cpm = metrics['cpm']
        if hasattr(item, 'cpf'):
            item.cpf = metrics['cpf']
        
        return item
    
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