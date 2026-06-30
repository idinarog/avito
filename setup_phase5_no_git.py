#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Установка Этапа 5 без Git.
Создаёт файлы для генерации, валидации и публикации через веб-интерфейс GitHub.
"""

import os
import sys
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✅ {path}")

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     🔧 УСТАНОВКА ЭТАПА 5 (БЕЗ GIT)                    ║
    ║     Avito Commander — Генерация → Валидация → GitHub   ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # 1. Генератор XML (такой же, как раньше)
    print("\n📄 Создание генератора XML...")
    generator_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Финальный генератор XML-фида для автозагрузки Avito
"""

import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent))

from database.models import DatabaseManager, Item, Project


class AvitoXmlFeedGenerator:
    CITY_MAP = {
        'MSK': 'Москва', 'KLG': 'Калуга', 'RZN': 'Рязань',
        'TUL': 'Тула', 'NN': 'Нижний Новгород', 'SRN': 'Саранск',
        'LPK': 'Липецк', 'ORL': 'Орел', 'VRN': 'Воронеж',
        'VLD': 'Владимир', 'TVR': 'Тверь', 'KRS': 'Калуга'
    }
    CITY_ORDER = ['Москва','Рязань','Тула','Калуга','Нижний Новгород','Саранск','Липецк','Орел','Воронеж','Владимир','Тверь']
    
    def __init__(self, db_path="avito_commander.db"):
        self.db = DatabaseManager(db_path)
        self.db.init_db()
        self.contact_phone = "+74952921880"
        self.manager_name = "Теплый дом"
        self.image_base_url = "https://ee1c563e-8a5a-42cd-8b8a-5120e056f928.selstorage.ru/"
        self.category = "Ремонт и строительство"
        self.goods_type = "Стройматериалы"
        self.goods_sub_type = "Изоляция"
        self.product_sub_type = "Другое"
        self.condition = "Новое"
        self.ad_type = "Товар от производителя"
    
    def generate_feed(self, project_id: int, output_file: str = None) -> str:
        session = self.db.get_session()
        try:
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise ValueError(f"Проект с ID {project_id} не найден")
            items = session.query(Item).filter(Item.project_id == project_id, Item.is_active == True).all()
            if not items:
                print(f"⚠️ В проекте '{project.name}' нет активных объявлений")
                return ""
            grouped = self._group_by_city(items)
            root = ET.Element("Ads", formatVersion="3", target="Avito.ru")
            total_ads = 0
            for city in self.CITY_ORDER:
                if city in grouped:
                    root.append(ET.Comment(f" {city} "))
                    for idx, item in enumerate(grouped[city], 1):
                        root.append(ET.Comment(f" {idx} "))
                        ad = self._create_ad_element(root, item, city)
                        total_ads += 1
            for city, city_items in grouped.items():
                if city not in self.CITY_ORDER:
                    root.append(ET.Comment(f" {city} "))
                    for idx, item in enumerate(city_items, 1):
                        root.append(ET.Comment(f" {idx} "))
                        ad = self._create_ad_element(root, item, city)
                        total_ads += 1
            xml_str = self._pretty_xml(root)
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(xml_str)
                print(f"✅ XML-фид сохранен: {output_file}")
                print(f"📊 Всего объявлений: {total_ads}")
            return xml_str
        except Exception as e:
            print(f"❌ Ошибка генерации XML: {e}")
            return ""
        finally:
            session.close()
    
    def _group_by_city(self, items):
        grouped = {}
        for item in items:
            city = self._extract_city(item)
            grouped.setdefault(city, []).append(item)
        return grouped
    
    def _extract_city(self, item):
        if item.item_id_avito and '-' in item.item_id_avito:
            parts = item.item_id_avito.split('-')
            if len(parts) >= 4:
                city_code = parts[-1]
                if city_code in self.CITY_MAP:
                    return self.CITY_MAP[city_code]
        return 'Москва'
    
    def _extract_model(self, item):
        if item.item_id_avito:
            parts = item.item_id_avito.split('-')
            if len(parts) >= 3:
                return '-'.join(parts[1:4])
        return "NF-303"
    
    def _get_price(self, item, city):
        if item.price and item.price > 0:
            return item.price
        price_map = {'Москва':260,'Калуга':330,'Рязань':330,'Тула':330,'Нижний Новгород':330,'Саранск':330,'Липецк':330,'Орел':330,'Воронеж':330,'Владимир':330,'Тверь':330}
        return price_map.get(city, 330)
    
    def _create_ad_element(self, root, item, city):
        ad = ET.SubElement(root, "Ad")
        ET.SubElement(ad, "Id").text = str(item.item_id_avito or f"ID-{item.id}")
        title = item.title or f"Компоненты ППУ {self._extract_model(item)}"
        ET.SubElement(ad, "Title").text = title
        ET.SubElement(ad, "Category").text = self.category
        ET.SubElement(ad, "GoodsType").text = self.goods_type
        ET.SubElement(ad, "GoodsSubType").text = self.goods_sub_type
        ET.SubElement(ad, "ProductSubType").text = self.product_sub_type
        ET.SubElement(ad, "Condition").text = self.condition
        ET.SubElement(ad, "AdType").text = self.ad_type
        ET.SubElement(ad, "Region").text = city
        ET.SubElement(ad, "Address").text = city
        desc = ET.SubElement(ad, "Description")
        desc.text = self._format_description(item, city)
        price = self._get_price(item, city)
        ET.SubElement(ad, "Price").text = str(price)
        images = ET.SubElement(ad, "Images")
        model = self._extract_model(item)
        image_url = f"{self.image_base_url}{model}.jpg"
        ET.SubElement(images, "Image", url=image_url)
        ET.SubElement(ad, "ContactPhone").text = self.contact_phone
        ET.SubElement(ad, "ManagerName").text = self.manager_name
        return ad
    
    def _format_description(self, item, city):
        if item.description and len(item.description) > 50:
            return item.description
        model = self._extract_model(item)
        price = self._get_price(item, city)
        return f"""
Компоненты ППУ РПК {model} — профессиональная система для получения жесткого пенополиуретана (ППУ) методом напыления.

Цена: {price} руб/кг • 15 лет поставок • Отгрузка в день оплаты

Применение:
— утепление фасадов и кровель
— теплоизоляция промышленных объектов
— напыление ППУ в холодильных камерах

Преимущества:
— теплопроводность 0,021–0,024 Вт/(м·°С)
— закрытоячеистая структура
— высокая механическая прочность
— класс горючести Г3

Технические характеристики:
Соотношение компонентов: 100:100
Плотность: 25–29 кг/м³

Склад: Московская область
Доставка — {city} и область.
"""
    
    def _pretty_xml(self, element):
        rough = ET.tostring(element, 'utf-8')
        reparsed = minidom.parseString(rough)
        return reparsed.toprettyxml(indent="  ")


if __name__ == "__main__":
    import sys
    from database.models import Project
    db = DatabaseManager()
    db.init_db()
    session = db.get_session()
    project = session.query(Project).first()
    if not project:
        print("❌ Нет проектов в БД. Сначала создайте проект.")
        sys.exit(1)
    gen = AvitoXmlFeedGenerator()
    output = f"avito_feed_{project.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
    gen.generate_feed(project.id, output)
'''
    write_file(PROJECT_ROOT / "update_phase5_xml_final.py", generator_content)

    # 2. Валидатор
    print("\n📄 Создание валидатора...")
    validator_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Легкая валидация XML без внешних зависимостей.
Проверяет только базовую структуру и обязательные поля.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

def find_latest_xml():
    xml_files = sorted(Path(".").glob("avito_feed_*.xml"), key=lambda f: f.stat().st_mtime, reverse=True)
    return xml_files[0] if xml_files else None

def validate_xml_light(xml_path):
    print("🔍 Быстрая проверка XML...")
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        errors, warnings = [], []
        if root.tag != "Ads":
            errors.append("Корневой элемент должен быть <Ads>")
        elif root.get("formatVersion") != "3":
            errors.append("formatVersion должен быть '3'")
        ads = root.findall("Ad")
        if not ads:
            errors.append("Нет ни одного объявления <Ad>")
        else:
            print(f"  Найдено объявлений: {len(ads)}")
            for i, ad in enumerate(ads, 1):
                for field in ["Id", "Title", "Category", "Price", "Description"]:
                    if ad.find(field) is None:
                        errors.append(f"Объявление #{i}: отсутствует <{field}>")
                price_elem = ad.find("Price")
                if price_elem is not None and price_elem.text:
                    try:
                        int(price_elem.text)
                    except ValueError:
                        warnings.append(f"Объявление #{i}: цена не число: '{price_elem.text}'")
                id_elem = ad.find("Id")
                if id_elem is not None and not id_elem.text:
                    warnings.append(f"Объявление #{i}: <Id> пустое")
        if errors:
            print("\\n❌ Критические ошибки:")
            for err in errors:
                print(f"  • {err}")
            return False
        elif warnings:
            print("\\n⚠️ Предупреждения:")
            for warn in warnings:
                print(f"  • {warn}")
            print("\\n✅ Базовая структура OK (с предупреждениями)")
            return True
        else:
            print("\\n✅ Всё отлично! XML корректен.")
            return True
    except ET.ParseError as e:
        print(f"❌ Ошибка парсинга XML: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     🔍 ЛЕГКАЯ ВАЛИДАЦИЯ XML (без интернета)            ║
    ║     Avito Commander — Быстрая проверка                 ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    xml_path = find_latest_xml()
    if not xml_path:
        print("❌ XML-файлы не найдены. Сначала запустите генератор.")
        return
    print(f"📄 Файл: {xml_path}")
    print(f"📅 Создан: {datetime.fromtimestamp(xml_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    if validate_xml_light(xml_path):
        print("\\n✅ Файл готов к публикации!")
    else:
        print("\\n❌ Исправьте ошибки и сгенерируйте XML заново.")

if __name__ == "__main__":
    main()
'''
    write_file(PROJECT_ROOT / "validate_light.py", validator_content)

    # 3. Публикатор без Git (открывает веб-интерфейс)
    print("\n📄 Создание скрипта публикации (без Git)...")
    publish_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Публикация XML-фида через веб-интерфейс GitHub.
Генерация → валидация → инструкция по загрузке → открытие Avito.
"""

import os
import sys
import subprocess
import webbrowser
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

GITHUB_UPLOAD_URL = "https://github.com/idinarog/avitoxml/upload/main"
GENERATOR_SCRIPT = "update_phase5_xml_final.py"
XML_FILENAME = "avito_feed.xml"

def print_header(text):
    print("\\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def generate_xml():
    print_header("1️⃣ ГЕНЕРАЦИЯ XML")
    if not os.path.exists(GENERATOR_SCRIPT):
        print(f"❌ Генератор {GENERATOR_SCRIPT} не найден!")
        return None
    result = subprocess.run([sys.executable, GENERATOR_SCRIPT], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Ошибка генерации:")
        print(result.stderr)
        return None
    print("✅ XML-фид сгенерирован")
    return find_latest_xml()

def find_latest_xml():
    xml_files = sorted(Path(".").glob("avito_feed_*.xml"), key=lambda f: f.stat().st_mtime, reverse=True)
    return xml_files[0] if xml_files else None

def validate_xml(xml_path):
    print_header("2️⃣ ВАЛИДАЦИЯ XML")
    print(f"📄 Файл: {xml_path.name}")
    print(f"📅 Создан: {datetime.fromtimestamp(xml_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        errors, warnings = [], []
        if root.tag != "Ads":
            errors.append("Корневой элемент должен быть <Ads>")
        elif root.get("formatVersion") != "3":
            errors.append("formatVersion должен быть '3'")
        ads = root.findall("Ad")
        if not ads:
            errors.append("Нет ни одного объявления <Ad>")
        else:
            print(f"  Найдено объявлений: {len(ads)}")
            for i, ad in enumerate(ads, 1):
                for field in ["Id", "Title", "Category", "Price", "Description"]:
                    if ad.find(field) is None:
                        errors.append(f"Объявление #{i}: отсутствует <{field}>")
                price_elem = ad.find("Price")
                if price_elem is not None and price_elem.text:
                    try:
                        int(price_elem.text)
                    except ValueError:
                        warnings.append(f"Объявление #{i}: цена не число: '{price_elem.text}'")
                id_elem = ad.find("Id")
                if id_elem is not None and not id_elem.text:
                    warnings.append(f"Объявление #{i}: <Id> пустое")
        if errors:
            print("\\n❌ Критические ошибки:")
            for err in errors:
                print(f"  • {err}")
            return False
        elif warnings:
            print("\\n⚠️ Предупреждения:")
            for warn in warnings:
                print(f"  • {warn}")
            print("\\n✅ Базовая структура OK (с предупреждениями)")
            return True
        else:
            print("\\n✅ Всё отлично! XML корректен.")
            return True
    except ET.ParseError as e:
        print(f"❌ Ошибка парсинга XML: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def show_upload_instructions(xml_path):
    print_header("3️⃣ ЗАГРУЗКА НА GITHUB")
    print("📤 Ваш XML-файл готов к публикации.")
    print(f"   Файл: {xml_path.name}")
    print(f"   Размер: {xml_path.stat().st_size} байт")
    print()
    print("👉 Чтобы загрузить его на GitHub, выполните следующие действия:")
    print(f"   1. Откройте в браузере: {GITHUB_UPLOAD_URL}")
    print("   2. Перетащите файл в окно загрузки или выберите его через кнопку")
    print(f"   3. Если хотите использовать постоянное имя {XML_FILENAME}, переименуйте файл перед загрузкой")
    print("   4. Напишите комментарий к коммиту (например, 'Обновление фида')")
    print("   5. Нажмите 'Commit changes'")
    print()
    print("🌐 Открываю страницу загрузки...")
    webbrowser.open(GITHUB_UPLOAD_URL)

def open_avito_autoload():
    print_header("4️⃣ ОТКРЫТИЕ AVITO")
    url = "https://www.avito.ru/profile/autoload"
    print("🌐 Открываю страницу автозагрузки...")
    webbrowser.open(url)
    print("👉 После загрузки страницы нажмите кнопку 'Загрузить сейчас'.")

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     🚀 AVITO COMMANDER — ПУБЛИКАЦИЯ ЧЕРЕЗ ВЕБ-ИНТЕРФЕЙС║
    ║     Генерация → Валидация → Загрузка вручную → Avito   ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    xml_path = generate_xml()
    if not xml_path:
        return
    if not validate_xml(xml_path):
        print("\\n❌ Валидация не пройдена. Исправьте ошибки и попробуйте снова.")
        return
    show_upload_instructions(xml_path)
    open_avito_autoload()
    print("\\n" + "="*60)
    print("✅ ВСЁ ГОТОВО! После загрузки файла на GitHub нажмите 'Загрузить сейчас' в Avito.")
    print("="*60)

if __name__ == "__main__":
    main()
'''
    write_file(PROJECT_ROOT / "avito_publish.py", publish_content)

    # 4. Финальная инструкция
    print("\n" + "="*60)
    print("✅ УСТАНОВКА ЭТАПА 5 ЗАВЕРШЕНА!")
    print("="*60)
    print("\n📋 Теперь у вас есть:")
    print("  • update_phase5_xml_final.py  — генератор XML")
    print("  • validate_light.py           — быстрая валидация")
    print("  • avito_publish.py            — полный цикл (без Git)")
    print("\n🚀 Запустите полный цикл одной командой:")
    print("   python avito_publish.py")
    print("\n📖 Или пошагово:")
    print("   python update_phase5_xml_final.py")
    print("   python validate_light.py")
    print("   python avito_publish.py  # (откроет страницу загрузки)")

if __name__ == "__main__":
    main()
