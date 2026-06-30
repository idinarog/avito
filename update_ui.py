from pathlib import Path

main_app_code = r'''
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QFrame, QPushButton,
    QListWidget, QListWidgetItem, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Avito Commander 1.0")
        self.setMinimumSize(1400, 900)

        self.setStyleSheet(self.get_styles())

        root = QVBoxLayout(self)
        root.setSpacing(10)

        root.addWidget(self.top_bar())

        center = QHBoxLayout()
        center.addWidget(self.left_panel(), 2)
        center.addWidget(self.right_panel(), 8)

        root.addLayout(center)
        root.addWidget(self.bottom_bar())

    # =========================
    # 🔷 TOP BAR
    # =========================
    def top_bar(self):
        bar = QFrame()
        layout = QHBoxLayout(bar)

        title = QLabel("📁 Avito Commander 1.0")

        search = QLineEdit()
        search.setPlaceholderText("🔍 Поиск...")

        sync_btn = QPushButton("🔄 Синхронизация")
        import_btn = QPushButton("⬇ Импорт")
        export_btn = QPushButton("⬆ Экспорт")

        layout.addWidget(title)
        layout.addWidget(search)
        layout.addStretch()
        layout.addWidget(sync_btn)
        layout.addWidget(import_btn)
        layout.addWidget(export_btn)

        return bar

    # =========================
    # 📂 LEFT PANEL
    # =========================
    def left_panel(self):
        panel = QFrame()
        layout = QVBoxLayout(panel)

        layout.addWidget(QLabel("📂 ПРОЕКТЫ"))

        self.project_list = QListWidget()

        for name, count in [
            ("Основной проект", 18),
            ("Авто", 4),
            ("Недвижимость", 7),
            ("Электроника", 12)
        ]:
            item = QListWidgetItem(f"{name}   {count}")
            self.project_list.addItem(item)

        layout.addWidget(self.project_list)

        stats = QLabel(
            "Всего: 24\n"
            "Активных: 18\n"
            "Неактивных: 4\n"
            "Заблокированных: 2"
        )

        layout.addWidget(stats)

        return panel

    # =========================
    # 📄 RIGHT PANEL
    # =========================
    def right_panel(self):
        panel = QFrame()
        layout = QVBoxLayout(panel)

        layout.addWidget(QLabel("📄 ОБЪЯВЛЕНИЯ"))

        self.table = QTableWidget(4, 11)
        self.table.setHorizontalHeaderLabels([
            "ID", "Название", "Цена", "Статус",
            "Просмотры", "Лиды", "Звонки",
            "Сообщения", "CTR", "CPL", "CPM"
        ])

        data = [
            ["1", "MacBook Pro", "1500 ₽", "Active", "10", "5", "2", "3", "2.3%", "250", "150"],
            ["2", "iPhone 15", "850 ₽", "Active", "5", "1", "0", "1", "1.2%", "170", "170"],
            ["3", "Квартира", "5000 ₽", "Inactive", "20", "10", "3", "4", "3.4%", "1000", "250"],
            ["4", "Дизайнер", "2000 ₽", "Blocked", "0", "0", "0", "0", "-", "-", "-"],
        ]

        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

        layout.addWidget(self.table)

        layout.addWidget(self.metrics_panel())

        return panel

    # =========================
    # 📊 METRICS PANEL
    # =========================
    def metrics_panel(self):
        frame = QFrame()
        layout = QHBoxLayout(frame)

        def block(title, value):
            b = QVBoxLayout()
            b.addWidget(QLabel(title))
            val = QLabel(value)
            val.setStyleSheet("font-size: 18px; color: #4a8aba;")
            b.addWidget(val)
            return b

        layout.addLayout(block("Просмотры", "10"))
        layout.addLayout(block("Лиды", "5"))
        layout.addLayout(block("Звонки", "2"))
        layout.addLayout(block("Сообщения", "3"))
        layout.addLayout(block("CTR", "2.3%"))

        return frame

    # =========================
    # ⬇️ BOTTOM BAR
    # =========================
    def bottom_bar(self):
        bar = QFrame()
        layout = QHBoxLayout(bar)

        layout.addWidget(QLabel("[F1] Помощь"))
        layout.addWidget(QLabel("[F3] Просмотр"))
        layout.addWidget(QLabel("[F4] Правка"))
        layout.addWidget(QLabel("[F7] Создать"))
        layout.addWidget(QLabel("[F8] Удалить"))
        layout.addStretch()
        layout.addWidget(QLabel("[F10] Выход"))

        return bar

    # =========================
    # 🎨 STYLES
    # =========================
    def get_styles(self):
        return """
        QWidget {
            background-color: #0a0e17;
            color: #cfd8e3;
            font-family: Arial;
        }

        QFrame {
            background-color: #111927;
            border: 1px solid #1a2a3a;
            border-radius: 6px;
        }

        QTableWidget {
            background-color: #0f1624;
            gridline-color: #1a2a3a;
        }

        QPushButton {
            background-color: #1a2a3a;
            padding: 6px;
            border-radius: 4px;
        }

        QPushButton:hover {
            background-color: #4a8aba;
        }

        QLineEdit {
            background-color: #0f1624;
            border: 1px solid #1a2a3a;
            padding: 6px;
        }
        """
'''

Path("main_app.py").write_text(main_app_code, encoding="utf-8")

print("✅ UI обновлён под финальный макет")