#!/usr/bin/env python3
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
    print("\n" + "="*60)
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
        print("\n❌ Валидация не пройдена. Исправьте ошибки и попробуйте снова.")
        return
    show_upload_instructions(xml_path)
    open_avito_autoload()
    print("\n" + "="*60)
    print("✅ ВСЁ ГОТОВО! После загрузки файла на GitHub нажмите 'Загрузить сейчас' в Avito.")
    print("="*60)

if __name__ == "__main__":
    main()
