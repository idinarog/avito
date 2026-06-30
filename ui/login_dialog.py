"""
Диалог входа в приложение
Поддерживает OAuth авторизацию через Avito
"""

import os
import webbrowser
from datetime import datetime, timedelta
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from core.app import Application
from core.session import Session  # <-- добавлено


class LoginDialog(QDialog):
    """Диалог для входа пользователя с OAuth авторизацией"""

    def __init__(self, app: Application, parent=None):
        super().__init__(parent)
        self.app = app
        self.user = None
        self.auth_code = None

        self.setWindowTitle("Вход в Avito Commander")
        self.setMinimumSize(500, 600)
        self.resize(500, 600)
        self.setModal(True)

        self.init_ui()
        self.load_saved_users()

    def init_ui(self):
        """Создание интерфейса"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # Заголовок
        title = QLabel("🔑 Avito Commander")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Подзаголовок
        subtitle = QLabel("Войдите в свой аккаунт")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666;")
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # Поле для имени пользователя
        layout.addWidget(QLabel("Имя пользователя:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите имя пользователя...")
        layout.addWidget(self.username_input)

        # Поле для User ID Avito
        layout.addWidget(QLabel("Ваш ID на Avito:"))
        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("Например: 123456789")
        self.user_id_input.setToolTip("ID можно найти в URL вашего профиля на Avito")
        layout.addWidget(self.user_id_input)

        # Комбобокс с сохраненными пользователями
        layout.addWidget(QLabel("Или выберите существующего:"))
        self.users_combo = QComboBox()
        self.users_combo.addItem("-- Выберите пользователя --")
        self.users_combo.currentIndexChanged.connect(self.on_user_selected)
        layout.addWidget(self.users_combo)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Кнопка OAuth авторизации
        self.auth_btn = QPushButton("🌐 Авторизоваться через Avito")
        self.auth_btn.clicked.connect(self.auth_via_avito)
        self.auth_btn.setFixedHeight(45)
        self.auth_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A651;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #008845;
            }
        """)
        layout.addWidget(self.auth_btn)

        # Информация о шагах авторизации
        steps_label = QLabel(
            "1. Нажмите кнопку → откроется браузер\n"
            "2. Войдите в Avito и разрешите доступ\n"
            "3. Скопируйте код из URL (после code=)\n"
            "4. Вставьте код в поле ниже"
        )
        steps_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(steps_label)

        # Поле для кода авторизации
        layout.addWidget(QLabel("Код авторизации:"))
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Вставьте код из URL после авторизации...")
        self.code_input.setToolTip("Код выглядит как: abc123def456")
        layout.addWidget(self.code_input)

        # Статус
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #FF6B6B; font-weight: bold;")
        layout.addWidget(self.status_label)

        # Кнопки
        btn_layout = QHBoxLayout()

        self.login_btn = QPushButton("✅ Войти")
        self.login_btn.clicked.connect(self.login)
        self.login_btn.setFixedHeight(45)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setFixedHeight(45)

        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_saved_users(self):
        """Загружает сохраненных пользователей"""
        try:
            users = self.app.user_repo.get_all_active()
            for user in users:
                self.users_combo.addItem(
                    f"{user.username} (ID: {user.user_id_avito})",
                    user.id
                )
        except Exception as e:
            print(f"⚠️ Ошибка загрузки пользователей: {e}")

    def on_user_selected(self, index):
        """Обработчик выбора пользователя из списка"""
        if index > 0:
            user_id = self.users_combo.currentData()
            user = self.app.user_repo.get_by_id(user_id)
            if user:
                self.username_input.setText(user.username)
                self.user_id_input.setText(user.user_id_avito)
                self.status_label.setText("")
                self.status_label.setStyleSheet("color: #00A651;")
                self.status_label.setText("✅ Пользователь выбран")

    def auth_via_avito(self):
        """Открывает браузер для OAuth авторизации через Avito"""
        try:
            client_id = os.getenv("avito_client_id")
            redirect_uri = os.getenv("avito_redirect_uri")

            if not client_id:
                self.status_label.setText("❌ Client ID не найден в .env файле")
                self.status_label.setStyleSheet("color: #FF6B6B;")
                return

            if not redirect_uri:
                redirect_uri = "https://sk-consulting.group/"

            from urllib.parse import urlencode

            auth_params = {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": "items:info,stats:read,user:read",
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
                "1. Войдите в свой аккаунт Avito в открывшемся окне\n"
                "2. Разрешите доступ приложению Avito Commander\n"
                "3. После авторизации в URL будет параметр code=XXXXXXXX\n"
                "4. Скопируйте этот код и вставьте в поле ниже\n"
                "5. Нажмите 'Войти'\n\n"
                "⚠️ Важно: у вас должен быть подключен платный тариф Avito!",
                QMessageBox.Ok
            )

        except Exception as e:
            self.status_label.setText(f"❌ Ошибка: {str(e)}")
            self.status_label.setStyleSheet("color: #FF6B6B;")
            print(f"❌ Ошибка авторизации: {e}")

    def get_access_token(self, code: str):
        """Обменивает код авторизации на токен доступа"""
        try:
            import requests

            client_id = os.getenv("avito_client_id")
            client_secret = os.getenv("avito_client_secret")
            redirect_uri = os.getenv("avito_redirect_uri")

            if not client_id or not client_secret:
                self.status_label.setText("❌ Client ID или Secret не найдены в .env")
                self.status_label.setStyleSheet("color: #FF6B6B;")
                return None

            if not redirect_uri:
                redirect_uri = "https://sk-consulting.group/"

            data = {
                "grant_type": "authorization_code",
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "code": code
            }

            print("🔄 Обмен кода на токен...")

            response = requests.post(
                "https://api.avito.ru/token",
                data=data,
                timeout=30
            )

            if response.status_code == 200:
                tokens = response.json()
                access_token = tokens.get("access_token")
                refresh_token = tokens.get("refresh_token")

                print("✅ Токен получен успешно")
                return access_token, refresh_token
            else:
                error_msg = f"Ошибка {response.status_code}: {response.text}"
                print(f"❌ {error_msg}")
                self.status_label.setText(f"❌ {error_msg[:50]}...")
                self.status_label.setStyleSheet("color: #FF6B6B;")
                return None

        except requests.exceptions.Timeout:
            self.status_label.setText("❌ Таймаут подключения к Avito")
            self.status_label.setStyleSheet("color: #FF6B6B;")
            return None
        except Exception as e:
            self.status_label.setText(f"❌ Ошибка: {str(e)[:50]}...")
            self.status_label.setStyleSheet("color: #FF6B6B;")
            print(f"❌ Ошибка получения токена: {e}")
            return None

    def login(self):
        """Обработчик входа с автоматическим использованием сохранённого токена"""
        username = self.username_input.text().strip()
        user_id_avito = self.user_id_input.text().strip()
        auth_code = self.code_input.text().strip()

        if not username:
            self.status_label.setText("❌ Введите имя пользователя")
            self.status_label.setStyleSheet("color: #FF6B6B;")
            return

        if not user_id_avito:
            self.status_label.setText("❌ Введите ваш ID на Avito")
            self.status_label.setStyleSheet("color: #FF6B6B;")
            return

        # Попытка найти пользователя в БД
        user = self.app.user_repo.get_by_username(username)
        if user and user.user_id_avito != user_id_avito:
            user.user_id_avito = user_id_avito
            self.app.user_repo.update(user)
        elif not user:
            user_id = self.app.user_repo.create(username, user_id_avito)
            if user_id:
                user = self.app.user_repo.get_by_id(user_id)
            else:
                self.status_label.setText("❌ Ошибка создания пользователя")
                self.status_label.setStyleSheet("color: #FF6B6B;")
                return

        if not user:
            self.status_label.setText("❌ Ошибка загрузки пользователя")
            self.status_label.setStyleSheet("color: #FF6B6B;")
            return

        # Проверяем, есть ли у пользователя действующий токен
        if user.access_token and user.token_expires_at and user.token_expires_at > datetime.now():
            # Токен валиден – входим сразу
            self.user = user
            self.status_label.setText("✅ Автоматический вход по токену")
            self.status_label.setStyleSheet("color: #00A651;")

            # Устанавливаем токен в API клиент
            self.app.avito_api.set_access_token(user.access_token)
            Session.access_token = user.access_token  # <-- добавляем
            self.accept()
            return

        # Если токена нет или он истёк – требуется код авторизации
        if not auth_code:
            self.status_label.setText("❌ Введите код авторизации для получения нового токена")
            self.status_label.setStyleSheet("color: #FF6B6B;")
            return

        # Обмен кода на токен
        self.status_label.setText("🔄 Получение токена доступа...")
        self.status_label.setStyleSheet("color: #FFA500;")
        QApplication.processEvents()

        tokens = self.get_access_token(auth_code)
        if tokens:
            access_token, refresh_token = tokens
            user.access_token = access_token
            user.refresh_token = refresh_token
            user.token_expires_at = datetime.now() + timedelta(hours=24)
            self.app.user_repo.update(user)

            # Устанавливаем токен в API клиент
            self.app.avito_api.set_access_token(access_token)
            Session.access_token = access_token  # <-- добавляем

            self.user = user
            self.status_label.setText("✅ Токен получен! Вход выполнен.")
            self.status_label.setStyleSheet("color: #00A651;")
            self.accept()
        else:
            self.status_label.setText("❌ Не удалось получить токен. Проверьте код.")
            self.status_label.setStyleSheet("color: #FF6B6B;")

    def get_user(self):
        """Возвращает текущего пользователя"""
        return self.user