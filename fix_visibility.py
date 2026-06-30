#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для исправления читаемости текста в интерфейсе
Заменяет черный текст на светлый в FilterPanel и MainWindow
"""

import os
import re
from pathlib import Path


def fix_filter_panel():
    """Исправление видимости в фильтрах"""
    file_path = Path("ui/widgets/filter_panel.py")
    
    if not file_path.exists():
        print("❌ Файл ui/widgets/filter_panel.py не найден!")
        return False
    
    print(f"📖 Читаем {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Находим метод setup_ui
    if 'def setup_ui(self):' not in content:
        print("❌ Метод setup_ui не найден!")
        return False
    
    # Заменяем содержимое метода setup_ui
    new_setup_ui = '''    def setup_ui(self):
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
        self.setStyleSheet("background-color: #111927; border-radius: 4px;")'''
    
    # Находим старый setup_ui и заменяем
    pattern = r'def setup_ui\(self\):.*?(?=\n    def |\nclass |\Z)'
    new_content = re.sub(pattern, new_setup_ui, content, flags=re.DOTALL)
    
    # Сохраняем
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ ui/widgets/filter_panel.py обновлен")
    return True


def fix_main_window():
    """Исправление стилей в главном окне"""
    file_path = Path("ui/main_window.py")
    
    if not file_path.exists():
        print("❌ Файл ui/main_window.py не найден!")
        return False
    
    print(f"📖 Читаем {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем, есть ли уже правильные стили
    if 'color: #e8eef4' in content:
        print("✅ Стили уже исправлены!")
        return True
    
    # Заменяем метод apply_styles
    new_apply_styles = '''    def apply_styles(self):
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
        """)'''
    
    # Находим старый apply_styles и заменяем
    pattern = r'def apply_styles\(self\):.*?(?=\n    def |\nclass |\Z)'
    if re.search(pattern, content, flags=re.DOTALL):
        new_content = re.sub(pattern, new_apply_styles, content, flags=re.DOTALL)
    else:
        # Если метода нет, вставляем после __init__
        init_pos = content.find('def __init__')
        if init_pos != -1:
            # Ищем конец __init__
            end_init = content.find('    def ', init_pos + 10)
            if end_init != -1:
                new_content = content[:end_init] + '\n' + new_apply_styles + '\n' + content[end_init:]
            else:
                new_content = content + '\n' + new_apply_styles
        else:
            print("❌ Не найден метод __init__")
            return False
    
    # Сохраняем
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ ui/main_window.py обновлен")
    return True


def main():
    print("""
    ╔═══════════════════════════════════════════════╗
    ║     🔧 ИСПРАВЛЕНИЕ ВИДИМОСТИ ТЕКСТА        ║
    ║     Avito Commander — Читаемость           ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    # Проверяем, что мы в корне проекта
    if not Path("ui").exists():
        print("❌ Папка ui не найдена! Запустите скрипт из корня проекта.")
        return
    
    # Исправляем файлы
    ok1 = fix_filter_panel()
    ok2 = fix_main_window()
    
    print("\n" + "="*50)
    if ok1 and ok2:
        print("✅ ВСЕ ФАЙЛЫ ИСПРАВЛЕНЫ!")
        print("🚀 Запустите приложение: python main.py")
    else:
        print("❌ Некоторые файлы не были исправлены")
        print("📝 Проверьте, что файлы существуют:")
        print("   - ui/widgets/filter_panel.py")
        print("   - ui/main_window.py")


if __name__ == "__main__":
    main()
