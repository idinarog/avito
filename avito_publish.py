#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Автоматическая публикация XML-фида Avito Commander.
Генерация → Валидация → Публикация на GitHub → Проверка на валидаторе Avito.
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ======================== НАСТРОЙКИ ============================
GITHUB_REPO_PATH = Path.home() / "avito_commander" / "avitoxml"
GITHUB_REMOTE_URL = "https://github.com/idinarog/avitoxml.git"
XML_FILENAME = "avito_feed.xml"
GENERATOR_SCRIPT = "update_phase5_xml_final.py"
VALIDATOR_URL = "https://autoload.avito.ru/format/xmlcheck/"
# ==============================================================

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
    # ... (оставляем без изменений) ...
    print_header("2️⃣ ВАЛИДАЦИЯ XML")
    print("📄 Файл: {}".format(xml_path.name))
    print("📅 Создан: {}".format(datetime.fromtimestamp(xml_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')))
    try:
        import xml.etree.ElementTree as ET
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
    except Exception as e:
        print("❌ Ошибка парсинга XML: {}".format(e))
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

def validate_xml_by_link(link):
    """
    Открывает валидатор Avito, вставляет ссылку, запускает проверку и выводит результат.
    """
    print_header("4️⃣ ПРОВЕРКА НА ВАЛИДАТОРЕ AVITO")
    print("🌐 Открываю валидатор и проверяю ссылку...")

    # Настройка драйвера
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # Уберите эту строку, если хотите видеть браузер
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(VALIDATOR_URL)
        wait = WebDriverWait(driver, 20)

        # 1. Переключиться на вкладку "По ссылке"
        link_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'По ссылке')]")))
        link_tab.click()
        print("   ✅ Переключились на вкладку 'По ссылке'")

        # 2. Вставить ссылку
        link_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='url' or @placeholder='Ссылка']")))
        link_input.clear()
        link_input.send_keys(link)
        print("   ✅ Ссылка вставлена")

        # 3. Нажать кнопку "Проверить"
        check_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Проверить')]")))
        check_button.click()
        print("   ✅ Нажата кнопка 'Проверить'")

        # 4. Дождаться результата
        time.sleep(5)  # Даём время на проверку
        result_element = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'result')]")))
        result_text = result_element.text

        print("\n📋 РЕЗУЛЬТАТ ПРОВЕРКИ:")
        print("-" * 40)
        print(result_text)
        print("-" * 40)

        driver.quit()
        return True

    except Exception as e:
        print("❌ Ошибка при проверке на валидаторе: {}".format(e))
        try:
            driver.quit()
        except:
            pass
        return False

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
        print("\n❌ Публикация на GitHub не удалась.")
        return

    # Формируем ссылку на файл
    raw_link = "https://raw.githubusercontent.com/idinarog/avitoxml/main/{}".format(XML_FILENAME)

    # Выполняем проверку на валидаторе Avito
    validate_xml_by_link(raw_link)

    print("\n" + "="*60)
    print("✅ ВСЁ ГОТОВО! Файл опубликован и проверен.")
    print("="*60)

if __name__ == "__main__":
    main()