#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Автоматическая публикация XML-фида Avito Commander.
Генерация → Валидация → Публикация на GitHub → Проверка.
"""

import os
import sys
import subprocess
import shutil
import webbrowser
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

GITHUB_REPO_PATH = Path.home() / "avito_commander" / "avitoxml"
GITHUB_REMOTE_URL = "https://github.com/idinarog/avitoxml.git"
XML_FILENAME = "avito_feed.xml"
GENERATOR_SCRIPT = "update_phase5_xml_final.py"
VALIDATOR_URL = "https://autoload.avito.ru/format/xmlcheck/"

def print_header(text):
    print("\n" + "="*60)
    print("  " + text)
    print("="*60)

def generate_xml():
    print_header("1️⃣ ГЕНЕРАЦИЯ XML")
    if not os.path.exists(GENERATOR_SCRIPT):
        print("❌ Генератор {} не найден!".format(GENERATOR_SCRIPT))
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
    print("📄 Файл: {}".format(xml_path.name))
    print("📅 Создан: {}".format(datetime.fromtimestamp(xml_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')))
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
            print("  Найдено объявлений: {}".format(len(ads)))
            for i, ad in enumerate(ads, 1):
                for field in ["Id", "Title", "Category", "Price", "Description"]:
                    if ad.find(field) is None:
                        errors.append("Объявление #{}: отсутствует <{}>".format(i, field))
                price_elem = ad.find("Price")
                if price_elem is not None and price_elem.text:
                    try:
                        int(price_elem.text)
                    except ValueError:
                        warnings.append("Объявление #{}: цена не число: '{}'".format(i, price_elem.text))
                id_elem = ad.find("Id")
                if id_elem is not None and not id_elem.text:
                    warnings.append("Объявление #{}: <Id> пустое".format(i))
        if errors:
            print("\n❌ Критические ошибки:")
            for err in errors:
                print("  • {}".format(err))
            return False
        elif warnings:
            print("\n⚠️ Предупреждения:")
            for warn in warnings:
                print("  • {}".format(warn))
            print("\n✅ Базовая структура OK (с предупреждениями)")
            return True
        else:
            print("\n✅ Всё отлично! XML корректен.")
            return True
    except ET.ParseError as e:
        print("❌ Ошибка парсинга XML: {}".format(e))
        return False
    except Exception as e:
        print("❌ Неожиданная ошибка: {}".format(e))
        return False

def publish_to_github(xml_path):
    print_header("3️⃣ ПУБЛИКАЦИЯ НА GITHUB")
    if not GITHUB_REPO_PATH.exists():
        print("❌ Репозиторий не найден: {}".format(GITHUB_REPO_PATH))
        return False
    dest_path = GITHUB_REPO_PATH / XML_FILENAME
    try:
        shutil.copy2(xml_path, dest_path)
        print("✅ Файл скопирован: {}".format(dest_path))
    except Exception as e:
        print("❌ Ошибка копирования: {}".format(e))
        return False
    os.chdir(GITHUB_REPO_PATH)
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not status.stdout.strip():
        print("ℹ️ Нет изменений для коммита. Файл уже актуален.")
        return True
    try:
        subprocess.run(["git", "config", "user['name']"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user['email']"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("⚠️ Git не настроен! Выполните:")
        print("  cd {}".format(GITHUB_REPO_PATH))
        print('  git config user['name'] "Ваше Имя"')
        print('  git config user['email'] "ваш_email@example.com"')
        return False
    try:
        subprocess.run(["git", "add", XML_FILENAME], check=True, capture_output=True)
        commit_msg = "Обновление фида от {}".format(datetime.now().strftime('%Y-%m-%d %H:%M'))
        subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True)
        print("✅ Изменения запушены на GitHub")
        raw_url = "https://raw.githubusercontent.com/idinarog/avitoxml/main/{}".format(XML_FILENAME)
        print("\n🔗 Прямая ссылка (для Avito):\n   {}".format(raw_url))
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Ошибка Git: {}".format(e.stderr.decode() if e.stderr else str(e)))
        return False

def open_validator():
    print_header("4️⃣ ПРОВЕРКА НА ВАЛИДАТОРЕ AVITO")
    link = "https://raw.githubusercontent.com/idinarog/avitoxml/main/{}".format(XML_FILENAME)
    print("\n🔗 Ваша ссылка для проверки:")
    print(f"   {link}")

    try:
        import pyperclip
        pyperclip.copy(link)
        print("✅ Ссылка скопирована в буфер обмена!")
    except ImportError:
        print("⚠️ Установите pyperclip: pip install pyperclip")
        print("   Или скопируйте ссылку вручную.")

    print("\n👉 Действия:")
    print("   1. Откройте страницу валидатора (браузер откроется автоматически)")
    print("   2. Переключитесь на вкладку 'По ссылке'")
    print("   3. Вставьте ссылку (Ctrl+V / Cmd+V) и нажмите 'Проверить'")
    print("   4. Убедитесь, что ошибок нет")

    webbrowser.open(VALIDATOR_URL)
    return True

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     🚀 AVITO COMMANDER — АВТОМАТИЧЕСКАЯ ПУБЛИКАЦИЯ     ║
    ║     Генерация → Валидация → GitHub → Проверка          ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    xml_path = generate_xml()
    if not xml_path:
        return
    if not validate_xml(xml_path):
        print("\n❌ Локальная валидация не пройдена. Исправьте ошибки и попробуйте снова.")
        return
    if not publish_to_github(xml_path):
        print("\n⚠️ Публикация на GitHub не удалась.")
    open_validator()
    print("\n" + "="*60)
    print("✅ ВСЁ ГОТОВО! Проверьте фид на валидаторе и вставьте ссылку в настройки Avito.")
    print("="*60)

if __name__ == "__main__":
    main()
