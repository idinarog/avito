"""
Модуль стартового экрана
Содержит главное меню и процесс авторизации
"""

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# Импортируем модули для работы с API и главным окном
from avito_api import AvitoAuth, AvitoAPI
from main_app import MainApp


class AuthDialog(QDialog):
    """
    Диалоговое окно для авторизации в Avito
    Пользователь вводит свои данные вручную
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Авторизация в Avito")
        self.setFixedSize(500, 380)
        self.setModal(True)  # Блокирует основное окно пока открыт диалог
        
        # Создаем элементы интерфейса
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Заголовок
        title = QLabel("🔑 Авторизация в Avito API")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Описание
        desc = QLabel(
            "Введите данные для доступа к Avito API.\n"
            "Вы можете получить их в кабинете разработчика Avito."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Поле для client_id
        layout.addWidget(QLabel("Client ID:"))
        self.client_id_input = QLineEdit()
        self.client_id_input.setPlaceholderText("Введите ваш Client ID")
        layout.addWidget(self.client_id_input)
        
        # Поле для client_secret
        layout.addWidget(QLabel("Client Secret:"))
        self.client_secret_input = QLineEdit()
        self.client_secret_input.setPlaceholderText("Введите ваш Client Secret")
        self.client_secret_input.setEchoMode(QLineEdit.Password)  # Скрываем ввод
        layout.addWidget(self.client_secret_input)
        
        # Поле для user_id
        layout.addWidget(QLabel("User ID (ваш ID в Avito):"))
        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("Введите ваш user_id (например: 123456789)")
        layout.addWidget(self.user_id_input)
        
        # Подсказка где взять user_id
        hint = QLabel("💡 User ID можно найти в URL вашего профиля на Avito")
        hint.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(hint)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        self.auth_btn = QPushButton("✅ Авторизоваться")
        self.auth_btn.clicked.connect(self.accept)
        self.auth_btn.setFixedHeight(40)
        self.auth_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        
        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setFixedHeight(40)
        
        button_layout.addWidget(self.auth_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Загружаем сохраненные данные, если есть
        self.load_saved_data()
    
    def load_saved_data(self):
        """Загружает сохраненные данные из файлов"""
        # Пытаемся загрузить из .env файла
        try:
            if os.path.exists(".env"):
                with open(".env", "r") as f:
                    for line in f:
                        if "=" in line:
                            key, value = line.strip().split("=", 1)
                            if key == "AVITO_CLIENT_ID":
                                self.client_id_input.setText(value)
                            elif key == "AVITO_CLIENT_SECRET":
                                self.client_secret_input.setText(value)
                            elif key == "AVITO_USER_ID":
                                self.user_id_input.setText(value)
        except:
            pass
        
        # Или из отдельных файлов
        try:
            if os.path.exists("client_id.txt"):
                with open("client_id.txt", "r") as f:
                    self.client_id_input.setText(f.read().strip())
        except:
            pass
            
        try:
            if os.path.exists("client_secret.txt"):
                with open("client_secret.txt", "r") as f:
                    self.client_secret_input.setText(f.read().strip())
        except:
            pass
            
        try:
            if os.path.exists("user_id.txt"):
                with open("user_id.txt", "r") as f:
                    self.user_id_input.setText(f.read().strip())
        except:
            pass
    
    def get_data(self):
        """Возвращает введенные данные"""
        return {
            "client_id": self.client_id_input.text().strip(),
            "client_secret": self.client_secret_input.text().strip(),
            "user_id": self.user_id_input.text().strip()
        }
    
    def save_data(self):
        """Сохраняет данные в файлы"""
        data = self.get_data()
        
        # Сохраняем в .env
        try:
            with open(".env", "w") as f:
                f.write(f"AVITO_CLIENT_ID={data['client_id']}\n")
                f.write(f"AVITO_CLIENT_SECRET={data['client_secret']}\n")
                f.write(f"AVITO_USER_ID={data['user_id']}\n")
        except:
            pass
        
        # Сохраняем отдельные файлы
        try:
            with open("client_id.txt", "w") as f:
                f.write(data["client_id"])
        except:
            pass
            
        try:
            with open("client_secret.txt", "w") as f:
                f.write(data["client_secret"])
        except:
            pass
            
        try:
            with open("user_id.txt", "w") as f:
                f.write(data["user_id"])
        except:
            pass


class StartScreen(QWidget):
    """
    Стартовый экран с меню и авторизацией
    """
    
    def __init__(self):
        super().__init__()
        
        # Настройки окна
        self.setWindowTitle("Avito Commander")
        self.setFixedSize(1200, 700)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()
        
        # Пытаемся загрузить фоновое изображение
        self.bg = None
        try:
            self.bg = QPixmap("assets/splash.png")
        except:
            print("Фоновое изображение не найдено")
        
        # Данные авторизации
        self.client_id = None
        self.client_secret = None
        self.user_id = None
        self.auth = None
        self.api = None
        
        # Загружаем сохраненные данные
        self.load_config()
        
        # Пункты меню
        self.menu_index = 0
        self.menu_items = [
            "1. ПРОДОЛЖИТЬ",
            "2. ОТКРЫТЬ ПРОЕКТ",
            "3. СОЗДАТЬ ПРОЕКТ",
            "4. НАСТРОЙКИ",
            "5. ВЫХОД"
        ]
        
        # Текущее время
        self.time = QTime.currentTime().toString("HH:mm:ss")
        
        # Таймер для обновления времени
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
    
    def load_config(self):
        """Загружает конфигурацию из файлов"""
        try:
            if os.path.exists(".env"):
                with open(".env", "r") as f:
                    for line in f:
                        if "=" in line:
                            key, value = line.strip().split("=", 1)
                            if key == "AVITO_CLIENT_ID":
                                self.client_id = value
                            elif key == "AVITO_CLIENT_SECRET":
                                self.client_secret = value
                            elif key == "AVITO_USER_ID":
                                self.user_id = value
        except:
            pass
        
        # Если .env не найден, пробуем отдельные файлы
        if not self.client_id:
            try:
                if os.path.exists("client_id.txt"):
                    with open("client_id.txt", "r") as f:
                        self.client_id = f.read().strip()
            except:
                pass
                
        if not self.client_secret:
            try:
                if os.path.exists("client_secret.txt"):
                    with open("client_secret.txt", "r") as f:
                        self.client_secret = f.read().strip()
            except:
                pass
                
        if not self.user_id:
            try:
                if os.path.exists("user_id.txt"):
                    with open("user_id.txt", "r") as f:
                        self.user_id = f.read().strip()
            except:
                pass
    
    def update_time(self):
        """Обновляет время каждую секунду"""
        self.time = QTime.currentTime().toString("HH:mm:ss")
        self.update()
    
    def paintEvent(self, event):
        """Отрисовка интерфейса"""
        painter = QPainter(self)
        
        # Фон - если есть изображение, используем его
        if self.bg and not self.bg.isNull():
            painter.drawPixmap(self.rect(), self.bg)
        else:
            # Если нет изображения - заливаем темным фоном
            painter.fillRect(self.rect(), QColor(30, 30, 40))
        
        # =========================
        # ДВОЙНАЯ РАМКА ВОКРУГ ВСЕГО
        # =========================
        pen_outer = QPen(QColor(200, 210, 230))
        pen_outer.setWidth(2)
        painter.setPen(pen_outer)
        painter.drawRect(8, 8, self.width() - 16, self.height() - 16)
        
        pen_inner = QPen(QColor(200, 210, 230))
        pen_inner.setWidth(1)
        painter.setPen(pen_inner)
        painter.drawRect(14, 14, self.width() - 28, self.height() - 28)
        
        # =========================
        # ВЕРХНИЙ ТЕКСТ
        # =========================
        painter.setPen(QColor(200, 210, 230))
        painter.setFont(QFont("Courier New", 10))
        painter.drawText(30, 40, "AVITO COMMANDER 0.1")
        painter.drawText(self.width() - 360, 40, "РАЗРАБОТАНО: СТАНИСЛАВ КУЗНЕЦОВ 2026")
        
        # =========================
        # РАМКА ПОД ЗАГОЛОВОК
        # =========================
        painter.setPen(QPen(QColor(200, 210, 230), 2))
        painter.drawRect(650, 120, 420, 180)
        
        painter.setPen(QPen(QColor(200, 210, 230), 1))
        painter.drawRect(660, 130, 400, 160)
        
        # =========================
        # ЗАГОЛОВОК
        # =========================
        painter.setFont(QFont("Courier New", 28, QFont.Weight.Bold))
        
        # Рассчитываем ширину текста для центрирования
        text_avito = "АВИТО"
        text_komander = "КОММАНДЕР"
        
        avito_width = painter.fontMetrics().horizontalAdvance(text_avito)
        komander_width = painter.fontMetrics().horizontalAdvance(text_komander)
        
        center_x = 860
        painter.drawText(center_x - avito_width // 2, 190, text_avito)
        painter.drawText(center_x - komander_width // 2, 250, text_komander)
        
        # =========================
        # ВЕРСИЯ
        # =========================
        painter.setFont(QFont("Courier New", 10))
        v_text = "v0.1"
        v_width = painter.fontMetrics().horizontalAdvance(v_text)
        painter.drawText(center_x - v_width // 2, 320, v_text)
        
        # =========================
        # РАМКА МЕНЮ
        # =========================
        painter.setPen(QPen(QColor(200, 210, 230), 2))
        painter.drawRect(700, 350, 360, 230)
        
        painter.setPen(QPen(QColor(200, 210, 230), 1))
        painter.drawRect(710, 360, 340, 210)
        
        # =========================
        # МЕНЮ
        # =========================
        painter.setFont(QFont("Courier New", 14))
        start_y = 390
        
        for i, item in enumerate(self.menu_items):
            y = start_y + i * 36
            
            if i == self.menu_index:
                painter.fillRect(720, y - 18, 320, 30, QColor(200, 200, 200))
                painter.setPen(QColor(20, 20, 20))
                painter.drawText(740, y, f"> {item}")
                painter.setPen(QColor(200, 210, 230))
            else:
                painter.drawText(740, y, item)
        
        # =========================
        # НИЖНЯЯ ПАНЕЛЬ
        # =========================
        painter.setPen(QPen(QColor(200, 210, 230), 2))
        painter.drawLine(10, self.height() - 60, self.width() - 10, self.height() - 60)
        
        painter.setPen(QPen(QColor(200, 210, 230), 1))
        painter.drawLine(10, self.height() - 55, self.width() - 10, self.height() - 55)
        
        painter.setFont(QFont("Courier New", 10))
        painter.drawText(20, self.height() - 25, "F1 — ПОМОЩЬ")
        
        # Проверяем статус авторизации
        if self.client_id and self.client_secret and self.user_id:
            status = "✅ Авторизован"
        else:
            status = "❌ Требуется авторизация"
        painter.drawText(300, self.height() - 25, status)
        
        welcome = "ДОБРО ПОЖАЛОВАТЬ В АВИТО КОММАНДЕР"
        welcome_width = painter.fontMetrics().horizontalAdvance(welcome)
        painter.drawText((self.width() - welcome_width) // 2, self.height() - 25, welcome)
        
        time_width = painter.fontMetrics().horizontalAdvance(self.time)
        painter.drawText(self.width() - time_width - 20, self.height() - 25, self.time)
    
    def keyPressEvent(self, event):
        """Обработка нажатий клавиш"""
        if event.key() == Qt.Key.Key_Up:
            self.menu_index = (self.menu_index - 1) % len(self.menu_items)
            self.update()
        elif event.key() == Qt.Key.Key_Down:
            self.menu_index = (self.menu_index + 1) % len(self.menu_items)
            self.update()
        elif event.key() == Qt.Key.Key_Return:
            self.activate_menu()
        elif event.key() == Qt.Key.Key_F1:
            self.show_help()
    
    def activate_menu(self):
        """Выполнение действий при выборе пункта меню"""
        choice = self.menu_index
        
        if choice == 0:  # ПРОДОЛЖИТЬ
            self.continue_app()
        elif choice == 1:  # ОТКРЫТЬ ПРОЕКТ
            self.open_project()
        elif choice == 2:  # СОЗДАТЬ ПРОЕКТ
            self.create_project()
        elif choice == 3:  # НАСТРОЙКИ
            self.show_settings()
        elif choice == 4:  # ВЫХОД
            self.quit_app()
    
    def show_auth_dialog(self):
        """Показывает диалог авторизации с кнопками Да/Нет"""
        # Создаем кастомный диалог
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Авторизация")
        msg_box.setText("Для работы требуется авторизация в Avito.\nХотите ввести данные для авторизации?")
        msg_box.setIcon(QMessageBox.Question)
        
        # Создаем кнопки с русскими названиями
        yes_button = QPushButton("Да")
        no_button = QPushButton("Нет")
        
        msg_box.addButton(yes_button, QMessageBox.YesRole)
        msg_box.addButton(no_button, QMessageBox.NoRole)
        
        # Показываем диалог и получаем ответ
        msg_box.exec_()
        
        # Определяем, какая кнопка была нажата
        clicked_button = msg_box.clickedButton()
        return clicked_button == yes_button
    
    def continue_app(self):
        """Запуск основного интерфейса"""
        print("Запуск основного интерфейса...")
        
        # Проверяем, есть ли данные авторизации
        if not self.client_id or not self.client_secret or not self.user_id:
            # Показываем диалог с кнопками Да/Нет
            if not self.show_auth_dialog():
                return
            
            # Открываем диалог авторизации
            auth_dialog = AuthDialog(self)
            if auth_dialog.exec_() == QDialog.Accepted:
                data = auth_dialog.get_data()
                
                # Проверяем, что все поля заполнены
                if not data["client_id"] or not data["client_secret"] or not data["user_id"]:
                    QMessageBox.warning(
                        self,
                        "Ошибка",
                        "Все поля должны быть заполнены!",
                        QMessageBox.Ok
                    )
                    return
                
                # Сохраняем данные
                self.client_id = data["client_id"]
                self.client_secret = data["client_secret"]
                self.user_id = data["user_id"]
                auth_dialog.save_data()
                
                QMessageBox.information(
                    self,
                    "Успех",
                    "Данные сохранены!",
                    QMessageBox.Ok
                )
            else:
                return
        
        # Если есть данные, но нет объекта авторизации - создаем его
        if not self.auth:
            # Создаем объект авторизации
            self.auth = AvitoAuth(self.client_id, self.client_secret, "http://localhost:8080")
            # Временно создаем заглушку для токена
            self.auth.access_token = "temp_token_for_testing"
        
        # Создаем API клиент
        self.api = AvitoAPI(self.auth)
        
        # Открываем главное окно
        self.main_app = MainApp(self.auth)
        self.main_app.show()
        self.close()
    
    def open_project(self):
        """Открыть существующий проект"""
        print("Открыть проект")
        QMessageBox.information(
            self,
            "Открыть проект",
            "Функция открытия проекта в разработке.",
            QMessageBox.Ok
        )
    
    def create_project(self):
        """Создать новый проект"""
        print("Создать проект")
        QMessageBox.information(
            self,
            "Создать проект",
            "Функция создания проекта в разработке.",
            QMessageBox.Ok
        )
    
    def show_settings(self):
        """Показать настройки"""
        print("Настройки")
        
        # Открываем диалог с текущими настройками
        auth_dialog = AuthDialog(self)
        if auth_dialog.exec_() == QDialog.Accepted:
            data = auth_dialog.get_data()
            if data["client_id"] and data["client_secret"] and data["user_id"]:
                self.client_id = data["client_id"]
                self.client_secret = data["client_secret"]
                self.user_id = data["user_id"]
                auth_dialog.save_data()
                self.update()
                QMessageBox.information(
                    self,
                    "Успех",
                    "Настройки сохранены!",
                    QMessageBox.Ok
                )
    
    def quit_app(self):
        """Выход из приложения"""
        print("Выход из приложения...")
        QApplication.quit()
    
    def show_help(self):
        """Показать справку"""
        QMessageBox.information(
            self,
            "Помощь",
            "Avito Commander v0.1\n\n"
            "Управление:\n"
            "↑/↓ - Навигация по меню\n"
            "Enter - Выбор пункта\n"
            "F1 - Эта справка\n\n"
            "Для работы требуется авторизация в Avito.\n"
            "Нажмите 'ПРОДОЛЖИТЬ' для ввода данных.",
            QMessageBox.Ok
        )


# Запуск для тестирования
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StartScreen()
    window.show()
    sys.exit(app.exec_())