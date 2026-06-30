from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout
from core.session import Session
from ui.login_dialog import LoginDialog
from PyQt5.QtGui import QPainter, QPixmap, QPen, QColor, QFont
from PyQt5.QtCore import Qt, QTimer, QTime


class StartScreen(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.setWindowTitle("Avito Commander")
        self.setFixedSize(1200, 700)

        self.bg = QPixmap("assets/splash.png")

        self.menu_index = 0
        self.menu_items = [
            "ПРОДОЛЖИТЬ",
            "ОТКРЫТЬ ПРОЕКТ",
            "СОЗДАТЬ ПРОЕКТ",
            "НАСТРОЙКИ",
            "ВЫХОД"
        ]

        self.time = QTime.currentTime().toString("HH:mm:ss")

        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)

    def update_time(self):
        self.time = QTime.currentTime().toString("HH:mm:ss")
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.bg)

        painter.setPen(QPen(QColor(200, 210, 230), 2))
        painter.drawRect(10, 10, self.width() - 20, self.height() - 20)

        painter.setFont(QFont("Courier New", 28, QFont.Bold))
        painter.setPen(QColor(200, 210, 230))

        painter.drawText(700, 200, "АВИТО")
        painter.drawText(700, 260, "КОММАНДЕР")

        painter.setFont(QFont("Courier New", 10))
        painter.drawText(780, 300, "v0.1")

        painter.setFont(QFont("Courier New", 14))

        for i, item in enumerate(self.menu_items):
            y = 400 + i * 35

            if i == self.menu_index:
                painter.fillRect(700, y - 20, 300, 30, QColor(200, 200, 200))
                painter.setPen(QColor(0, 0, 0))
                painter.drawText(720, y, f"> {item}")
                painter.setPen(QColor(200, 210, 230))
            else:
                painter.drawText(720, y, item)

        painter.drawText(20, self.height() - 20, "F1 — ПОМОЩЬ")
        painter.drawText(self.width() - 120, self.height() - 20, self.time)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.menu_index = (self.menu_index - 1) % len(self.menu_items)
            self.update()

        elif event.key() == Qt.Key_Down:
            self.menu_index = (self.menu_index + 1) % len(self.menu_items)
            self.update()

        elif event.key() == Qt.Key_Return:
            self.handle_enter()

    def handle_enter(self):
        if self.menu_index == 0:
            self.open_main_app()
        elif self.menu_index == 4:
            self.close()

    def open_main_app(self):
        from main_app import MainApp
        # 🔐 Проверка авторизации
        if not Session.access_token:
            dialog = LoginDialog(self.app)
            dialog.exec_()

            if not Session.access_token:
                print("❌ Авторизация не выполнена")
                return

        self.main = MainApp(self.app)
        self.main.show()
        self.close()
