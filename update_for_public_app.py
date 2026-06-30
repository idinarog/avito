#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для обновления приложения для работы с публичным OAuth 2.0
Поддерживает авторизацию пользователей с платным тарифом Avito
"""

import os
import re
import sys
import shutil
from pathlib import Path


class AppUpdater:
    """Класс для обновления приложения"""
    
    def __init__(self):
        self.files_updated = []
        self.files_backup = []
        self.errors = []
        
        # Цвета для вывода
        self.GREEN = '\033[92m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.BLUE = '\033[94m'
        self.RESET = '\033[0m'
        self.BOLD = '\033[1m'
    
    def print_header(self, text):
        print(f"\n{self.BOLD}{self.BLUE}{'='*60}{self.RESET}")
        print(f"{self.BOLD}{self.BLUE}{text:^60}{self.RESET}")
        print(f"{self.BOLD}{self.BLUE}{'='*60}{self.RESET}\n")
    
    def print_success(self, text):
        print(f"{self.GREEN}✅ {text}{self.RESET}")
    
    def print_error(self, text):
        print(f"{self.RED}❌ {text}{self.RESET}")
        self.errors.append(text)
    
    def print_info(self, text):
        print(f"{self.BLUE}ℹ️ {text}{self.RESET}")
    
    def backup_file(self, file_path):
        """Создает резервную копию файла"""
        if not file_path.exists():
            return False
        
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        shutil.copy2(file_path, backup_path)
        self.files_backup.append(str(backup_path))
        return True
    
    def update_env_file(self):
        """Обновляет .env файл с комментариями"""
        self.print_header("1. ОБНОВЛЕНИЕ .ENV ФАЙЛА")
        
        env_path = Path(".env")
        
        # Создаем резервную копию
        if env_path.exists():
            self.backup_file(env_path)
        
        # Новое содержимое .env
        new_env = """# Avito API - Публичное приложение
# ⚠️ Замените на свои ключи после регистрации приложения!
AVITO_CLIENT_ID=ВАШ_CLIENT_ID_ОТ_ПУБЛИЧНОГО_ПРИЛОЖЕНИЯ
AVITO_CLIENT_SECRET=ВАШ_CLIENT_SECRET_ОТ_ПУБЛИЧНОГО_ПРИЛОЖЕНИЯ
AVITO_REDIRECT_URI=https://sk-consulting.group/

# Telegram Bot (опционально)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Настройки приложения
APP_NAME=Avito Commander
APP_VERSION=1.0.0
THEME=dark
AUTO_SYNC=true
SYNC_INTERVAL=3600
"""
        
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(new_env)
        
        self.print_success(".env файл обновлен")
        self.print_info("Не забудьте заменить ВАШ_CLIENT_ID_ОТ_ПУБЛИЧНОГО_ПРИЛОЖЕНИЯ на реальные ключи!")
        self.files_updated.append(str(env_path))
    
    def update_login_dialog(self):
        """Обновляет ui/login_dialog.py"""
        self.print_header("2. ОБНОВЛЕНИЕ LOGIN_DIALOG.PY")
        
        file_path = Path("ui/login_dialog.py")
        
        if not file_path.exists():
            self.print_error("Файл ui/login_dialog.py не найден!")
            return False
        
        # Создаем резервную копию
        self.backup_file(file_path)
        
        # Читаем содержимое
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Новый метод auth_via_avito
        new_auth_method = '''    def auth_via_avito(self):
        """Открывает браузер для OAuth авторизации через Avito"""
        try:
            client_id = self.app.config.get("avito_client_id")
            redirect_uri = self.app.config.get("avito_redirect_uri")
            
            if not client_id or client_id == "your_client_id_here" or client_id == "ВАШ_CLIENT_ID_ОТ_ПУБЛИЧНОГО_ПРИЛОЖЕНИЯ":
                self.status_label.setText("❌ Client ID не настроен. Проверьте .env файл")
                self.status_label.setStyleSheet("color: #FF6B6B;")
                return
            
            from urllib.parse import urlencode
            
            # ✅ Правильные параметры для публичного OAuth 2.0
            auth_params = {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": "items:info,stats:read,user:read",  # Явно указываем scope
                "pro_users_flow": "true"
            }
            
            auth_url = f"https://avito.ru/oauth?{urlencode(auth_params)}"
            
            print(f"🔗 Открываем URL: {auth_url}")
            webbrowser.open(auth_url)
            
            self.status_label.setText("✅ Браузер открыт. Войдите в Avito и скопируйте код.")
            self.status_label.setStyleSheet("color: #00A651;")
            
            QMessageBox.information(
                self,
                "Инструкция по авторизации",
                "1. Войдите в свой аккаунт Avito в открывшемся окне\\n"
                "2. Разрешите доступ приложению Avito Commander\\n"
                "3. После авторизации в URL будет параметр code=XXXXXXXX\\n"
                "4. Скопируйте этот код и вставьте в поле ниже\\n"
                "5. Нажмите 'Войти'\\n\\n"
                "⚠️ Важно: у вас должен быть подключен платный тариф Avito!",
                QMessageBox.Ok
            )
            
        except Exception as e:
            self.status_label.setText(f"❌ Ошибка: {str(e)}")
            self.status_label.setStyleSheet("color: #FF6B6B;")
            print(f"❌ Ошибка авторизации: {e}")'''
        
        # Заменяем метод
        pattern = r'def auth_via_avito\(self\):.*?(?=\n    def |\nclass |\Z)'
        new_content = re.sub(pattern, new_auth_method, content, flags=re.DOTALL)
        
        # Проверяем, есть ли импорт webbrowser
        if 'import webbrowser' not in new_content:
            new_content = new_content.replace(
                'from PyQt5.QtGui import *',
                'from PyQt5.QtGui import *\nimport webbrowser'
            )
        
        # Сохраняем
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        self.print_success("ui/login_dialog.py обновлен")
        self.files_updated.append(str(file_path))
        return True
    
    def update_avito_api(self):
        """Обновляет api/avito_api.py"""
        self.print_header("3. ОБНОВЛЕНИЕ AVITO_API.PY")
        
        file_path = Path("api/avito_api.py")
        
        if not file_path.exists():
            self.print_error("Файл api/avito_api.py не найден!")
            return False
        
        self.backup_file(file_path)
        
        # Читаем содержимое
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Добавляем метод для Client Credentials
        new_methods = '''
    
    def get_token_client_credentials(self) -> Optional[str]:
        """
        Получение токена через Client Credentials
        Используется для доступа к своему профилю
        """
        try:
            import requests
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            
            response = requests.post("https://api.avito.ru/token", data=data)
            if response.status_code == 200:
                tokens = response.json()
                self.auth.access_token = tokens.get("access_token")
                return self.auth.access_token
            else:
                print(f"❌ Ошибка получения токена: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    def get_my_items(self, user_id: str):
        """Получение своих объявлений (для Client Credentials)"""
        token = self.get_token_client_credentials()
        if not token:
            return {"items": []}
        
        headers = self._get_headers()
        try:
            response = requests.get(
                f"{self.base_url}core/v1/accounts/{user_id}/items",
                headers=headers
            )
            if response.status_code == 200:
                return response.json()
            return {"items": []}
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return {"items": []}
'''
        
        # Добавляем методы перед последним return или в конец класса
        if 'class AvitoAPI:' in content:
            # Находим конец класса
            class_end = content.rfind('    def ')
            if class_end != -1:
                # Ищем последний метод и вставляем перед ним
                last_method_start = content.rfind('    def ', class_end)
                if last_method_start != -1:
                    # Вставляем новые методы перед последним методом
                    insert_pos = last_method_start
                    new_content = content[:insert_pos] + new_methods + content[insert_pos:]
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    self.print_success("api/avito_api.py обновлен")
                    self.files_updated.append(str(file_path))
                    return True
        
        # Если не удалось найти место, просто добавляем в конец
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(new_methods)
        
        self.print_success("api/avito_api.py обновлен (добавлено в конец)")
        self.files_updated.append(str(file_path))
        return True
    
    def update_main_app(self):
        """Обновляет ui/main_window.py"""
        self.print_header("4. ОБНОВЛЕНИЕ MAIN_WINDOW.PY")
        
        file_path = Path("ui/main_window.py")
        
        if not file_path.exists():
            self.print_error("Файл ui/main_window.py не найден!")
            return False
        
        self.backup_file(file_path)
        
        # Читаем содержимое
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Добавляем проверку платного тарифа в sync_items
        sync_method_check = '''
        # Проверяем, есть ли у пользователя платный тариф
        try:
            # Пробуем получить объявления
            test_items = self.app.sync_service.sync_items(project_id)
            if not test_items:
                # Если объявлений нет, это может быть бесплатный аккаунт
                reply = QMessageBox.question(
                    self,
                    "Проверка тарифа",
                    "Не удалось загрузить объявления.\\n\\n"
                    "Убедитесь, что у вас подключен платный тариф Avito.\\n"
                    "Бесплатные аккаунты не поддерживаются.\\n\\n"
                    "Продолжить работу в демо-режиме?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
        except Exception as e:
            if "403" in str(e) or "forbidden" in str(e).lower():
                QMessageBox.warning(
                    self,
                    "Доступ запрещен",
                    "Для работы с приложением требуется платный тариф Avito.\\n\\n"
                    "Подключите тариф в личном кабинете Avito и попробуйте снова.",
                    QMessageBox.Ok
                )
                return
            raise
'''
        
        # Ищем метод sync_items и добавляем проверку
        if 'def sync_items(self):' in content:
            # Находим метод и добавляем проверку после получения project_id
            pattern = r'(def sync_items\(self\):.*?project_id = projects\[0\]\.id)'
            replacement = r'\1' + sync_method_check
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        else:
            new_content = content
        
        # Сохраняем
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        self.print_success("ui/main_window.py обновлен")
        self.files_updated.append(str(file_path))
        return True
    
    def create_quick_start(self):
        """Создает файл quick_start.py для быстрого запуска"""
        self.print_header("5. СОЗДАНИЕ QUICK_START.PY")
        
        file_path = Path("quick_start.py")
        
        quick_start_content = '''#!/usr/bin/env python3
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
        if "ВАШ_CLIENT_ID" in content or "your_client_id" in content:
            print("⚠️ В .env файле используются примеры ключей!")
            print("Замените их на реальные ключи из кабинета разработчика.")
            return False
    
    return True

def main():
    print("""
    ╔═══════════════════════════════════════════╗
    ║     Avito Commander v1.0.0              ║
    ║     Управление объявлениями Avito       ║
    ╚═══════════════════════════════════════════╝
    """)
    
    if not check_env():
        print("\\nНастройте .env файл и запустите снова.")
        sys.exit(1)
    
    # Запускаем приложение
    from main import main as run_app
    run_app()

if __name__ == "__main__":
    main()
'''
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(quick_start_content)
        
        # Делаем исполняемым
        os.chmod(file_path, 0o755)
        
        self.print_success("quick_start.py создан")
        self.files_updated.append(str(file_path))
        return True
    
    def show_summary(self):
        """Показывает итоговый отчет"""
        self.print_header("📊 ИТОГОВЫЙ ОТЧЕТ")
        
        print(f"\n{self.BOLD}Обновленные файлы:{self.RESET}")
        for file in self.files_updated:
            print(f"  ✅ {file}")
        
        print(f"\n{self.BOLD}Резервные копии:{self.RESET}")
        for file in self.files_backup:
            print(f"  📦 {file}")
        
        if self.errors:
            print(f"\n{self.RED}Ошибки:{self.RESET}")
            for error in self.errors:
                print(f"  ❌ {error}")
        
        print(f"\n{self.BOLD}{self.GREEN}✅ Обновление завершено!{self.RESET}")
        print(f"\n{self.BOLD}📋 Дальнейшие действия:{self.RESET}")
        print(f"  1. {self.BOLD}Замените{self.RESET} ключи в .env файле на реальные:")
        print(f"     AVITO_CLIENT_ID=ваш_новый_client_id")
        print(f"     AVITO_CLIENT_SECRET=ваш_новый_client_secret")
        print(f"  2. {self.BOLD}Зарегистрируйте{self.RESET} приложение в кабинете разработчика")
        print(f"  3. {self.BOLD}Запустите{self.RESET} приложение: python quick_start.py")
        print(f"\n{self.BOLD}⚠️ Важно:{self.RESET} Приложение работает только с платными тарифами Avito!")
    
    def run(self):
        """Запуск всех обновлений"""
        print(self.BOLD + """
    ╔═══════════════════════════════════════════════════════════╗
    ║      🔄 ОБНОВЛЕНИЕ ДЛЯ ПУБЛИЧНОГО OAuth 2.0            ║
    ║      Avito Commander - Платные тарифы                  ║
    ╚═══════════════════════════════════════════════════════════╝
    """ + self.RESET)
        
        # Проверяем, что мы в корне проекта
        if not Path("main.py").exists():
            self.print_error("Запустите скрипт из корневой папки проекта!")
            return
        
        # Выполняем обновления
        self.update_env_file()
        self.update_login_dialog()
        self.update_avito_api()
        self.update_main_app()
        self.create_quick_start()
        
        # Показываем итоги
        self.show_summary()


def main():
    updater = AppUpdater()
    updater.run()


if __name__ == "__main__":
    main()
