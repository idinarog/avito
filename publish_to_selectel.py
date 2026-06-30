#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Публикация XML-фида в Selectel S3 через API.
Читает ключи из .env файла.
"""

import os
import sys
import boto3
from botocore.exceptions import ClientError
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# ============================================================
# Чтение конфигурации из .env
# ============================================================
SELECTEL_CONFIG = {
    "endpoint_url": os.getenv("SELECTEL_ENDPOINT", "https://s3.selectel.ru"),
    "access_key": os.getenv("SELECTEL_ACCESS_KEY"),
    "secret_key": os.getenv("SELECTEL_SECRET_KEY"),
    "bucket_name": os.getenv("SELECTEL_BUCKET", "avito-feed"),
    "region_name": os.getenv("SELECTEL_REGION", "ru-1")
}

# Проверяем, что ключи заданы
if not SELECTEL_CONFIG["access_key"] or not SELECTEL_CONFIG["secret_key"]:
    print("❌ Ошибка: ключи доступа не найдены в .env файле!")
    print("   Добавьте SELECTEL_ACCESS_KEY и SELECTEL_SECRET_KEY в .env")
    sys.exit(1)

# Публичный URL бакета (после создания бакета)
# Формат: https://<UUID>.selstorage.ru/<имя_бакета>/
# ⚠️ ЗАМЕНИТЕ <UUID> на реальный UUID вашего бакета
PUBLIC_URL_BASE = f"https://<UUID>.selstorage.ru/{SELECTEL_CONFIG['bucket_name']}/"
# ============================================================


def get_s3_client():
    """Создает и возвращает клиент S3 для Selectel"""
    try:
        session = boto3.session.Session()
        s3_client = session.client(
            service_name='s3',
            endpoint_url=SELECTEL_CONFIG["endpoint_url"],
            aws_access_key_id=SELECTEL_CONFIG["access_key"],
            aws_secret_access_key=SELECTEL_CONFIG["secret_key"],
            region_name=SELECTEL_CONFIG["region_name"]
        )
        print("✅ S3 клиент создан успешно")
        return s3_client
    except Exception as e:
        print(f"❌ Ошибка создания S3 клиента: {e}")
        return None


def upload_file_to_selectel(local_file_path: str, s3_object_name: str = None) -> str:
    """
    Загружает файл в бакет Selectel и делает его публичным
    """
    if not os.path.exists(local_file_path):
        print(f"❌ Файл не найден: {local_file_path}")
        return None

    if s3_object_name is None:
        s3_object_name = os.path.basename(local_file_path)

    s3_client = get_s3_client()
    if not s3_client:
        return None

    try:
        print(f"⬆️ Загрузка {local_file_path} -> {SELECTEL_CONFIG['bucket_name']}/{s3_object_name}")

        s3_client.upload_file(
            Filename=local_file_path,
            Bucket=SELECTEL_CONFIG["bucket_name"],
            Key=s3_object_name,
            ExtraArgs={
                'ACL': 'public-read',
                'ContentType': 'application/xml'
            }
        )

        public_url = f"{PUBLIC_URL_BASE}{s3_object_name}"
        print(f"✅ Файл успешно загружен!")
        print(f"🔗 Публичная ссылка: {public_url}")
        return public_url

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        if error_code == 'NoSuchBucket':
            print(f"❌ Бакет '{SELECTEL_CONFIG['bucket_name']}' не существует!")
            print("   Создайте бакет в панели управления Selectel или через API.")
        elif error_code == 'AccessDenied':
            print("❌ Ошибка доступа! Проверьте ключи доступа.")
            print("   Убедитесь, что у бакета есть права на публичный доступ.")
        else:
            print(f"❌ Ошибка загрузки: {e}")
        return None
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return None


def list_bucket_files():
    """Показывает список файлов в бакете"""
    s3_client = get_s3_client()
    if not s3_client:
        return

    try:
        response = s3_client.list_objects_v2(
            Bucket=SELECTEL_CONFIG["bucket_name"]
        )

        if 'Contents' not in response:
            print("📁 Бакет пуст")
            return

        print("\n📋 Файлы в бакете:")
        for obj in response['Contents']:
            size_kb = obj['Size'] / 1024
            modified = obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
            print(f"  • {obj['Key']} ({size_kb:.1f} KB) — {modified}")

    except ClientError as e:
        print(f"❌ Ошибка получения списка: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")


def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         📤 ПУБЛИКАЦИЯ В SELECTEL S3                    ║
    ║         Avito Commander — Автозагрузка                 ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Проверяем, что бакет существует
    print("🔍 Проверка доступа к бакету...")
    s3_client = get_s3_client()
    if not s3_client:
        return

    try:
        s3_client.head_bucket(Bucket=SELECTEL_CONFIG["bucket_name"])
        print(f"✅ Бакет '{SELECTEL_CONFIG['bucket_name']}' доступен")
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        if error_code == 'NoSuchBucket':
            print(f"❌ Бакет '{SELECTEL_CONFIG['bucket_name']}' не найден!")
            print("\n📋 Инструкция по созданию бакета:")
            print("  1. Зайдите в панель управления Selectel")
            print("  2. Перейдите в раздел S3")
            print("  3. Нажмите 'Создать бакет'")
            print(f"  4. Введите имя: {SELECTEL_CONFIG['bucket_name']}")
            print("  5. Установите публичный доступ (Public)")
            return
        else:
            print(f"❌ Ошибка доступа к бакету: {e}")
            return

    # Находим последний XML-файл
    xml_files = sorted(
        Path(".").glob("avito_feed_*.xml"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )

    if not xml_files:
        print("❌ XML-файлы не найдены. Запустите генератор XML.")
        return

    latest_file = xml_files[0]
    print(f"\n📄 Найден файл: {latest_file}")
    print(f"📅 Создан: {datetime.fromtimestamp(latest_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")

    # Загружаем файл
    public_url = upload_file_to_selectel(str(latest_file))

    if public_url:
        print("\n" + "="*40)
        print("✅ ПУБЛИКАЦИЯ УСПЕШНО ЗАВЕРШЕНА!")
        print("\n📋 Дальнейшие действия:")
        print("  1. Скопируйте ссылку ниже:")
        print(f"     {public_url}")
        print("  2. Перейдите в настройки автозагрузки Avito")
        print("  3. В разделе 'Загрузка по ссылке' укажите эту ссылку")
        print("  4. Настройте расписание обновления")
        print("\n📊 Просмотр файлов в бакете:")
        list_bucket_files()
    else:
        print("\n❌ Публикация не удалась.")
        print("   Проверьте:")
        print("   - Правильность Access Key и Secret Key в .env")
        print("   - Существование бакета")
        print("   - Настройки доступа к бакету")


if __name__ == "__main__":
    main()
