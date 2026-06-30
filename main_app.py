"""
Модуль главного окна приложения
Содержит интерфейс для управления объявлениями Avito
"""

import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Any

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Импортируем наш класс для работы с API
from avito_api import AvitoAuth, AvitoAPI


class MainApp(QWidget):
    """
    Главное окно приложения для работы с объявлениями Avito
    Содержит таблицу, фильтры и элементы управления
    """
    
    def __init__(self, auth: AvitoAuth = None):
        """
        Инициализация главного окна
        
        Аргументы:
            auth: Объект AvitoAuth (если None, будет создан новый)
        """
        super().__init__()
        
        # Настройки окна
        self.setWindowTitle("Avito Commander - Управление объявлениями")
        self.setFixedSize(1400, 800)  # Чуть больше для комфортной работы
        
        # Инициализация авторизации
        self.auth = auth
        self.api = None
        self.user_id = None
        
        # Данные
        self.items = []  # Список объявлений
        self.current_page = 1
        self.total_pages = 1
        self.is_loading = False
        
        # Настройка интерфейса
        self.init_ui()
        
        # Загрузка данных при запуске
        if self.auth and self.auth.get_valid_token():
            self.api = AvitoAPI(self.auth)
            # Пытаемся загрузить user_id из сохраненных данных
            self.load_user_id()
            if self.user_id:
                self.load_items()
    
    def init_ui(self):
        """
        Создание всех элементов интерфейса
        """
        # Основной контейнер с отступами
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # ============================================================
        # ВЕРХНЯЯ ПАНЕЛЬ - ЗАГОЛОВОК И СТАТУС
        # ============================================================
        top_panel = QHBoxLayout()
        
        # Заголовок
        title_label = QLabel("📊 Управление объявлениями")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        top_panel.addWidget(title_label)
        
        # Заполнитель для выравнивания
        top_panel.addStretch()
        
        # Информация о пользователе
        self.user_label = QLabel("Пользователь: не авторизован")
        self.user_label.setFont(QFont("Arial", 10))
        top_panel.addWidget(self.user_label)
        
        # Время
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Arial", 10))
        top_panel.addWidget(self.time_label)
        
        # Таймер для обновления времени
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        main_layout.addLayout(top_panel)
        
        # ============================================================
        # ПАНЕЛЬ ФИЛЬТРОВ
        # ============================================================
        filter_panel = QHBoxLayout()
        filter_panel.setSpacing(10)
        
        # Статус объявления
        filter_panel.addWidget(QLabel("Статус:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Все", "active", "inactive", "blocked"])
        self.status_filter.currentTextChanged.connect(self.on_filter_changed)
        filter_panel.addWidget(self.status_filter)
        
        # Поиск по названию
        filter_panel.addWidget(QLabel("Поиск:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите текст для поиска...")
        self.search_input.textChanged.connect(self.on_filter_changed)
        filter_panel.addWidget(self.search_input)
        
        # Количество на странице
        filter_panel.addWidget(QLabel("Показывать:"))
        self.per_page = QComboBox()
        self.per_page.addItems(["10", "25", "50", "100"])
        self.per_page.currentTextChanged.connect(self.on_filter_changed)
        filter_panel.addWidget(self.per_page)
        
        # Заполнитель
        filter_panel.addStretch()
        
        # Кнопки действий
        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.clicked.connect(self.load_items)
        filter_panel.addWidget(self.refresh_btn)
        
        self.add_btn = QPushButton("➕ Создать")
        self.add_btn.clicked.connect(self.create_item)
        filter_panel.addWidget(self.add_btn)
        
        main_layout.addLayout(filter_panel)
        
        # ============================================================
        # ТАБЛИЦА С ОБЪЯВЛЕНИЯМИ
        # ============================================================
        self.table = QTableWidget()
        self.table.setColumnCount(8)  # Количество колонок
        self.table.setHorizontalHeaderLabels([
            "ID", "Название", "Цена", "Статус", 
            "Просмотры", "Звонки", "Избранные", "Дата"
        ])
        
        # Настройка внешнего вида таблицы
        self.table.setAlternatingRowColors(True)  # Чередование цветов строк
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # Выделение всей строки
        self.table.setSelectionMode(QTableWidget.SingleSelection)  # Выбор только одной строки
        self.table.setSortingEnabled(True)  # Включить сортировку
        
        # Настройка ширины колонок
        self.table.setColumnWidth(0, 100)   # ID
        self.table.setColumnWidth(1, 300)   # Название
        self.table.setColumnWidth(2, 100)   # Цена
        self.table.setColumnWidth(3, 100)   # Статус
        self.table.setColumnWidth(4, 80)    # Просмотры
        self.table.setColumnWidth(5, 80)    # Звонки
        self.table.setColumnWidth(6, 80)    # Избранные
        self.table.setColumnWidth(7, 150)   # Дата
        
        # Подключение обработчика двойного клика
        self.table.itemDoubleClicked.connect(self.on_item_double_click)
        
        main_layout.addWidget(self.table)
        
        # ============================================================
        # НИЖНЯЯ ПАНЕЛЬ - ПАГИНАЦИЯ И СТАТУС
        # ============================================================
        bottom_panel = QHBoxLayout()
        
        # Кнопки пагинации
        self.prev_btn = QPushButton("◀ Назад")
        self.prev_btn.clicked.connect(self.previous_page)
        self.prev_btn.setEnabled(False)
        bottom_panel.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("Вперед ▶")
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setEnabled(False)
        bottom_panel.addWidget(self.next_btn)
        
        # Информация о страницах
        self.page_label = QLabel("Страница 1 из 1")
        bottom_panel.addWidget(self.page_label)
        
        # Информация о количестве
        bottom_panel.addStretch()
        
        self.status_label = QLabel("Готово")
        bottom_panel.addWidget(self.status_label)
        
        main_layout.addLayout(bottom_panel)
        
        # Устанавливаем основной layout
        self.setLayout(main_layout)
    
    # ============================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С ДАННЫМИ
    # ============================================================
    
    def load_user_id(self):
        """
        Загружает user_id из файла или использует заглушку
        В реальном приложении user_id нужно получать от пользователя
        """
        try:
            if os.path.exists("user_id.txt"):
                with open("user_id.txt", "r") as f:
                    self.user_id = f.read().strip()
                    self.user_label.setText(f"Пользователь: {self.user_id}")
            else:
                # Используем user_id из auth если есть
                if self.auth and hasattr(self.auth, 'user_id'):
                    self.user_id = self.auth.user_id
                    self.user_label.setText(f"Пользователь: {self.user_id}")
                else:
                    # Если user_id не найден, показываем сообщение
                    self.user_label.setText("Пользователь: не указан")
                    QMessageBox.warning(
                        self,
                        "Предупреждение",
                        "User ID не найден. Проверьте настройки.",
                        QMessageBox.Ok
                    )
        except Exception as e:
            print(f"Ошибка загрузки user_id: {str(e)}")
    
    def load_items(self):
        """
        Загрузка объявлений с API
        """
        if not self.api or not self.user_id:
            self.status_label.setText("❌ Требуется авторизация")
            return
        
        # Блокируем повторные загрузки
        if self.is_loading:
            return
        
        self.is_loading = True
        self.status_label.setText("⏳ Загрузка объявлений...")
        QApplication.processEvents()  # Обновляем интерфейс
        
        try:
            # Получаем параметры фильтрации
            status = self.status_filter.currentText()
            if status == "Все":
                status = None
            
            per_page = int(self.per_page.currentText())
            
            # Загружаем объявления
            response = self.api.get_items(
                user_id=self.user_id,
                status=status,
                page=self.current_page,
                per_page=per_page
            )
            
            # Обрабатываем ответ
            self.items = response.get("items", [])
            self.total_pages = response.get("total_pages", 1)
            
            # Обновляем интерфейс
            self.display_items()
            self.update_pagination()
            
            self.status_label.setText(f"✅ Загружено {len(self.items)} объявлений")
            
        except Exception as e:
            self.status_label.setText(f"❌ Ошибка: {str(e)}")
            print(f"Ошибка загрузки: {str(e)}")
        finally:
            self.is_loading = False
    
    def display_items(self):
        """
        Отображает объявления в таблице
        """
        self.table.setRowCount(0)  # Очищаем таблицу
        
        # Применяем поиск (фильтрация на клиенте)
        search_text = self.search_input.text().lower()
        
        for item in self.items:
            # Проверяем поисковый фильтр
            title = item.get("title", "").lower()
            if search_text and search_text not in title:
                continue
            
            # Добавляем строку
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Заполняем ячейки
            self.table.setItem(row, 0, QTableWidgetItem(str(item.get("id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(item.get("title", "Без названия")))
            self.table.setItem(row, 2, QTableWidgetItem(f"{item.get('price', 0):,} ₽"))
            self.table.setItem(row, 3, QTableWidgetItem(item.get("status", "unknown")))
            
            # Статистика
            stats = item.get("stats", {})
            self.table.setItem(row, 4, QTableWidgetItem(str(stats.get("views", 0))))
            self.table.setItem(row, 5, QTableWidgetItem(str(stats.get("calls", 0))))
            self.table.setItem(row, 6, QTableWidgetItem(str(stats.get("favorites", 0))))
            
            # Дата
            date_str = item.get("created_at", "")
            if date_str:
                try:
                    date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    date_str = date.strftime("%d.%m.%Y %H:%M")
                except:
                    pass
            self.table.setItem(row, 7, QTableWidgetItem(date_str))
            
            # Цвет статуса
            status_item = self.table.item(row, 3)
            if item.get("status") == "active":
                status_item.setForeground(QColor(0, 150, 0))  # Зеленый
            elif item.get("status") == "inactive":
                status_item.setForeground(QColor(200, 200, 0))  # Желтый
            elif item.get("status") == "blocked":
                status_item.setForeground(QColor(200, 0, 0))  # Красный
    
    def update_pagination(self):
        """
        Обновляет информацию о пагинации
        """
        self.page_label.setText(f"Страница {self.current_page} из {self.total_pages}")
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)
    
    # ============================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ
    # ============================================================
    
    def on_filter_changed(self):
        """
        Обработчик изменения фильтров
        Сбрасывает на первую страницу и перезагружает
        """
        self.current_page = 1
        self.load_items()
    
    def on_item_double_click(self, item):
        """
        Обработчик двойного клика по объявлению
        Показывает детальную информацию
        """
        row = item.row()
        item_id = self.table.item(row, 0).text()
        title = self.table.item(row, 1).text()
        
        QMessageBox.information(
            self,
            f"Объявление #{item_id}",
            f"Название: {title}\n\nДетальная информация загружается...",
            QMessageBox.Ok
        )
    
    def previous_page(self):
        """
        Переход на предыдущую страницу
        """
        if self.current_page > 1:
            self.current_page -= 1
            self.load_items()
    
    def next_page(self):
        """
        Переход на следующую страницу
        """
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_items()
    
    def create_item(self):
        """
        Открывает диалог создания нового объявления
        """
        QMessageBox.information(
            self,
            "Создание объявления",
            "Функция в разработке...",
            QMessageBox.Ok
        )
    
    def update_time(self):
        """
        Обновляет время в статусной строке
        """
        self.time_label.setText(datetime.now().strftime("%H:%M:%S"))