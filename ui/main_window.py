"""
Главное окно приложения в стиле коммандера
Две панели: проекты + объявления
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from core.app import Application
from ui.widgets.project_panel import ProjectPanel
from ui.widgets.items_panel import ItemsPanel
from ui.widgets.filter_panel import FilterPanel
from ui.widgets.modern_status_bar import ModernStatusBar
from core.metrics_calculator import MetricsCalculator


class MainWindow(QMainWindow):
    """Главное окно с двумя панелями"""

    def __init__(self, app: Application):
        super().__init__()
        self.app = app

        self.setWindowTitle("Avito Commander 1.0")
        self.setGeometry(50, 50, 1600, 900)
        self.setMinimumSize(1200, 700)

        # Применяем стили
        self.apply_styles()

        # Создаем интерфейс
        self.setup_ui()

        # Подключаем сигналы
        self.connect_signals()

        # Загружаем данные
        self.load_initial_data()

    def apply_styles(self):
        """Применение QSS стилей"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0e17;
            }

            QFrame {
                background-color: #111927;
                border: 1px solid #1a2a3a;
                border-radius: 8px;
            }

            QPushButton {
                background-color: #1a2a3a;
                color: #c8d0dc;
                border: 1px solid #2a3a4a;
                border-radius: 4px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2a4a6a;
                border-color: #4a8aba;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #0d2030;
            }
            QPushButton.accent {
                background-color: #4a6a8a;
                border-color: #6a8aaa;
                color: #ffffff;
            }
            QPushButton.accent:hover {
                background-color: #5a8aaa;
                border-color: #8aaaca;
            }
            QPushButton.danger {
                background-color: #6a2a2a;
                border-color: #8a3a3a;
                color: #ffffff;
            }
            QPushButton.danger:hover {
                background-color: #8a3a3a;
                border-color: #aa4a4a;
            }
            QPushButton.export-btn {
                background-color: #2a5a3a;
                border-color: #3a7a4a;
                color: #ffffff;
            }
            QPushButton.export-btn:hover {
                background-color: #3a7a4a;
                border-color: #5a9a6a;
            }

            QLineEdit {
                background-color: #0d1520;
                color: #e8eef4;
                border: 1px solid #1a2a3a;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #4a8aba;
            }
            QLineEdit::placeholder {
                color: #5a7a9a;
            }

            QComboBox {
                background-color: #0d1520;
                color: #e8eef4;
                border: 1px solid #1a2a3a;
                border-radius: 4px;
                padding: 4px 8px;
                min-height: 24px;
            }
            QComboBox:hover {
                border-color: #4a8aba;
            }
            QComboBox::drop-down {
                border: none;
                background-color: transparent;
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
                border: 1px solid #1a2a3a;
            }
            QComboBox QAbstractItemView::item {
                padding: 4px 8px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #1a2a3a;
            }

            QLabel {
                color: #a8b8c8;
            }

            QTableWidget {
                background-color: #0d1520;
                border: none;
                color: #c8d0dc;
                font-size: 12px;
                gridline-color: #1a2a3a;
                outline: none;
            }
            QTableWidget::item {
                padding: 6px 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #1a3a5a;
                color: #ffffff;
            }
            QTableWidget::item:hover {
                background-color: #1a2a3a;
            }
            QHeaderView::section {
                background-color: #0d1520;
                color: #7a8ba8;
                padding: 6px 8px;
                border: none;
                border-bottom: 1px solid #1a2a3a;
                font-size: 11px;
                font-weight: bold;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #0d1520;
                border: none;
            }

            QStatusBar {
                background-color: #0d1520;
                color: #5a7a9a;
                font-size: 11px;
                padding: 4px 10px;
                border-top: 1px solid #1a2a3a;
            }
            QStatusBar QLabel {
                color: #5a7a9a;
            }

            QDateEdit {
                background-color: #0d1520;
                color: #e8eef4;
                border: 1px solid #1a2a3a;
                border-radius: 4px;
                padding: 4px 8px;
                min-height: 24px;
            }
            QDateEdit:hover {
                border-color: #4a8aba;
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
            QCalendarWidget {
                background-color: #0d1520;
                color: #e8eef4;
            }
            QCalendarWidget QWidget {
                background-color: #0d1520;
                color: #e8eef4;
            }
            QCalendarWidget QToolButton {
                color: #e8eef4;
                background-color: transparent;
            }
            QCalendarWidget QMenu {
                background-color: #0d1520;
                color: #e8eef4;
            }
            QCalendarWidget QSpinBox {
                background-color: #0d1520;
                color: #e8eef4;
            }

            QListWidget {
                background-color: #0d1520;
                border: none;
                color: #c8d0dc;
                font-size: 13px;
                padding: 4px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 4px;
                margin: 1px 0;
            }
            QListWidget::item:selected {
                background-color: #1a3a5a;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #1a2a3a;
            }

            QScrollBar:vertical {
                background-color: #0d1520;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #2a4a6a;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #3a6a8a;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }

            QScrollBar:horizontal {
                background-color: #0d1520;
                height: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal {
                background-color: #2a4a6a;
                border-radius: 4px;
                min-width: 30px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #3a6a8a;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0;
            }
        """)

    def setup_ui(self):
        """Создание интерфейса с двумя панелями"""
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(8, 8, 8, 8)
        central.setLayout(main_layout)

        # Верхняя панель с заголовком и кнопками
        self.create_header(main_layout)

        # Панель фильтров
        self.filter_panel = FilterPanel()
        self.filter_panel.filter_applied.connect(self.apply_filters)
        main_layout.addWidget(self.filter_panel)

        # Основные панели (две колонки)
        panels_layout = QHBoxLayout()
        panels_layout.setSpacing(8)

        # Левая панель - Проекты (30%)
        self.project_panel = ProjectPanel(self.app)
        self.project_panel.project_selected.connect(self.on_project_selected)
        panels_layout.addWidget(self.project_panel, 3)

        # Правая панель - Объявления (70%)
        self.items_panel = ItemsPanel(self.app)
        self.items_panel.item_double_clicked.connect(self.on_item_double_click)
        panels_layout.addWidget(self.items_panel, 7)

        main_layout.addLayout(panels_layout, 1)

        # Статус-бар
        self.status_bar = ModernStatusBar()
        self.setStatusBar(self.status_bar)

        # Подключаем статус-бар к событиям
        self.app.event_bus.sync_started.connect(
            lambda: self.status_bar.set_sync_status("Синхронизация...")
        )
        self.app.event_bus.sync_finished.connect(
            lambda count: self.status_bar.set_sync_status(f"Синхронизировано: {count}")
        )

    def create_header(self, parent_layout):
        """Создание верхней панели"""
        header = QHBoxLayout()
        header.setSpacing(20)

        # Логотип
        logo = QLabel("📁 Avito Commander 1.0")
        logo.setStyleSheet("""
            color: #8aabca;
            font-size: 16px;
            font-weight: bold;
            letter-spacing: 0.5px;
            padding: 6px 12px;
        """)
        header.addWidget(logo)

        header.addStretch()

        # Информация о пользователе
        user = self.app.get_current_user()
        if user:
            user_label = QLabel(f"👤 {user.username}")
            user_label.setStyleSheet("color: #5a7a9a; font-size: 13px;")
            header.addWidget(user_label)

        # Время
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: #5a7a9a; font-size: 13px; font-family: monospace;")
        header.addWidget(self.time_label)

        # Таймер для времени
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        self.update_time()

        # Кнопка "Экспорт XML"
        self.export_btn = QPushButton("📤 Экспорт XML")
        self.export_btn.setProperty("class", "export-btn")
        self.export_btn.clicked.connect(self.export_xml_feed)
        self.export_btn.setFixedHeight(30)
        header.addWidget(self.export_btn)

        parent_layout.addLayout(header)

    def connect_signals(self):
        """Подключение сигналов"""
        self.app.event_bus.items_updated.connect(self.refresh)
        self.app.event_bus.project_changed.connect(self.refresh)

    def load_initial_data(self):
        """Загрузка начальных данных"""
        self.refresh()

    def refresh(self):
        """Обновление всех панелей"""
        self.project_panel.refresh()
        self.items_panel.refresh()

    def on_project_selected(self, project_id):
        """Обработчик выбора проекта"""
        self.items_panel.load_items(project_id)
        self.filter_panel.set_count(self.items_panel.table.rowCount())

    def on_item_double_click(self, item):
        """Обработчик двойного клика по объявлению"""
        QMessageBox.information(
            self,
            "Объявление",
            f"📄 {item.title}\n\n"
            f"💰 Цена: {item.price:,} ₽\n"
            f"📌 Статус: {item.status}\n"
            f"👁️ Просмотры: {item.views}\n"
            f"📞 Звонки: {item.calls}\n"
            f"💬 Сообщения: {getattr(item, 'messages', 0)}\n"
            f"⭐ Избранные: {item.favorites}"
        )

    def apply_filters(self, filters):
        """Применение фильтров"""
        # TODO: Реализовать фильтрацию на уровне ItemsPanel
        self.status_bar.set_message("🔍 Фильтры применены")

    def export_xml_feed(self):
        """Запускает скрипт публикации XML-фида"""
        import subprocess
        import sys
        from pathlib import Path

        script_path = Path(__file__).parent.parent / "avito_publish.py"

        if not script_path.exists():
            QMessageBox.critical(self, "Ошибка", "Скрипт avito_publish.py не найден!")
            return

        reply = QMessageBox.question(
            self,
            "Экспорт XML",
            "Будет сгенерирован и опубликован XML-фид.\n"
            "Продолжить?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.status_bar.set_message("⏳ Генерация и публикация XML...")
            try:
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.status_bar.set_message("✅ XML-фид успешно опубликован!")
                    QMessageBox.information(
                        self,
                        "Успех",
                        "XML-фид опубликован и доступен по ссылке:\n"
                        "https://raw.githubusercontent.com/idinarog/avitoxml/main/avito_feed.xml"
                    )
                else:
                    self.status_bar.set_message("❌ Ошибка публикации XML")
                    QMessageBox.critical(
                        self,
                        "Ошибка",
                        f"Ошибка выполнения:\n{result.stderr}"
                    )
            except Exception as e:
                self.status_bar.set_message("❌ Ошибка")
                QMessageBox.critical(self, "Ошибка", str(e))

    def update_time(self):
        """Обновление времени"""
        from datetime import datetime
        self.time_label.setText(datetime.now().strftime("%H:%M:%S"))
