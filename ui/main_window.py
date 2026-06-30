from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import datetime

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Avito Commander")
        self.resize(1200, 800)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Верхняя панель с пользователем
        top_bar = QHBoxLayout()
        user = self.app.current_user
        if user:
            user_label = QLabel(f"👤 {user['username']}")
        else:
            user_label = QLabel("👤 Не авторизован")
        top_bar.addWidget(user_label)
        top_bar.addStretch()

        self.status_label = QLabel("Готов")
        top_bar.addWidget(self.status_label)

        # Кнопка синхронизации
        self.sync_btn = QPushButton("🔄 Синхронизация")
        self.sync_btn.clicked.connect(self.sync_items)
        top_bar.addWidget(self.sync_btn)

        layout.addLayout(top_bar)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Цена", "Статус", "Просмотры", "Звонки", "Сообщения", "Лиды", "CTR", "CPL"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # Загружаем данные
        self.load_items_from_db()

    def load_items_from_db(self):
        # Заглушка пока нет реальных данных
        self.table.setRowCount(0)
        print("Загрузка данных из БД (заглушка)")

    def sync_items(self):
        print("Синхронизация запущена")
        self.status_label.setText("Синхронизация...")
        QTimer.singleShot(100, self._do_sync)

    def _do_sync(self):
        self.status_label.setText("Синхронизация завершена")
        print("Синхронизация выполнена")
