#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для применения изменений Этапа 4:
- Создание панели проектов (ProjectPanel)
- Создание панели объявлений (ItemsPanel) 
- Создание панели фильтров (FilterPanel)
- Создание современного статус-бара (ModernStatusBar)
- Обновление главного окна (MainWindow) с двумя панелями
- Добавление QSS стилей для темной темы
"""

import os
import sys
import shutil
from pathlib import Path


class Phase4Updater:
    """Класс для применения изменений Этапа 4"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors = []
        self.steps = []
        
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
        self.steps.append(f"✅ {text}")
    
    def print_error(self, text):
        print(f"{self.RED}❌ {text}{self.RESET}")
        self.errors.append(f"❌ {text}")
    
    def print_info(self, text):
        print(f"{self.BLUE}ℹ️ {text}{self.RESET}")
    
    def print_warning(self, text):
        print(f"{self.YELLOW}⚠️ {text}{self.RESET}")
    
    def create_widgets_folder(self):
        """Создание папки для виджетов"""
        widgets_dir = self.project_root / "ui" / "widgets"
        widgets_dir.mkdir(parents=True, exist_ok=True)
        self.print_success(f"Создана папка {widgets_dir}")
        return True
    
    def create_project_panel(self) -> bool:
        """Создание ui/widgets/project_panel.py"""
        self.print_header("1. СОЗДАНИЕ PROJECT_PANEL.PY")
        
        file_path = self.project_root / "ui" / "widgets" / "project_panel.py"
        
        content = '''"""
Панель проектов (левая панель)
Отображает список проектов пользователя
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from core.app import Application


class ProjectPanel(QWidget):
    """Панель с проектами пользователя"""
    
    project_selected = pyqtSignal(object)  # Сигнал при выборе проекта
    
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
        
        # Заголовок
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
        
        # Список проектов
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
        
        # Статистика проекта (внизу)
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
        
        # Ряды статистики
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
        """Загрузка проектов пользователя"""
        self.projects_list.clear()
        
        user = self.app.get_current_user()
        if not user:
            return
        
        projects = self.app.project_repo.get_by_user(user['id'])
        
        for project in projects:
            item = QListWidgetItem(f"📁 {project.name}")
            item.setData(Qt.UserRole, project.id)
            self.projects_list.addItem(item)
        
        if self.projects_list.count() > 0:
            self.projects_list.setCurrentRow(0)
            self.on_project_clicked(self.projects_list.currentItem())
    
    def on_project_clicked(self, item):
        """Обработчик клика по проекту"""
        if not item:
            return
        
        project_id = item.data(Qt.UserRole)
        self.current_project_id = project_id
        
        # Получаем проект из БД
        user = self.app.get_current_user()
        projects = self.app.project_repo.get_by_user(user['id'])
        
        for project in projects:
            if project.id == project_id:
                self.app.set_current_project(project)
                break
        
        # Обновляем статистику
        self.update_stats(project_id)
        
        # Отправляем сигнал
        self.project_selected.emit(project_id)
    
    def update_stats(self, project_id: int):
        """Обновление статистики проекта"""
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
        """Обновление панели"""
        self.load_projects()
        if self.current_project_id:
            self.update_stats(self.current_project_id)
    
    def get_selected_project(self):
        """Возвращает ID выбранного проекта"""
        return self.current_project_id
'''
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.print_success(f"Создан {file_path}")
            return True
        except Exception as e:
            self.print_error(f"Ошибка создания файла: {e}")
            return False
    
    def create_items_panel(self) -> bool:
        """Создание ui/widgets/items_panel.py"""
        self.print_header("2. СОЗДАНИЕ ITEMS_PANEL.PY")
        
        file_path = self.project_root / "ui" / "widgets" / "items_panel.py"
        
        content = '''"""
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
    
    item_double_clicked = pyqtSignal(object)  # Сигнал при двойном клике
    
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
        
        # Заголовок
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
        
        # Таблица объявлений
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
        
        # Настройка ширины колонок
        self.table.setColumnWidth(0, 80)   # ID
        self.table.setColumnWidth(1, 250)  # Название
        self.table.setColumnWidth(2, 100)  # Цена
        self.table.setColumnWidth(3, 100)  # Статус
        self.table.setColumnWidth(4, 50)   # Просмотры
        self.table.setColumnWidth(5, 50)   # Звонки
        self.table.setColumnWidth(6, 50)   # Сообщения
        self.table.setColumnWidth(7, 50)   # Избранные
        self.table.setColumnWidth(8, 150)  # Метрики
        
        # Стиль таблицы
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
        """Подключение сигналов"""
        self.app.event_bus.items_updated.connect(self.load_items)
    
    def load_items(self, project_id: int = None):
        """Загрузка объявлений в таблицу"""
        if project_id is not None:
            self.current_project_id = project_id
        
        if not self.current_project_id:
            return
        
        self.table.setRowCount(0)
        
        items = self.app.item_repo.get_by_project(self.current_project_id)
        
        for item in items:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(item.item_id_avito)))
            
            # Название
            self.table.setItem(row, 1, QTableWidgetItem(item.title or "Без названия"))
            
            # Цена
            price_text = f"{item.price:,} ₽" if item.price else "0 ₽"
            self.table.setItem(row, 2, QTableWidgetItem(price_text))
            
            # Статус с цветом
            status_item = QTableWidgetItem(item.status or "unknown")
            if item.status == "active":
                status_item.setForeground(QColor(0, 200, 0))
            elif item.status == "inactive":
                status_item.setForeground(QColor(200, 200, 0))
            elif item.status == "blocked":
                status_item.setForeground(QColor(200, 0, 0))
            self.table.setItem(row, 3, status_item)
            
            # Статистика
            self.table.setItem(row, 4, QTableWidgetItem(str(item.views or 0)))
            self.table.setItem(row, 5, QTableWidgetItem(str(item.calls or 0)))
            self.table.setItem(row, 6, QTableWidgetItem(str(getattr(item, 'messages', 0) or 0)))
            self.table.setItem(row, 7, QTableWidgetItem(str(item.favorites or 0)))
            
            # Метрики (кратко)
            metrics = MetricsCalculator.calculate_for_ad(item)
            metrics_text = f"CTR: {metrics['ctr']}%"
            self.table.setItem(row, 8, QTableWidgetItem(metrics_text))
        
        self.update_status(len(items))
    
    def update_status(self, count: int):
        """Обновление статуса"""
        # Статус будет обновляться через главное окно
        pass
    
    def on_item_double_click(self, item):
        """Обработчик двойного клика по объявлению"""
        row = item.row()
        item_id = self.table.item(row, 0).text()
        
        # Находим объявление в БД
        items = self.app.item_repo.get_by_project(self.current_project_id)
        for it in items:
            if str(it.item_id_avito) == item_id:
                self.current_item = it
                self.item_double_clicked.emit(it)
                break
    
    def on_selection_changed(self):
        """Обработчик изменения выделения"""
        selected = len(self.table.selectedItems())
        if selected > 0:
            selected = selected // self.table.columnCount()
            # Отправляем сигнал о количестве выбранных
            self.parent().selection_label.setText(f"Выбрано: {selected}") if hasattr(self.parent(), 'selection_label') else None
    
    def get_selected_items(self):
        """Возвращает список выбранных объявлений"""
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
        """Обновление панели"""
        self.load_items(self.current_project_id)
'''
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.print_success(f"Создан {file_path}")
            return True
        except Exception as e:
            self.print_error(f"Ошибка создания файла: {e}")
            return False
    
    def create_filter_panel(self) -> bool:
        """Создание ui/widgets/filter_panel.py"""
        self.print_header("3. СОЗДАНИЕ FILTER_PANEL.PY")
        
        file_path = self.project_root / "ui" / "widgets" / "filter_panel.py"
        
        content = '''"""
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
        
        # Фильтр по статусу
        layout.addWidget(QLabel("Статус:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Все", "active", "inactive", "blocked"])
        self.status_filter.setFixedWidth(100)
        layout.addWidget(self.status_filter)
        
        # Разделитель
        layout.addWidget(QLabel("|"))
        
        # Фильтр по дате
        layout.addWidget(QLabel("📅 С:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setFixedWidth(100)
        layout.addWidget(self.date_from)
        
        layout.addWidget(QLabel("ПО:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setFixedWidth(100)
        layout.addWidget(self.date_to)
        
        # Разделитель
        layout.addWidget(QLabel("|"))
        
        # Фильтр по цене
        layout.addWidget(QLabel("Цена:"))
        self.price_min = QLineEdit()
        self.price_min.setPlaceholderText("от")
        self.price_min.setFixedWidth(60)
        layout.addWidget(self.price_min)
        
        self.price_max = QLineEdit()
        self.price_max.setPlaceholderText("до")
        self.price_max.setFixedWidth(60)
        layout.addWidget(self.price_max)
        
        # Кнопки
        self.apply_btn = QPushButton("🔘 Применить")
        self.apply_btn.clicked.connect(self.apply_filter)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a3a5a;
                color: #8aabca;
                border: 1px solid #2a4a6a;
                border-radius: 4px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #2a4a6a;
                color: #ffffff;
            }
        """)
        layout.addWidget(self.apply_btn)
        
        self.reset_btn = QPushButton("🔄 Сбросить")
        self.reset_btn.clicked.connect(self.reset_filter)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #5a7a9a;
                border: 1px solid #1a2a3a;
                border-radius: 4px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #1a2a3a;
                color: #8aabca;
            }
        """)
        layout.addWidget(self.reset_btn)
        
        layout.addStretch()
        
        # Информация о количестве
        self.count_label = QLabel("Всего: 0")
        self.count_label.setStyleSheet("color: #5a7a9a; font-size: 12px;")
        layout.addWidget(self.count_label)
        
        self.setLayout(layout)
    
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
'''
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.print_success(f"Создан {file_path}")
            return True
        except Exception as e:
            self.print_error(f"Ошибка создания файла: {e}")
            return False
    
    def create_status_bar(self) -> bool:
        """Создание ui/widgets/modern_status_bar.py"""
        self.print_header("4. СОЗДАНИЕ MODERN_STATUS_BAR.PY")
        
        file_path = self.project_root / "ui" / "widgets" / "modern_status_bar.py"
        
        content = '''"""
Современный статус-бар
Отображает информацию о состоянии приложения
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from datetime import datetime


class ModernStatusBar(QStatusBar):
    """Современный статус-бар с информацией"""
    
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
        
        # Левый статус
        self.left_label = QLabel("💻 Готов к работе")
        self.addWidget(self.left_label)
        
        self.addPermanentWidget(QLabel("|"))
        
        # Статус синхронизации
        self.sync_label = QLabel("🔄 Синхронизация: не выполнена")
        self.sync_label.setObjectName("highlight")
        self.addPermanentWidget(self.sync_label)
        
        self.addPermanentWidget(QLabel("|"))
        
        # Статус авторизации
        self.auth_label = QLabel("✅ Авторизован")
        self.auth_label.setObjectName("highlight")
        self.addPermanentWidget(self.auth_label)
    
    def set_message(self, message: str):
        """Установка сообщения"""
        self.left_label.setText(message)
    
    def set_sync_status(self, status: str):
        """Установка статуса синхронизации"""
        self.sync_label.setText(f"🔄 {status}")
    
    def set_auth_status(self, status: str):
        """Установка статуса авторизации"""
        self.auth_label.setText(status)
'''
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.print_success(f"Создан {file_path}")
            return True
        except Exception as e:
            self.print_error(f"Ошибка создания файла: {e}")
            return False
    
    def update_main_window(self) -> bool:
        """Обновление ui/main_window.py"""
        self.print_header("5. ОБНОВЛЕНИЕ MAIN_WINDOW.PY")
        
        file_path = self.project_root / "ui" / "main_window.py"
        
        # Создаем резервную копию
        if file_path.exists():
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            shutil.copy2(file_path, backup_path)
            self.print_info(f"Создана резервная копия: {backup_path}")
        
        content = '''"""
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
                color: #8aabca;
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
                color: #c8d0dc;
                border: 1px solid #1a2a3a;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #4a8aba;
            }
            QComboBox {
                background-color: #0d1520;
                color: #c8d0dc;
                border: 1px solid #1a2a3a;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #0d1520;
                color: #c8d0dc;
                selection-background-color: #1a3a5a;
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
        
        # Верхняя панель с заголовком
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
            user_label = QLabel(f"👤 {user['username"]}")
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
            f"📄 {item.title}\\n\\n"
            f"💰 Цена: {item.price:,} ₽\\n"
            f"📌 Статус: {item.status}\\n"
            f"👁️ Просмотры: {item.views}\\n"
            f"📞 Звонки: {item.calls}\\n"
            f"💬 Сообщения: {getattr(item, 'messages', 0)}\\n"
            f"⭐ Избранные: {item.favorites}"
        )
    
    def apply_filters(self, filters):
        """Применение фильтров"""
        # TODO: Реализовать фильтрацию
        self.status_bar.set_message("🔍 Фильтры применены")
    
    def update_time(self):
        """Обновление времени"""
        from datetime import datetime
        self.time_label.setText(datetime.now().strftime("%H:%M:%S"))
'''
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.print_success(f"Обновлен {file_path}")
            return True
        except Exception as e:
            self.print_error(f"Ошибка обновления файла: {e}")
            return False
    
    def update_widgets_init(self) -> bool:
        """Обновление ui/widgets/__init__.py"""
        file_path = self.project_root / "ui" / "widgets" / "__init__.py"
        
        content = '''"""
Виджеты интерфейса
"""
from .project_panel import ProjectPanel
from .items_panel import ItemsPanel
from .filter_panel import FilterPanel
from .modern_status_bar import ModernStatusBar

__all__ = ['ProjectPanel', 'ItemsPanel', 'FilterPanel', 'ModernStatusBar']
'''
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.print_success(f"Обновлен {file_path}")
            return True
        except Exception as e:
            self.print_error(f"Ошибка обновления файла: {e}")
            return False
    
    def show_summary(self):
        """Показывает итоговый отчет"""
        self.print_header("📊 ИТОГОВЫЙ ОТЧЕТ")
        
        print(f"\n{self.BOLD}Выполненные шаги:{self.RESET}")
        for step in self.steps:
            print(f"  {step}")
        
        if self.errors:
            print(f"\n{self.RED}Ошибки:{self.RESET}")
            for error in self.errors:
                print(f"  {error}")
        
        print(f"\n{self.BOLD}{self.GREEN}✅ Этап 4 завершен!{self.RESET}")
        print(f"\n{self.BOLD}📋 Дальнейшие действия:{self.RESET}")
        print(f"  1. Запустите приложение: {self.BOLD}python main.py{self.RESET}")
        print(f"  2. Проверьте отображение двух панелей")
        print(f"  3. Проверьте работу фильтров")
        print(f"  4. Если всё OK, переходите к Этапу 5 (Фильтры и импорт)")
    
    def run(self):
        """Запуск всех изменений"""
        print(self.BOLD + """
    ╔═══════════════════════════════════════════════════════════╗
    ║         🖥️ ЭТАП 4: UI — ДВЕ ПАНЕЛИ                    ║
    ║         Avito Commander 1.0                            ║
    ╚═══════════════════════════════════════════════════════════╝
    """ + self.RESET)
        
        # 1. Создаем папку widgets
        self.create_widgets_folder()
        
        # 2. Создаем ProjectPanel
        self.create_project_panel()
        
        # 3. Создаем ItemsPanel
        self.create_items_panel()
        
        # 4. Создаем FilterPanel
        self.create_filter_panel()
        
        # 5. Создаем ModernStatusBar
        self.create_status_bar()
        
        # 6. Обновляем MainWindow
        self.update_main_window()
        
        # 7. Обновляем __init__.py
        self.update_widgets_init()
        
        # Итоговый отчет
        self.show_summary()


def main():
    updater = Phase4Updater()
    updater.run()


if __name__ == "__main__":
    main()