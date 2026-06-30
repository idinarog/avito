#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для исправления URL авторизации в Avito
Заменяет старый URL на новый: https://avito.ru/oauth
"""

import os
import re
import sys
from pathlib import Path


def fix_auth_url():
    """
    Исправляет URL авторизации в файле ui/login_dialog.py
    """
    file_path = Path("ui/login_dialog.py")
    
    # Проверяем существование файла
    if not file_path.exists():
        print(f"❌ Файл {file_path} не найден!")
        print("Убедитесь, что вы находитесь в корневой папке проекта")
        return False
    
    # Читаем содержимое файла
    print(f"📖 Читаем файл: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Паттерны для поиска
    old_patterns = [
        # Старый URL с www.avito.ru
        r'auth_url = f"https://www\.avito\.ru/oauth/authorize\?{.*?}"',
        # Старый URL без www
        r'auth_url = f"https://avito\.ru/oauth/authorize\?{.*?}"',
        # Любой вариант с authorize
        r'auth_url = f".*?/oauth/authorize\?.*?"',
    ]
    
    # Новый URL
    new_auth_url = 'auth_url = f"https://avito.ru/oauth?{urlencode(auth_params)}"'
    
    # Проверяем, содержит ли файл старый URL
    has_old = False
    for pattern in old_patterns:
        if re.search(pattern, content, re.DOTALL):
            has_old = True
            break
    
    if not has_old:
        print("⚠️ Старый URL не найден. Проверяем, может быть уже исправлен...")
        
        # Проверяем, есть ли новый URL
        if 'auth_url = f"https://avito.ru/oauth?{urlencode(auth_params)}"' in content:
            print("✅ URL уже исправлен! Ничего не делаем.")
            return True
        else:
            # Пробуем найти метод и заменить вручную
            print("🔍 Пытаемся найти метод auth_via_avito...")
            return fix_method_manually(content, file_path)
    
    # Заменяем все вхождения
    print("🔄 Замена URL на корректный...")
    new_content = content
    for pattern in old_patterns:
        new_content = re.sub(pattern, new_auth_url, new_content)
    
    # Дополнительная проверка: убеждаемся, что нет оставшихся старых URL
    if 'oauth/authorize' in new_content:
        print("⚠️ В файле остались ссылки с /authorize, заменяем их...")
        new_content = new_content.replace('oauth/authorize', 'oauth')
    
    # Сохраняем изменения
    print("💾 Сохраняем изменения...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Файл успешно обновлен!")
    print(f"📁 Файл: {file_path}")
    
    # Показываем изменения
    print("\n📋 Изменения:")
    print("- https://www.avito.ru/oauth/authorize → https://avito.ru/oauth")
    
    return True


def fix_method_manually(content, file_path):
    """
    Если не удалось найти паттерн, пробуем заменить метод целиком
    """
    # Ищем метод auth_via_avito
    method_start = content.find('def auth_via_avito')
    if method_start == -1:
        print("❌ Метод auth_via_avito не найден в файле!")
        return False
    
    print("🔍 Найден метод auth_via_avito, заменяем целиком...")
    
    # Новый метод
    new_method = '''    def auth_via_avito(self):
        """Открывает браузер для OAuth авторизации через Avito"""
        try:
            # Получаем данные для авторизации из конфига
            client_id = self.app.config.get("avito_client_id")
            redirect_uri = self.app.config.get("avito_redirect_uri")
            
            if not client_id or client_id == "your_client_id_here":
                self.status_label.setText("❌ Client ID не настроен. Проверьте .env файл")
                self.status_label.setStyleSheet("color: #FF6B6B;")
                return
            
            # Формируем URL для OAuth
            from urllib.parse import urlencode
            auth_params = {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": "read write"
            }
            # ✅ Исправленный URL
            auth_url = f"https://avito.ru/oauth?{urlencode(auth_params)}"
            
            # Открываем в браузере
            webbrowser.open(auth_url)
            
            self.status_label.setText("✅ Браузер открыт. Войдите в Avito и скопируйте код.")
            self.status_label.setStyleSheet("color: #00A651;")
            
            # Показываем инструкцию
            QMessageBox.information(
                self,
                "Инструкция по авторизации",
                "1. Войдите в свой аккаунт Avito в открывшемся окне\\n"
                "2. Разрешите доступ приложению Avito Commander\\n"
                "3. После авторизации вы будете перенаправлены на сайт\\n"
                "4. В URL будет параметр code=XXXXXXXX\\n"
                "5. Скопируйте этот код и вставьте в поле ниже\\n"
                "6. Нажмите 'Войти'",
                QMessageBox.Ok
            )
            
        except Exception as e:
            self.status_label.setText(f"❌ Ошибка: {str(e)}")
            self.status_label.setStyleSheet("color: #FF6B6B;")'''
    
    # Находим конец метода (следующий def или конец файла)
    # Ищем следующую функцию или конец класса
    next_def = content.find('def ', method_start + 10)
    if next_def != -1:
        # Находим отступы для определения конца метода
        end_pos = content.find('\n\n    def ', method_start)
        if end_pos != -1:
            # Начинаем с начала метода и до следующей функции
            content_parts = [
                content[:method_start],
                new_method,
                content[end_pos:]
            ]
        else:
            # Если это последний метод в классе
            content_parts = [
                content[:method_start],
                new_method
            ]
    else:
        # Если нет других методов
        content_parts = [
            content[:method_start],
            new_method
        ]
    
    # Собираем новый контент
    new_content = ''.join(content_parts)
    
    # Дополнительная проверка: удаляем старые импорты если они есть
    if 'from urllib.parse import urlencode' not in new_content:
        # Добавляем импорт в начало файла
        if 'from PyQt5.QtGui import *' in new_content:
            new_content = new_content.replace(
                'from PyQt5.QtGui import *',
                'from PyQt5.QtGui import *\nfrom urllib.parse import urlencode'
            )
    
    # Сохраняем изменения
    print("💾 Сохраняем изменения...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Метод успешно заменен!")
    return True


def create_backup():
    """Создает резервную копию файла перед изменением"""
    file_path = Path("ui/login_dialog.py")
    if not file_path.exists():
        return False
    
    backup_path = file_path.with_suffix(file_path.suffix + '.backup')
    print(f"📦 Создаем резервную копию: {backup_path}")
    
    import shutil
    shutil.copy2(file_path, backup_path)
    print("✅ Резервная копия создана")
    return True


def main():
    """Главная функция"""
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║     Исправление URL авторизации Avito           ║
    ║     https://avito.ru/oauth                      ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    # Проверяем, что мы в корневой папке
    if not Path("ui").exists() or not Path("main.py").exists():
        print("❌ Похоже, вы не в корневой папке проекта!")
        print("📍 Текущая папка:", os.getcwd())
        print("📁 Должны быть папки: ui/, core/, api/, etc.")
        return
    
    # Создаем резервную копию
    if not create_backup():
        print("⚠️ Не удалось создать резервную копию. Продолжаем без нее...")
    
    # Исправляем URL
    if fix_auth_url():
        print("\n" + "="*50)
        print("✅ ГОТОВО! Теперь можно запускать приложение:")
        print("   python main.py")
        print("="*50)
    else:
        print("\n❌ Не удалось автоматически исправить файл.")
        print("📝 Рекомендации:")
        print("1. Откройте файл ui/login_dialog.py вручную")
        print("2. Найдите метод auth_via_avito()")
        print("3. Замените URL на: https://avito.ru/oauth")
        print("\nИли скопируйте корректный код метода из документации.")


if __name__ == "__main__":
    main()