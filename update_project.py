import os

files = {
    "main.py": """import sys
from PyQt5.QtWidgets import QApplication
from start_screen import StartScreen

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = StartScreen()
    window.show()

    sys.exit(app.exec_())
""",

    "start_screen.py": """from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPixmap, QPen, QColor, QFont
from PyQt5.QtCore import Qt, QTimer, QTime


class StartScreen(QWidget):
    def __init__(self):
        super().__init__()

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
        self.main = MainApp()
        self.main.show()
        self.close()
""",

    "main_app.py": """from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QPushButton
)


class MainApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Avito Commander")
        self.setGeometry(100, 100, 1200, 700)

        self.setStyleSheet(\"\"\"
            QWidget {
                background-color: #0a0e17;
                color: #c8d2e6;
                font-family: Courier New;
            }
            QTableWidget {
                background-color: #111927;
                gridline-color: #1a2a3a;
            }
            QListWidget {
                background-color: #111927;
            }
        \"\"\")

        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()

        header = QHBoxLayout()

        header.addWidget(QLabel("📁 Avito Commander 1.0"))
        header.addStretch()

        search = QLineEdit()
        search.setPlaceholderText("🔍 Поиск...")
        header.addWidget(search)

        header.addStretch()
        header.addWidget(QLabel("22:45:30"))

        # LEFT
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("📂 ПРОЕКТЫ"))

        project_list = QListWidget()
        project_list.addItems([
            "📁 Основной проект",
            "📁 Авто",
            "📁 Недвижимость"
        ])

        left_panel.addWidget(project_list)
        left_panel.addWidget(QLabel("Всего: 24"))

        # RIGHT
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("📄 ОБЪЯВЛЕНИЯ"))

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("С:"))
        filter_layout.addWidget(QLineEdit("01.06.2026"))
        filter_layout.addWidget(QLabel("По:"))
        filter_layout.addWidget(QLineEdit("30.06.2026"))
        filter_layout.addWidget(QPushButton("Применить"))

        table = QTableWidget()
        table.setColumnCount(10)
        table.setHorizontalHeaderLabels([
            "ID", "Название", "Цена",
            "Статус", "👁", "📞", "💬",
            "Лиды", "CTR", "Цена лида"
        ])

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        data = [
            ["1", "MacBook", "1500", "Активно", "10", "2", "1", "3", "30%", "500"]
        ]

        table.setRowCount(len(data))

        for r, row in enumerate(data):
            for c, val in enumerate(row):
                table.setItem(r, c, QTableWidgetItem(val))

        right_panel.addLayout(filter_layout)
        right_panel.addWidget(table)

        top_layout.addLayout(left_panel, 1)
        top_layout.addLayout(right_panel, 3)

        bottom = QHBoxLayout()
        bottom.addWidget(QLabel("💻 Выбрано: 1"))
        bottom.addStretch()
        bottom.addWidget(QLabel("🔄 Синхронизация"))
        bottom.addStretch()
        bottom.addWidget(QLabel("✅ Авторизован"))

        main_layout.addLayout(header)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom)

        self.setLayout(main_layout)
"""
}

for filename, content in files.items():
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

print("✅ Файлы успешно обновлены!")
