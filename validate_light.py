#!/usr/bin/env python3
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
            print("\n❌ Критические ошибки:")
            for err in errors:
                print(f"  • {err}")
            return False
        elif warnings:
            print("\n⚠️ Предупреждения:")
            for warn in warnings:
                print(f"  • {warn}")
            print("\n✅ Базовая структура OK (с предупреждениями)")
            return True
        else:
            print("\n✅ Всё отлично! XML корректен.")
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
        print("\n✅ Файл готов к публикации!")
    else:
        print("\n❌ Исправьте ошибки и сгенерируйте XML заново.")

if __name__ == "__main__":
    main()
