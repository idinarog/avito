#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тестовый скрипт для проверки расчета метрик
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database.models import DatabaseManager, Item
from core.metrics_calculator import MetricsCalculator


def test_metrics():
    """Тест расчета метрик"""
    print("🧪 Тестирование метрик")
    print("=" * 40)
    
    # Создаем тестовое объявление
    item = Item()
    item.views = 100
    item.calls = 5
    item.messages = 3
    item.favorites = 2
    item.budget = 500.0
    item.title = "Тестовое объявление"
    item.price = 1000
    item.item_id_avito = "test_123"
    item.status = "active"
    
    # Рассчитываем метрики
    metrics = MetricsCalculator.calculate_for_ad(item)
    
    print("\n📊 Метрики для тестового объявления:")
    print(f"  Просмотры: {metrics['views']}")
    print(f"  Звонки: {metrics['calls']}")
    print(f"  Сообщения: {metrics['messages']}")
    print(f"  Избранные: {metrics['favorites']}")
    print(f"  Бюджет: {metrics['budget']}")
    print(f"\n  Всего лидов: {metrics['total_leads']}")
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
    
    print("\n" + "=" * 40)
    if all_ok:
        print("✅ Все метрики рассчитаны верно!")
    else:
        print("❌ Есть ошибки в расчетах")
    
    return all_ok


if __name__ == "__main__":
    test_metrics()