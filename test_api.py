#!/usr/bin/env python3
"""
Тестовый скрипт для проверки Avito API
Использует токен из базы данных или переменной окружения.
"""

import os
import sqlite3
import requests
import json
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

# 1. Пробуем получить токен из базы данных
db_path = os.getenv("db_path", "avito_commander.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.execute("SELECT access_token FROM users WHERE is_active = 1 ORDER BY id DESC LIMIT 1")
row = cursor.fetchone()
conn.close()

if row and row['access_token']:
    access_token = row['access_token']
    print(f"✅ Токен из БД: {access_token[:20]}...")
else:
    print("❌ Токен не найден в БД. Попробуйте сначала войти в приложение.")
    exit(1)

# 2. Формируем запрос к API
url = "https://api.avito.ru/core/v1/items"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}
params = {
    "page": 1,
    "per_page": 50
}

print(f"🔗 Запрос к {url}")
print(f"🔑 Заголовки: {headers}")
print(f"📦 Параметры: {params}")

try:
    response = requests.get(url, headers=headers, params=params)
    print(f"📊 Статус: {response.status_code}")
    print(f"📄 Ответ:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"❌ Ошибка: {e}")
