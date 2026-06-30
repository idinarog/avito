#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Быстрый запуск Avito Commander
С проверкой настроек перед запуском
"""

import os
import sys
from pathlib import Path

def check_env():
    """Проверяет наличие и настройку .env файла"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env файл не найден!")
        print("Создайте .env файл с вашими ключами:")
        print("""
AVITO_CLIENT_ID=ВАШ_CLIENT_ID_ОТ_ПУБЛИЧНОГО_ПРИЛОЖЕНИЯ
AVITO_CLIENT_SECRET=ВАШ_CLIENT_SECRET_ОТ_ПУБЛИЧНОГО_ПРИЛОЖЕНИЯ
AVITO_REDIRECT_URI=https://sk-consulting.group/
        """)
        return False
    
    # Проверяем наличие ключей
    with open(env_path, 'r') as f:
        content = f.read()
       # if "ВАШ_CLIENT_ID" in content or "your_client_id" in content:
       #    print("⚠️ В .env файле используются примеры ключей!")
       #    print("Замените их на реальные ключи из кабинета разработчика.")
       #     return False
    
    return True

def main():
    print("""
    ╔═══════════════════════════════════════════╗
    ║     Avito Commander v1.0.0              ║
    ║     Управление объявлениями Avito       ║
    ╚═══════════════════════════════════════════╝
    """)
    
    if not check_env():
        print("\nНастройте .env файл и запустите снова.")
        sys.exit(1)
    
    # Запускаем приложение
    from main import main as run_app
    run_app()

if __name__ == "__main__":
    main()
