#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для проверки настроек авторизации Avito
Проверяет .env файл, доступность сайта и правильность параметров
"""

import os
import re
import sys
import requests
from pathlib import Path
from urllib.parse import urlparse


class AvitoAuthChecker:
    """Класс для проверки настроек авторизации Avito"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success = []
        
        # Цвета для вывода
        self.RED = '\033[91m'
        self.GREEN = '\033[92m'
        self.YELLOW = '\033[93m'
        self.BLUE = '\033[94m'
        self.RESET = '\033[0m'
        self.BOLD = '\033[1m'
    
    def print_header(self, text):
        """Вывод заголовка"""
        print(f"\n{self.BOLD}{self.BLUE}{'='*60}{self.RESET}")
        print(f"{self.BOLD}{self.BLUE}{text:^60}{self.RESET}")
        print(f"{self.BOLD}{self.BLUE}{'='*60}{self.RESET}\n")
    
    def print_success(self, text):
        """Вывод успешного сообщения"""
        print(f"{self.GREEN}✅ {text}{self.RESET}")
        self.success.append(text)
    
    def print_error(self, text):
        """Вывод сообщения об ошибке"""
        print(f"{self.RED}❌ {text}{self.RESET}")
        self.errors.append(text)
    
    def print_warning(self, text):
        """Вывод предупреждения"""
        print(f"{self.YELLOW}⚠️ {text}{self.RESET}")
        self.warnings.append(text)
    
    def print_info(self, text):
        """Вывод информационного сообщения"""
        print(f"{self.BLUE}ℹ️ {text}{self.RESET}")
    
    def check_env_file(self):
        """Проверка .env файла"""
        self.print_header("1. ПРОВЕРКА .ENV ФАЙЛА")
        
        env_path = Path(".env")
        
        if not env_path.exists():
            self.print_error(".env файл не найден!")
            self.print_info("Создайте файл .env в корне проекта")
            return False
        
        self.print_success(".env файл найден")
        
        # Читаем .env
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем обязательные поля
        required_fields = {
            "AVITO_CLIENT_ID": "Client ID",
            "AVITO_CLIENT_SECRET": "Client Secret",
            "AVITO_REDIRECT_URI": "Redirect URI"
        }
        
        values = {}
        
        for key, name in required_fields.items():
            # Ищем значение
            pattern = rf'^{key}=(.+)$'
            found = False
            
            for line in content.split('\n'):
                match = re.search(pattern, line.strip())
                if match:
                    value = match.group(1).strip()
                    values[key] = value
                    found = True
                    break
            
            if not found:
                self.print_error(f"{name} не найден в .env файле!")
                return False
            
            if not values[key] or values[key] == "your_client_id_here":
                self.print_error(f"{name} не заполнен! Значение: {values[key]}")
                return False
        
        self.print_success("Все обязательные поля заполнены")
        
        # Проверяем значения
        self.print_info(f"Client ID: {values['AVITO_CLIENT_ID']}")
        self.print_info(f"Client Secret: {values['AVITO_CLIENT_SECRET'][:10]}...{values['AVITO_CLIENT_SECRET'][-5:]}")
        self.print_info(f"Redirect URI: {values['AVITO_REDIRECT_URI']}")
        
        return values
    
    def check_client_id(self, client_id):
        """Проверка Client ID"""
        self.print_header("2. ПРОВЕРКА CLIENT ID")
        
        # Проверяем длину
        if len(client_id) < 10:
            self.print_error(f"Client ID слишком короткий: {len(client_id)} символов")
            return False
        
        self.print_success(f"Длина Client ID: {len(client_id)} символов (нормально)")
        
        # Проверяем наличие запрещенных символов
        if not re.match(r'^[a-zA-Z0-9]+$', client_id):
            self.print_warning("Client ID содержит нестандартные символы")
        else:
            self.print_success("Client ID содержит только допустимые символы")
        
        return True
    
    def check_client_secret(self, client_secret):
        """Проверка Client Secret"""
        self.print_header("3. ПРОВЕРКА CLIENT SECRET")
        
        # Проверяем длину
        if len(client_secret) < 20:
            self.print_error(f"Client Secret слишком короткий: {len(client_secret)} символов")
            return False
        
        self.print_success(f"Длина Client Secret: {len(client_secret)} символов (нормально)")
        
        # Проверяем наличие специальных символов
        if re.search(r'[^a-zA-Z0-9_-]', client_secret):
            self.print_warning("Client Secret содержит специальные символы")
        else:
            self.print_success("Client Secret содержит только допустимые символы")
        
        return True
    
    def check_redirect_uri(self, redirect_uri):
        """Проверка Redirect URI"""
        self.print_header("4. ПРОВЕРКА REDIRECT URI")
        
        # Проверяем формат URL
        try:
            parsed = urlparse(redirect_uri)
            
            if not parsed.scheme:
                self.print_error("Отсутствует протокол (http:// или https://)")
                return False
            else:
                self.print_success(f"Протокол: {parsed.scheme}")
            
            if not parsed.netloc:
                self.print_error("Отсутствует домен")
                return False
            else:
                self.print_success(f"Домен: {parsed.netloc}")
            
            if not redirect_uri.endswith('/'):
                self.print_warning("Redirect URI не заканчивается слэшем /")
                self.print_info("Avito может не принять URL без слэша в конце")
            
            self.print_success("Формат URL корректен")
            
        except Exception as e:
            self.print_error(f"Ошибка парсинга URL: {e}")
            return False
        
        # Проверяем доступность сайта
        self.print_info("Проверка доступности сайта...")
        try:
            response = requests.get(redirect_uri, timeout=5, allow_redirects=True)
            self.print_success(f"Сайт доступен (статус: {response.status_code})")
        except requests.exceptions.ConnectionError:
            self.print_warning("Сайт недоступен (ошибка соединения)")
            self.print_info("Убедитесь, что сайт работает и доступен из интернета")
        except requests.exceptions.Timeout:
            self.print_warning("Таймаут при подключении к сайту")
        except Exception as e:
            self.print_warning(f"Ошибка проверки доступности: {e}")
        
        return True
    
    def check_auth_url(self, client_id, redirect_uri):
        """Проверка URL авторизации"""
        self.print_header("5. ПРОВЕРКА URL АВТОРИЗАЦИИ")
        
        from urllib.parse import urlencode
        
        # Варианты URL для проверки
        auth_params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code"
        }
        
        # Вариант 1: Без лишних параметров
        url1 = f"https://avito.ru/oauth?{urlencode(auth_params)}"
        
        # Вариант 2: С pro_users_flow
        auth_params2 = auth_params.copy()
        auth_params2["pro_users_flow"] = "true"
        url2 = f"https://avito.ru/oauth?{urlencode(auth_params2)}"
        
        self.print_info("Вариант 1 (без pro_users_flow):")
        print(f"  {url1}")
        
        self.print_info("Вариант 2 (с pro_users_flow):")
        print(f"  {url2}")
        
        self.print_info("\nПроверка доступности Avito OAuth...")
        
        # Проверяем доступность страницы авторизации
        try:
            response = requests.head(url1, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                self.print_success("Avito OAuth доступен")
            elif response.status_code == 302:
                self.print_success("Avito OAuth перенаправляет (это нормально)")
            else:
                self.print_warning(f"Неожиданный статус: {response.status_code}")
        except Exception as e:
            self.print_warning(f"Не удалось проверить доступность: {e}")
        
        return url1, url2
    
    def check_avito_profile(self):
        """Проверка номера профиля"""
        self.print_header("6. ПРОВЕРКА ПРОФИЛЯ AVITO")
        
        self.print_info("Номер профиля из скриншота: 177 185 850")
        self.print_info("Это ваш User ID - он нужен для работы с API")
        
        # Проверяем, сохранен ли user_id в БД
        if Path("avito_commander.db").exists():
            self.print_success("База данных существует")
            
            # Проверяем через SQLite
            try:
                import sqlite3
                conn = sqlite3.connect("avito_commander.db")
                cursor = conn.cursor()
                cursor.execute("SELECT username, user_id_avito FROM users WHERE is_active=1")
                users = cursor.fetchall()
                conn.close()
                
                if users:
                    self.print_success(f"Найдено {len(users)} активных пользователей:")
                    for username, user_id in users:
                        print(f"  - {username}: {user_id}")
                else:
                    self.print_warning("Нет активных пользователей в БД")
            except Exception as e:
                self.print_warning(f"Не удалось проверить БД: {e}")
        else:
            self.print_warning("База данных не создана")
    
    def generate_report(self):
        """Генерация итогового отчета"""
        self.print_header("📊 ИТОГОВЫЙ ОТЧЕТ")
        
        print(f"✅ Успешно: {len(self.success)}")
        print(f"⚠️ Предупреждений: {len(self.warnings)}")
        print(f"❌ Ошибок: {len(self.errors)}")
        
        print("\n" + self.BOLD + "Рекомендации:" + self.RESET)
        
        if self.errors:
            print(f"{self.RED}1. Исправьте ошибки:{self.RESET}")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        
        if self.warnings:
            print(f"{self.YELLOW}2. Обратите внимание на предупреждения:{self.RESET}")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        if not self.errors and not self.warnings:
            print(f"{self.GREEN}✅ Все проверки пройдены успешно!{self.RESET}")
            print(f"{self.GREEN}Вы можете запускать приложение: python main.py{self.RESET}")
        else:
            print(f"\n{self.YELLOW}После исправления ошибок перезапустите скрипт проверки.{self.RESET}")
    
    def run(self):
        """Запуск всех проверок"""
        print(self.BOLD + """
    ╔═══════════════════════════════════════════════════════════╗
    ║         🔍 ПРОВЕРКА НАСТРОЕК АВТОРИЗАЦИИ AVITO         ║
    ╚═══════════════════════════════════════════════════════════╝
    """ + self.RESET)
        
        # Шаг 1: Проверка .env
        env_values = self.check_env_file()
        if not env_values:
            self.generate_report()
            return
        
        client_id = env_values.get("AVITO_CLIENT_ID")
        client_secret = env_values.get("AVITO_CLIENT_SECRET")
        redirect_uri = env_values.get("AVITO_REDIRECT_URI")
        
        # Шаг 2: Проверка Client ID
        self.check_client_id(client_id)
        
        # Шаг 3: Проверка Client Secret
        self.check_client_secret(client_secret)
        
        # Шаг 4: Проверка Redirect URI
        self.check_redirect_uri(redirect_uri)
        
        # Шаг 5: Проверка URL авторизации
        url1, url2 = self.check_auth_url(client_id, redirect_uri)
        
        # Шаг 6: Проверка профиля
        self.check_avito_profile()
        
        # Итоговый отчет
        self.generate_report()
        
        # Вывод готовых URL для авторизации
        if not self.errors:
            print("\n" + self.BOLD + "📋 ГОТОВЫЕ ССЫЛКИ ДЛЯ АВТОРИЗАЦИИ:" + self.RESET)
            print(f"\n{self.BLUE}Вариант 1 (простой):{self.RESET}")
            print(f"  {url1}")
            print(f"\n{self.BLUE}Вариант 2 (с pro_users_flow):{self.RESET}")
            print(f"  {url2}")


def main():
    """Главная функция"""
    checker = AvitoAuthChecker()
    checker.run()


if __name__ == "__main__":
    main()