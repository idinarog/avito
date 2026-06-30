"""
Панель фильтров
Фильтрация объявлений по дате, статусу и цене
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class FilterPanel(QWidget):
    """Панель фильтров над таблицей"""

    filter_applied = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Создание интерфейса панели"""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(8, 6, 8, 6)

        # Стиль для всех элементов
        label_style = "color: #a8b8c8; font-size: 12px;"
        input_style = """
            QComboBox, QDateEdit, QLineEdit {
                background-color: #0d1520;
                color: #e8eef4;
                border: 1px solid #1a2a3a;
                border-radius: 4px;
                padding: 4px 8px;
                min-height: 24px;
            }
            QComboBox:hover, QDateEdit:hover, QLineEdit:hover {
                border-color: #4a8aba;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #5a7a9a;
                margin-right: 4px;
            }
            QComboBox QAbstractItemView {
                background-color: #0d1520;
                color: #e8eef4;
                selection-background-color: #1a3a5a;
            }
            QDateEdit::drop-down {
                border: none;
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #5a7a9a;
                margin-right: 4px;
            }
            QLineEdit::placeholder {
                color: #5a7a9a;
            }
        """

        # Фильтр по статусу
        status_label = QLabel("Статус:")
        status_label.setStyleSheet(label_style)
        layout.addWidget(status_label)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["Все", "active", "inactive", "blocked"])
        self.status_filter.setFixedWidth(100)
        self.status_filter.setStyleSheet(input_style)
        layout.addWidget(self.status_filter)

        # Разделитель
        sep = QLabel("|")
        sep.setStyleSheet("color: #1a2a3a;")
        layout.addWidget(sep)

        # Фильтр по дате
        date_label1 = QLabel("📅 С:")
        date_label1.setStyleSheet(label_style)
        layout.addWidget(date_label1)

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setFixedWidth(100)
        self.date_from.setStyleSheet(input_style)
        layout.addWidget(self.date_from)

        date_label2 = QLabel("ПО:")
        date_label2.setStyleSheet(label_style)
        layout.addWidget(date_label2)

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setFixedWidth(100)
        self.date_to.setStyleSheet(input_style)
        layout.addWidget(self.date_to)

        # Разделитель
        sep2 = QLabel("|")
        sep2.setStyleSheet("color: #1a2a3a;")
        layout.addWidget(sep2)

        # Фильтр по цене
        price_label = QLabel("Цена:")
        price_label.setStyleSheet(label_style)
        layout.addWidget(price_label)

        self.price_min = QLineEdit()
        self.price_min.setPlaceholderText("от")
        self.price_min.setFixedWidth(60)
        self.price_min.setStyleSheet(input_style)
        layout.addWidget(self.price_min)

        self.price_max = QLineEdit()
        self.price_max.setPlaceholderText("до")
        self.price_max.setFixedWidth(60)
        self.price_max.setStyleSheet(input_style)
        layout.addWidget(self.price_max)

        # Кнопки
        self.apply_btn = QPushButton("🔘 Применить")
        self.apply_btn.clicked.connect(self.apply_filter)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a3a5a;
                color: #c8d0dc;
                border: 1px solid #2a4a6a;
                border-radius: 4px;
                padding: 4px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2a4a6a;
                color: #ffffff;
                border-color: #4a8aba;
            }
        """)
        layout.addWidget(self.apply_btn)

        self.reset_btn = QPushButton("🔄 Сбросить")
        self.reset_btn.clicked.connect(self.reset_filter)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #7a8ba8;
                border: 1px solid #1a2a3a;
                border-radius: 4px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #1a2a3a;
                color: #c8d0dc;
                border-color: #2a3a4a;
            }
        """)
        layout.addWidget(self.reset_btn)

        layout.addStretch()

        # Информация о количестве
        self.count_label = QLabel("Всего: 0")
        self.count_label.setStyleSheet("color: #5a7a9a; font-size: 12px;")
        layout.addWidget(self.count_label)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #111927; border-radius: 4px;")

    def apply_filter(self):
        """Применение фильтров"""
        filters = {
            'status': self.status_filter.currentText(),
            'date_from': self.date_from.date().toString("yyyy-MM-dd"),
            'date_to': self.date_to.date().toString("yyyy-MM-dd"),
            'price_min': self.price_min.text().strip(),
            'price_max': self.price_max.text().strip(),
        }
        self.filter_applied.emit(filters)

    def reset_filter(self):
        """Сброс фильтров"""
        self.status_filter.setCurrentIndex(0)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_to.setDate(QDate.currentDate())
        self.price_min.clear()
        self.price_max.clear()
        self.apply_filter()

    def set_count(self, count: int):
        """Установка количества объявлений"""
        self.count_label.setText(f"Всего: {count}")
