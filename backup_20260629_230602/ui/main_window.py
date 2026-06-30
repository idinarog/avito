"""
Главное окно приложения
Отображает объявления из Avito API с возможностью синхронизации
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from core.app import Application
from datetime import datetime


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self, app: Application):
        super().__init__()
        
        self.app = app
        self.current_project_id = None
        
        self.setWindowTitle(f"Avito Commander - {app.get_current_user().username}")
        self.setGeometry(100, 100, 1400, 800)
        
        # Инициализация UI
        self.init_ui()
        
        # Подключение событий
        self.connect_events()
        
        # Загрузка данных
        self.load_initial_data()
    
    def init_ui(self):
        """Создание интерфейса"""
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        central_widget.setLayout(main_layout)
        
        # Верхняя панель с проектами и управлением
        self.create_project_panel(main_layout)
        
        # Панель фильтров
        self.create_filter_panel(main_layout)
        
        # Таблица объявлений
        self.create_table(main_layout)
        
        # Панель статистики
        self.create_stats_panel(main_layout)
        
        # Нижняя панель с действиями
        self.create_action_panel(main_layout)
        
        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("✅ Готов к работе")
    
    def create_project_panel(self, parent_layout):
        """Создание панели проектов"""
        panel = QHBoxLayout()
        panel.setSpacing(10)
        
        # Метка "Проекты:"
        project_label = QLabel("📁 Проекты:")
        project_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        panel.addWidget(project_label)
        
        # Кнопки проектов
        self.project_buttons = []
        self.load_project_buttons()
        
        # Кнопка создания проекта
        add_btn = QPushButton("➕ Новый проект")
        add_btn.clicked.connect(self.create_project)
        add_btn.setFixedHeight(30)
        panel.addWidget(add_btn)
        
        # Заполнитель
        panel.addStretch()
        
        # Кнопка синхронизации
        self.sync_btn = QPushButton("🔄 Синхронизировать")
        self.sync_btn.clicked.connect(self.sync_items)
        self.sync_btn.setFixedHeight(30)
        self.sync_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        panel.addWidget(self.sync_btn)
        
        # Кнопка обновить
        refresh_btn = QPushButton("↻ Обновить")
        refresh_btn.clicked.connect(self.load_items)
        refresh_btn.setFixedHeight(30)
        panel.addWidget(refresh_btn)
        
        # Кнопка настроек
        settings_btn = QPushButton("⚙️ Настройки")
        settings_btn.clicked.connect(self.show_settings)
        settings_btn.setFixedHeight(30)
        panel.addWidget(settings_btn)
        
        # Кнопка выхода
        logout_btn = QPushButton("🚪 Выйти")
        logout_btn.clicked.connect(self.logout)
        logout_btn.setFixedHeight(30)
        panel.addWidget(logout_btn)
        
        parent_layout.addLayout(panel)
    
    def load_project_buttons(self):
        """Загрузка кнопок проектов"""
        user = self.app.get_current_user()
        if not user:
            return
        
        projects = self.app.project_repo.get_by_user(user.id)
        
        # Удаляем старые кнопки
        for btn in self.project_buttons:
            btn.deleteLater()
        self.project_buttons.clear()
        
        # Создаем новые кнопки
        for project in projects:
            btn = QPushButton(project.name)
            btn.setCheckable(True)
            btn.setFixedHeight(30)
            btn.clicked.connect(lambda checked, p=project: self.select_project(p))
            
            # Добавляем в панель после метки
            layout = self.centralWidget().layout()
            project_panel = layout.itemAt(0).layout()
            project_panel.insertWidget(len(self.project_buttons) + 1, btn)
            
            self.project_buttons.append(btn)
        
        # Выбираем первый проект
        if projects:
            self.select_project(projects[0])
    
    def create_filter_panel(self, parent_layout):
        """Создание панели фильтров"""
        panel = QHBoxLayout()
        panel.setSpacing(10)
        
        # Фильтр по статусу
        panel.addWidget(QLabel("Статус:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Все", "active", "inactive", "blocked"])
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        self.status_filter.setFixedWidth(120)
        panel.addWidget(self.status_filter)
        
        # Поиск по названию
        panel.addWidget(QLabel("Поиск:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите текст для поиска...")
        self.search_input.textChanged.connect(self.apply_filters)
        self.search_input.setFixedWidth(200)
        panel.addWidget(self.search_input)
        
        # Фильтр по цене
        panel.addWidget(QLabel("Цена от:"))
        self.price_min = QLineEdit()
        self.price_min.setPlaceholderText("0")
        self.price_min.setFixedWidth(70)
        self.price_min.textChanged.connect(self.apply_filters)
        panel.addWidget(self.price_min)
        
        panel.addWidget(QLabel("до:"))
        self.price_max = QLineEdit()
        self.price_max.setPlaceholderText("999999")
        self.price_max.setFixedWidth(70)
        self.price_max.textChanged.connect(self.apply_filters)
        panel.addWidget(self.price_max)
        
        panel.addStretch()
        
        # Информация о количестве
        self.count_label = QLabel("Всего: 0 объявлений")
        self.count_label.setFont(QFont("Arial", 10))
        panel.addWidget(self.count_label)
        
        # Информация о последней синхронизации
        self.sync_info_label = QLabel("")
        self.sync_info_label.setStyleSheet("color: #888; font-size: 10px;")
        panel.addWidget(self.sync_info_label)
        
        parent_layout.addLayout(panel)
    
    def create_table(self, parent_layout):
        """Создание таблицы объявлений"""
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID Avito", "Название", "Цена", "Статус", 
            "Просмотры", "Звонки", "Избранные", "Дата"
        ])
        
        # Настройка таблицы
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Ширина колонок
        self.table.setColumnWidth(0, 100)   # ID Avito
        self.table.setColumnWidth(1, 350)   # Название
        self.table.setColumnWidth(2, 120)   # Цена
        self.table.setColumnWidth(3, 100)   # Статус
        self.table.setColumnWidth(4, 100)   # Просмотры
        self.table.setColumnWidth(5, 80)    # Звонки
        self.table.setColumnWidth(6, 100)   # Избранные
        self.table.setColumnWidth(7, 150)   # Дата
        
        # Подключение событий
        self.table.itemDoubleClicked.connect(self.on_item_double_click)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        parent_layout.addWidget(self.table)
    
    def create_stats_panel(self, parent_layout):
        """Создание панели статистики"""
        panel = QHBoxLayout()
        panel.setSpacing(20)
        
        # Карточки статистики
        self.stats_widgets = {}
        stats_data = [
            ("📊 Всего", "total", "0"),
            ("✅ Активные", "active", "0"),
            ("❌ Неактивные", "inactive", "0"),
            ("🚫 Заблокированные", "blocked", "0"),
            ("👁️ Просмотры", "views", "0"),
            ("📞 Звонки", "calls", "0"),
            ("⭐ Избранные", "favorites", "0"),
        ]
        
        for label, key, default in stats_data:
            widget = QFrame()
            widget.setFrameShape(QFrame.StyledPanel)
            widget.setStyleSheet("""
                QFrame {
                    background-color: #2d2d3d;
                    border-radius: 6px;
                    padding: 5px;
                    min-width: 100px;
                }
            """)
            
            layout = QVBoxLayout()
            layout.setSpacing(2)
            
            title = QLabel(label)
            title.setStyleSheet("color: #aaa; font-size: 10px;")
            layout.addWidget(title)
            
            value = QLabel(default)
            value.setStyleSheet("color: #fff; font-size: 16px; font-weight: bold;")
            value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(value)
            
            widget.setLayout(layout)
            panel.addWidget(widget)
            
            self.stats_widgets[key] = value
        
        panel.addStretch()
        
        # Кнопка экспорта
        export_btn = QPushButton("📥 Экспорт")
        export_btn.clicked.connect(self.export_data)
        export_btn.setFixedHeight(30)
        panel.addWidget(export_btn)
        
        parent_layout.addLayout(panel)
    
    def create_action_panel(self, parent_layout):
        """Создание панели действий"""
        panel = QHBoxLayout()
        panel.setSpacing(10)
        
        # Кнопки действий
        self.edit_btn = QPushButton("✏️ Редактировать")
        self.edit_btn.clicked.connect(self.edit_item)
        self.edit_btn.setEnabled(False)
        panel.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.clicked.connect(self.delete_item)
        self.delete_btn.setEnabled(False)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #555;
            }
        """)
        panel.addWidget(self.delete_btn)
        
        self.activate_btn = QPushButton("✅ Активировать")
        self.activate_btn.clicked.connect(self.activate_item)
        self.activate_btn.setEnabled(False)
        panel.addWidget(self.activate_btn)
        
        self.deactivate_btn = QPushButton("⏸️ Деактивировать")
        self.deactivate_btn.clicked.connect(self.deactivate_item)
        self.deactivate_btn.setEnabled(False)
        panel.addWidget(self.deactivate_btn)
        
        panel.addStretch()
        
        # Информация о выбранных
        self.selection_label = QLabel("Выбрано: 0")
        self.selection_label.setStyleSheet("color: #888;")
        panel.addWidget(self.selection_label)
        
        parent_layout.addLayout(panel)
    
    def connect_events(self):
        """Подключение событий"""
        self.app.event_bus.items_updated.connect(self.load_items)
        self.app.event_bus.sync_finished.connect(self.on_sync_finished)
        self.app.event_bus.sync_started.connect(self.on_sync_started)
        self.app.event_bus.error_occurred.connect(self.on_error)
        self.app.event_bus.project_changed.connect(self.on_project_changed)
    
    def load_initial_data(self):
        """Загрузка начальных данных"""
        user = self.app.get_current_user()
        if user:
            print(f"👤 Пользователь: {user.username}")
            self.load_project_buttons()
            self.load_items()
            self.update_sync_info()
    
    def load_items(self):
        """Загрузка объявлений из БД с применением фильтров"""
        self.table.setRowCount(0)
        
        if not self.current_project_id:
            self.count_label.setText("Всего: 0 объявлений")
            return
        
        try:
            items = self.app.item_repo.get_by_project(self.current_project_id)
            items = self.apply_filters_to_items(items)
            
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
                self.table.setItem(row, 6, QTableWidgetItem(str(item.favorites or 0)))
                
                date_str = ""
                if item.created_at:
                    date_str = item.created_at.strftime("%d.%m.%Y %H:%M")
                self.table.setItem(row, 7, QTableWidgetItem(date_str))
            
            self.count_label.setText(f"Всего: {len(items)} объявлений")
            self.update_stats(items)
            self.update_sync_info()
            
            self.status_bar.showMessage(f"✅ Загружено {len(items)} объявлений")
            
        except Exception as e:
            self.status_bar.showMessage(f"❌ Ошибка загрузки: {str(e)}")
            print(f"❌ Ошибка загрузки объявлений: {e}")
    
    def apply_filters_to_items(self, items):
        """Применяет фильтры к списку объявлений"""
        status = self.status_filter.currentText()
        if status != "Все":
            items = [i for i in items if i.status == status]
        
        search = self.search_input.text().strip().lower()
        if search:
            items = [i for i in items if search in (i.title or "").lower()]
        
        try:
            price_min = int(self.price_min.text()) if self.price_min.text() else 0
            price_max = int(self.price_max.text()) if self.price_max.text() else 999999999
            items = [i for i in items if price_min <= (i.price or 0) <= price_max]
        except ValueError:
            pass
        
        return items
    
    def apply_filters(self):
        """Применение фильтров к таблице"""
        self.load_items()
    
    def update_stats(self, items):
        """Обновление статистики"""
        total = len(items)
        active = len([i for i in items if i.status == "active"])
        inactive = len([i for i in items if i.status == "inactive"])
        blocked = len([i for i in items if i.status == "blocked"])
        
        total_views = sum(i.views or 0 for i in items)
        total_calls = sum(i.calls or 0 for i in items)
        total_favorites = sum(i.favorites or 0 for i in items)
        
        self.stats_widgets["total"].setText(str(total))
        self.stats_widgets["active"].setText(str(active))
        self.stats_widgets["inactive"].setText(str(inactive))
        self.stats_widgets["blocked"].setText(str(blocked))
        self.stats_widgets["views"].setText(f"{total_views:,}")
        self.stats_widgets["calls"].setText(f"{total_calls:,}")
        self.stats_widgets["favorites"].setText(f"{total_favorites:,}")
    
    def update_sync_info(self):
        """Обновление информации о синхронизации"""
        if self.app.sync_service:
            last_sync = self.app.sync_service.get_last_sync_time()
            if last_sync:
                self.sync_info_label.setText(f"🔄 Последняя синхронизация: {last_sync.strftime('%H:%M:%S %d.%m.%Y')}")
            else:
                self.sync_info_label.setText("🔄 Синхронизация не выполнялась")
    
    def select_project(self, project):
        """Выбор проекта"""
        self.current_project_id = project.id
        self.app.set_current_project(project)
        
        for btn in self.project_buttons:
            btn.setChecked(btn.text() == project.name)
        
        self.load_items()
    
    def create_project(self):
        """Создание нового проекта"""
        name, ok = QInputDialog.getText(
            self,
            "Новый проект",
            "Введите название проекта:"
        )
        
        if ok and name:
            user = self.app.get_current_user()
            project = self.app.project_service.create_project(user.id, name)
            if project:
                QMessageBox.information(self, "Успех", f"Проект '{name}' создан!")
                self.load_project_buttons()
    
    def sync_items(self):
        """Синхронизация с Avito API"""
        if not self.app.get_current_user():
            self.status_bar.showMessage("❌ Пользователь не авторизован")
            return
        
        user = self.app.get_current_user()
        if not user.access_token:
            reply = QMessageBox.question(
                self,
                "Требуется авторизация",
                "Для синхронизации требуется токен доступа.\n"
                "Хотите авторизоваться через Avito?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                from ui.login_dialog import LoginDialog
                login_dialog = LoginDialog(self.app, self)
                if login_dialog.exec_() == QDialog.Accepted:
                    self.app.current_user = login_dialog.get_user()
                    self.load_initial_data()
                return
            else:
                return
        
        projects = self.app.project_repo.get_by_user(user.id)
        if not projects:
            project = self.app.project_service.create_project(user.id, "Основной проект")
            if not project:
                self.status_bar.showMessage("❌ Ошибка создания проекта")
                return
            project_id = project.id
        else:
            project_id = projects[0].id
        
        self.app.sync_service.set_access_token(user.access_token)
        self.app.sync_service.set_user(user.user_id_avito)
        
        self.status_bar.showMessage("🔄 Синхронизация...")
        
        try:
            items = self.app.sync_service.sync_items(project_id)
            self.load_items()
            self.status_bar.showMessage(f"✅ Синхронизировано {len(items)} объявлений")
        except Exception as e:
            self.status_bar.showMessage(f"❌ Ошибка: {str(e)}")
            QMessageBox.critical(self, "Ошибка синхронизации", str(e))
    
    def on_sync_started(self):
        """Обработчик начала синхронизации"""
        self.sync_btn.setEnabled(False)
        self.sync_btn.setText("⏳ Синхронизация...")
        self.status_bar.showMessage("🔄 Загрузка данных из Avito...")
    
    def on_sync_finished(self, count):
        """Обработчик завершения синхронизации"""
        self.sync_btn.setEnabled(True)
        self.sync_btn.setText("🔄 Синхронизировать")
        self.status_bar.showMessage(f"✅ Синхронизировано {count} объявлений")
        self.load_items()
    
    def on_project_changed(self, project):
        """Обработчик смены проекта"""
        self.select_project(project)
    
    def on_error(self, error):
        """Обработчик ошибок"""
        self.status_bar.showMessage(f"❌ {error}")
        QMessageBox.critical(self, "Ошибка", error)
    
    def on_selection_changed(self):
        """Обработчик изменения выделения"""
        selected = len(self.table.selectedItems())
        if selected > 0:
            selected = selected // self.table.columnCount()
            self.selection_label.setText(f"Выбрано: {selected}")
            
            has_selection = selected > 0
            self.edit_btn.setEnabled(has_selection)
            self.delete_btn.setEnabled(has_selection)
            self.activate_btn.setEnabled(has_selection)
            self.deactivate_btn.setEnabled(has_selection)
        else:
            self.selection_label.setText("Выбрано: 0")
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.activate_btn.setEnabled(False)
            self.deactivate_btn.setEnabled(False)
    
    def on_item_double_click(self, item):
        """Обработчик двойного клика по объявлению"""
        row = item.row()
        item_id = self.table.item(row, 0).text()
        title = self.table.item(row, 1).text()
        price = self.table.item(row, 2).text()
        status = self.table.item(row, 3).text()
        
        QMessageBox.information(
            self,
            f"Объявление #{item_id}",
            f"📋 {title}\n\n"
            f"💰 Цена: {price}\n"
            f"📌 Статус: {status}\n"
            f"👁️ Просмотры: {self.table.item(row, 4).text()}\n"
            f"📞 Звонки: {self.table.item(row, 5).text()}\n"
            f"⭐ Избранные: {self.table.item(row, 6).text()}\n"
            f"📅 Дата: {self.table.item(row, 7).text()}",
            QMessageBox.Ok
        )
    
    def edit_item(self):
        """Редактирование объявления"""
        selected = self.table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        item_id = self.table.item(row, 0).text()
        title = self.table.item(row, 1).text()
        
        new_title, ok = QInputDialog.getText(
            self,
            "Редактирование",
            f"Новое название для объявления #{item_id}:",
            QLineEdit.Normal,
            title
        )
        
        if ok and new_title:
            items = self.app.item_repo.get_by_project(self.current_project_id)
            for item in items:
                if str(item.item_id_avito) == item_id:
                    item.title = new_title
                    self.status_bar.showMessage(f"✅ Обновлено объявление #{item_id}")
                    break
            self.load_items()
    
    def delete_item(self):
        """Удаление объявления"""
        selected = self.table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        item_id = self.table.item(row, 0).text()
        title = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self,
            "Удаление объявления",
            f"Удалить объявление '{title}' (ID: {item_id})?\n"
            "Это действие также удалит его на Avito.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                user = self.app.get_current_user()
                success = self.app.sync_service.delete_item(user.user_id_avito, item_id)
                if success:
                    items = self.app.item_repo.get_by_project(self.current_project_id)
                    for item in items:
                        if str(item.item_id_avito) == item_id:
                            self.app.item_repo.delete(item.id)
                            break
                    self.load_items()
                    self.status_bar.showMessage(f"🗑️ Объявление {item_id} удалено")
                else:
                    self.status_bar.showMessage("❌ Ошибка удаления на Avito")
            except Exception as e:
                self.status_bar.showMessage(f"❌ Ошибка: {str(e)}")
    
    def activate_item(self):
        """Активация объявления"""
        self.change_item_status("active", "✅ Активировано")
    
    def deactivate_item(self):
        """Деактивация объявления"""
        self.change_item_status("inactive", "⏸️ Деактивировано")
    
    def change_item_status(self, new_status, success_message):
        """Изменение статуса объявления"""
        selected = self.table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        item_id = self.table.item(row, 0).text()
        
        try:
            user = self.app.get_current_user()
            result = self.app.sync_service.update_item_status(user.user_id_avito, item_id, new_status)
            if result:
                self.status_bar.showMessage(f"{success_message} объявление {item_id}")
                self.load_items()
            else:
                self.status_bar.showMessage(f"❌ Ошибка изменения статуса {item_id}")
        except Exception as e:
            self.status_bar.showMessage(f"❌ Ошибка: {str(e)}")
    
    def export_data(self):
        """Экспорт данных в CSV"""
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Экспорт", "Нет данных для экспорта")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить как CSV",
            f"avito_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV файлы (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                headers = []
                for col in range(self.table.columnCount()):
                    headers.append(self.table.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
            
            QMessageBox.information(
                self,
                "Экспорт завершен",
                f"Данные экспортированы в:\n{file_path}\n\n"
                f"Всего строк: {self.table.rowCount()}",
                QMessageBox.Ok
            )
            self.status_bar.showMessage(f"📥 Экспортировано {self.table.rowCount()} строк")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка экспорта", str(e))
    
    def show_settings(self):
        """Показывает окно настроек"""
        QMessageBox.information(
            self,
            "Настройки",
            "Настройки приложения будут доступны в следующей версии.",
            QMessageBox.Ok
        )
    
    def logout(self):
        """Выход из аккаунта"""
        reply = QMessageBox.question(
            self,
            "Выход",
            "Вы уверены, что хотите выйти?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.app.config.set("user/current_id", None)
            self.app.quit()
            self.close()