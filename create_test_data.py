#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для создания тестовых данных в БД
Создает проект и объявления для проверки генератора XML
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from database.models import DatabaseManager, Project, Item, User


def create_test_data():
    """Создает тестовые данные в БД"""
    print("📁 Создание тестовых данных...")
    print("=" * 40)
    
    db = DatabaseManager("avito_commander.db")
    db.init_db()
    session = db.get_session()
    
    try:
        # 1. Проверяем, есть ли пользователь
        user = session.query(User).first()
        if not user:
            print("❌ Нет пользователей в БД. Сначала создайте пользователя через приложение.")
            return False
        
        print(f"✅ Найден пользователь: {user.username} (ID: {user.id})")
        
        # 2. Проверяем, есть ли уже проекты
        existing_project = session.query(Project).filter(Project.user_id == user.id).first()
        if existing_project:
            print(f"⚠️ Проект уже существует: {existing_project.name}")
            print("   Пропускаем создание...")
            return True
        
        # 3. Создаем проект (с user_id)
        project = Project(
            user_id=user.id,  # ← Обязательное поле!
            name="Тестовый проект",
            description="Проект для проверки генератора XML",
            is_active=True
        )
        session.add(project)
        session.commit()
        print(f"✅ Создан проект: {project.name} (ID: {project.id})")
        
        # 4. Тестовые объявления
        test_items = [
            {
                "item_id_avito": "RPK-NV-303-MSK",
                "title": "Компоненты ППУ для напыления РПК НВ‑303 | Полиол + изоцианат",
                "description": "Система для получения жесткого пенополиуретана (ППУ) методом напыления.",
                "price": 260,
                "status": "active",
            },
            {
                "item_id_avito": "RPK-NF-403-KLG",
                "title": "Компоненты ППУ РПК НФ‑403 Г3",
                "description": "Повышенная прочность. Плотность: 26–32 кг/м³.",
                "price": 335,
                "status": "active",
            },
            {
                "item_id_avito": "RPK-NV-203-RZN",
                "title": "Компоненты ППУ РПК НВ‑203 Г3",
                "description": "Легкий ППУ. Плотность 10–14 кг/м³.",
                "price": 310,
                "status": "active",
            },
            {
                "item_id_avito": "RPK-NF-303-TUL",
                "title": "Компоненты ППУ РПК НФ‑303 Г3",
                "description": "Плотность 25–29 кг/м³. Доставка по Туле и области.",
                "price": 330,
                "status": "active",
            },
            {
                "item_id_avito": "RPK-NV-401-VRN",
                "title": "Огнестойкая система ППУ РПК НВ‑401 Г1",
                "description": "Огнестойкая система с классом горючести Г1.",
                "price": 475,
                "status": "active",
            },
        ]
        
        count = 0
        for item_data in test_items:
            item = Item(
                project_id=project.id,
                item_id_avito=item_data["item_id_avito"],
                title=item_data["title"],
                description=item_data["description"],
                price=item_data["price"],
                status=item_data["status"],
                is_active=True
            )
            session.add(item)
            count += 1
        
        session.commit()
        print(f"✅ Добавлено {count} тестовых объявлений")
        
        # 5. Показываем что создано
        print("\n📋 Созданные объявления:")
        items = session.query(Item).filter(Item.project_id == project.id).all()
        for item in items:
            city = "Москва"
            if "-" in item.item_id_avito:
                parts = item.item_id_avito.split("-")
                if len(parts) >= 4:
                    city_code = parts[-1]
                    city_map = {
                        'MSK': 'Москва', 'KLG': 'Калуга', 'RZN': 'Рязань',
                        'TUL': 'Тула', 'VRN': 'Воронеж', 'VLD': 'Владимир',
                        'TVR': 'Тверь', 'LPK': 'Липецк', 'ORL': 'Орел',
                        'SRN': 'Саранск', 'NN': 'Нижний Новгород'
                    }
                    city = city_map.get(city_code, 'Москва')
            
            print(f"  • {item.item_id_avito} — {item.title[:40]}... ({city}) — {item.price} ₽")
        
        print("\n" + "="*40)
        print("✅ Тестовые данные успешно созданы!")
        print("🚀 Теперь можно запускать генератор XML:")
        print("   python update_phase5_xml_final.py")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"❌ Ошибка создания данных: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()


def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         📁 СОЗДАНИЕ ТЕСТОВЫХ ДАННЫХ                   ║
    ║         Avito Commander — Подготовка БД               ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    create_test_data()


if __name__ == "__main__":
    main()