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
