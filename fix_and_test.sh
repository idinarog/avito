#!/usr/bin/env bash

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     🔧 ИСПРАВЛЕНИЕ ФАЙЛОВ И ЗАПУСК ТЕСТА              ║"
echo "║     Avito Commander — Авто-исправление                ║"
echo "╚═══════════════════════════════════════════════════════════╝"

# Переходим в корень проекта
cd "$(dirname "$0")"

echo ""
echo "📁 1. Удаление проблемных файлов..."
rm -f ui/main_window.py
rm -f ui/__init__.py
rm -f ui/widgets/__init__.py
rm -f ui/widgets/filter_panel.py
rm -f ui/widgets/project_panel.py
rm -f ui/widgets/items_panel.py
rm -f ui/widgets/modern_status_bar.py
echo "✅ Проблемные файлы удалены"

echo ""
echo "📁 2. Создание файлов заново..."

# Создаем ui/__init__.py
cat > ui/__init__.py << 'EOF'
"""
Модуль пользовательского интерфейса
"""
from .main_window import MainWindow
from .login_dialog import LoginDialog

__all__ = ['MainWindow', 'LoginDialog']
EOF
echo "  ✅ ui/__init__.py"

# Создаем ui/widgets/__init__.py
cat > ui/widgets/__init__.py << 'EOF'
"""
Виджеты интерфейса
"""
from .project_panel import ProjectPanel
from .items_panel import ItemsPanel
from .filter_panel import FilterPanel
from .modern_status_bar import ModernStatusBar

__all__ = ['ProjectPanel', 'ItemsPanel', 'FilterPanel', 'ModernStatusBar']
EOF
echo "  ✅ ui/widgets/__init__.py"

# Создаем ui/widgets/filter_panel.py
cat > ui/widgets/filter_panel.py << 'EOF'
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
EOF
echo "  ✅ ui/widgets/filter_panel.py"

# Создаем ui/widgets/project_panel.py
cat > ui/widgets/project_panel.py << 'EOF'
"""
Панель проектов (левая панель)
Отображает список проектов пользователя
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from core.app import Application


class ProjectPanel(QWidget):
    """Панель с проектами пользователя"""

    project_selected = pyqtSignal(object)

    def __init__(self, app: Application):
        super().__init__()
        self.app = app
        self.current_project_id = None

        self.setup_ui()
        self.load_projects()

    def setup_ui(self):
        """Создание интерфейса панели"""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("📂 ПРОЕКТЫ")
        title.setObjectName("panel-title")
        title.setStyleSheet("""
            QLabel {
                color: #7a8ba8;
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
                padding: 10px 12px;
                background-color: #0d1520;
                border-bottom: 1px solid #1a2a3a;
            }
        """)
        layout.addWidget(title)

        self.projects_list = QListWidget()
        self.projects_list.setStyleSheet("""
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
        """)
        self.projects_list.itemClicked.connect(self.on_project_clicked)
        layout.addWidget(self.projects_list)

        self.stats_frame = QFrame()
        self.stats_frame.setStyleSheet("""
            QFrame {
                background-color: #0d1520;
                border-top: 1px solid #1a2a3a;
                padding: 8px 12px;
            }
            QLabel {
                color: #5a7a9a;
                font-size: 11px;
            }
            QLabel.value {
                color: #8aabca;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(4)
        stats_layout.setContentsMargins(8, 8, 8, 8)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("📊 Всего:"))
        self.total_label = QLabel("0")
        self.total_label.setObjectName("value")
        row1.addWidget(self.total_label)
        row1.addStretch()
        row1.addWidget(QLabel("✅ Активных:"))
        self.active_label = QLabel("0")
        self.active_label.setObjectName("value")
        row1.addWidget(self.active_label)
        stats_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("⏸️ Неактивных:"))
        self.inactive_label = QLabel("0")
        self.inactive_label.setObjectName("value")
        row2.addWidget(self.inactive_label)
        row2.addStretch()
        row2.addWidget(QLabel("🚫 Блок:"))
        self.blocked_label = QLabel("0")
        self.blocked_label.setObjectName("value")
        row2.addWidget(self.blocked_label)
        stats_layout.addLayout(row2)

        self.stats_frame.setLayout(stats_layout)
        layout.addWidget(self.stats_frame)

        self.setLayout(layout)

    def load_projects(self):
        self.projects_list.clear()
        user = self.app.get_current_user()
        if not user:
            return

        projects = self.app.project_repo.get_by_user(user.id)
        for project in projects:
            item = QListWidgetItem(f"📁 {project.name}")
            item.setData(Qt.UserRole, project.id)
            self.projects_list.addItem(item)

        if self.projects_list.count() > 0:
            self.projects_list.setCurrentRow(0)
            self.on_project_clicked(self.projects_list.currentItem())

    def on_project_clicked(self, item):
        if not item:
            return

        project_id = item.data(Qt.UserRole)
        self.current_project_id = project_id

        user = self.app.get_current_user()
        projects = self.app.project_repo.get_by_user(user.id)
        for project in projects:
            if project.id == project_id:
                self.app.set_current_project(project)
                break

        self.update_stats(project_id)
        self.project_selected.emit(project_id)

    def update_stats(self, project_id: int):
        items = self.app.item_repo.get_by_project(project_id)
        total = len(items)
        active = sum(1 for i in items if i.status == 'active')
        inactive = sum(1 for i in items if i.status == 'inactive')
        blocked = sum(1 for i in items if i.status == 'blocked')

        self.total_label.setText(str(total))
        self.active_label.setText(str(active))
        self.inactive_label.setText(str(inactive))
        self.blocked_label.setText(str(blocked))

    def refresh(self):
        self.load_projects()
        if self.current_project_id:
            self.update_stats(self.current_project_id)

    def get_selected_project(self):
        return self.current_project_id
EOF
echo "  ✅ ui/widgets/project_panel.py"

# Создаем ui/widgets/items_panel.py
cat > ui/widgets/items_panel.py << 'EOF'
"""
Панель объявлений (правая панель)
Отображает список объявлений с метриками
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from core.app import Application
from core.metrics_calculator import MetricsCalculator


class ItemsPanel(QWidget):
    """Панель с объявлениями и метриками"""

    item_double_clicked = pyqtSignal(object)

    def __init__(self, app: Application):
        super().__init__()
        self.app = app
        self.current_project_id = None
        self.current_item = None

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Создание интерфейса панели"""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("📄 ОБЪЯВЛЕНИЯ")
        title.setObjectName("panel-title")
        title.setStyleSheet("""
            QLabel {
                color: #7a8ba8;
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
                padding: 10px 12px;
                background-color: #0d1520;
                border-bottom: 1px solid #1a2a3a;
            }
        """)
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Название", "Цена", "Статус",
            "👁️", "📞", "💬", "⭐", "Метрики"
        ])

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setShowGrid(False)

        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(1, 250)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 50)
        self.table.setColumnWidth(5, 50)
        self.table.setColumnWidth(6, 50)
        self.table.setColumnWidth(7, 50)
        self.table.setColumnWidth(8, 150)

        self.table.setStyleSheet("""
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
                color: #5a7a9a;
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
        """)

        self.table.itemDoubleClicked.connect(self.on_item_double_click)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def connect_signals(self):
        self.app.event_bus.items_updated.connect(self.load_items)

    def load_items(self, project_id: int = None):
        if project_id is not None:
            self.current_project_id = project_id

        if not self.current_project_id:
            return

        self.table.setRowCount(0)
        items = self.app.item_repo.get_by_project(self.current_project_id)

        for item in items:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(item.item_id_avito)))
            self.table.setItem(row, 1, QTableWidgetItem(item.title or "Без названия"))

            price_text = f"{item.price:,} ₽" if item.price else "0 ₽"
            self.table.setItem(row, 2, QTableWidgetItem(price_text))

            status_item = QTableWidgetItem(item.status or "unknown")
            if item.status == "active":
                status_item.setForeground(QColor(0, 200, 0))
            elif item.status == "inactive":
                status_item.setForeground(QColor(200, 200, 0))
            elif item.status == "blocked":
                status_item.setForeground(QColor(200, 0, 0))
            self.table.setItem(row, 3, status_item)

            self.table.setItem(row, 4, QTableWidgetItem(str(item.views or 0)))
            self.table.setItem(row, 5, QTableWidgetItem(str(item.calls or 0)))
            self.table.setItem(row, 6, QTableWidgetItem(str(getattr(item, 'messages', 0) or 0)))
            self.table.setItem(row, 7, QTableWidgetItem(str(item.favorites or 0)))

            metrics = MetricsCalculator.calculate_for_ad(item)
            metrics_text = f"CTR: {metrics['ctr']}%"
            self.table.setItem(row, 8, QTableWidgetItem(metrics_text))

    def on_item_double_click(self, item):
        row = item.row()
        item_id = self.table.item(row, 0).text()
        items = self.app.item_repo.get_by_project(self.current_project_id)
        for it in items:
            if str(it.item_id_avito) == item_id:
                self.current_item = it
                self.item_double_clicked.emit(it)
                break

    def on_selection_changed(self):
        pass

    def get_selected_items(self):
        selected_items = []
        rows = set()
        for item in self.table.selectedItems():
            rows.add(item.row())

        for row in rows:
            item_id = self.table.item(row, 0).text()
            items = self.app.item_repo.get_by_project(self.current_project_id)
            for it in items:
                if str(it.item_id_avito) == item_id:
                    selected_items.append(it)
                    break

        return selected_items

    def refresh(self):
        self.load_items(self.current_project_id)
EOF
echo "  ✅ ui/widgets/items_panel.py"

# Создаем ui/widgets/modern_status_bar.py
cat > ui/widgets/modern_status_bar.py << 'EOF'
"""
Современный статус-бар
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class ModernStatusBar(QStatusBar):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
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
            QStatusBar QLabel.highlight {
                color: #8aabca;
            }
        """)

        self.left_label = QLabel("💻 Готов к работе")
        self.addWidget(self.left_label)

        self.addPermanentWidget(QLabel("|"))

        self.sync_label = QLabel("🔄 Синхронизация: не выполнена")
        self.sync_label.setObjectName("highlight")
        self.addPermanentWidget(self.sync_label)

        self.addPermanentWidget(QLabel("|"))

        self.auth_label = QLabel("✅ Авторизован")
        self.auth_label.setObjectName("highlight")
        self.addPermanentWidget(self.auth_label)

    def set_message(self, message: str):
        self.left_label.setText(message)

    def set_sync_status(self, status: str):
        self.sync_label.setText(f"🔄 {status}")

    def set_auth_status(self, status: str):
        self.auth_label.setText(status)
EOF
echo "  ✅ ui/widgets/modern_status_bar.py"

# Создаем ui/main_window.py
cat > ui/main_window.py << 'EOF'
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
    def __init__(self, app: Application):
        super().__init__()
        self.app = app

        self.setWindowTitle("Avito Commander 1.0")
        self.setGeometry(50, 50, 1600, 900)
        self.setMinimumSize(1200, 700)

        self.apply_styles()
        self.setup_ui()
        self.connect_signals()
        self.load_initial_data()

    def apply_styles(self):
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
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(8, 8, 8, 8)
        central.setLayout(main_layout)

        self.create_header(main_layout)

        self.filter_panel = FilterPanel()
        self.filter_panel.filter_applied.connect(self.apply_filters)
        main_layout.addWidget(self.filter_panel)

        panels_layout = QHBoxLayout()
        panels_layout.setSpacing(8)

        self.project_panel = ProjectPanel(self.app)
        self.project_panel.project_selected.connect(self.on_project_selected)
        panels_layout.addWidget(self.project_panel, 3)

        self.items_panel = ItemsPanel(self.app)
        self.items_panel.item_double_clicked.connect(self.on_item_double_click)
        panels_layout.addWidget(self.items_panel, 7)

        main_layout.addLayout(panels_layout, 1)

        self.status_bar = ModernStatusBar()
        self.setStatusBar(self.status_bar)

        self.app.event_bus.sync_started.connect(
            lambda: self.status_bar.set_sync_status("Синхронизация...")
        )
        self.app.event_bus.sync_finished.connect(
            lambda count: self.status_bar.set_sync_status(f"Синхронизировано: {count}")
        )

    def create_header(self, parent_layout):
        header = QHBoxLayout()
        header.setSpacing(20)

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

        user = self.app.get_current_user()
        if user:
            user_label = QLabel(f"👤 {user.username}")
            user_label.setStyleSheet("color: #5a7a9a; font-size: 13px;")
            header.addWidget(user_label)

        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: #5a7a9a; font-size: 13px; font-family: monospace;")
        header.addWidget(self.time_label)

        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        self.update_time()

        parent_layout.addLayout(header)

    def connect_signals(self):
        self.app.event_bus.items_updated.connect(self.refresh)
        self.app.event_bus.project_changed.connect(self.refresh)

    def load_initial_data(self):
        self.refresh()

    def refresh(self):
        self.project_panel.refresh()
        self.items_panel.refresh()

    def on_project_selected(self, project_id):
        self.items_panel.load_items(project_id)
        self.filter_panel.set_count(self.items_panel.table.rowCount())

    def on_item_double_click(self, item):
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
        self.status_bar.set_message("🔍 Фильтры применены")

    def update_time(self):
        from datetime import datetime
        self.time_label.setText(datetime.now().strftime("%H:%M:%S"))
EOF
echo "  ✅ ui/main_window.py"

echo ""
echo "📁 3. Проверка созданных файлов..."
ls -la ui/
ls -la ui/widgets/

echo ""
echo "📁 4. Запуск теста..."
python3 test_app.py

echo ""
echo "✅ Готово!"
