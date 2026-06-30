
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDate


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Avito Commander 1.0")
        self.resize(1400, 900)

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)

        # === SIDEBAR ===
        sidebar = QVBoxLayout()

        self.project_list = QListWidget()
        self.project_list.addItems([
            "Основной проект (18)",
            "Авто (4)",
            "Недвижимость (7)",
            "Электроника (12)"
        ])

        sidebar.addWidget(QLabel("ПРОЕКТЫ"))
        sidebar.addWidget(self.project_list)

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(250)

        # === RIGHT SIDE ===
        right_layout = QVBoxLayout()

        # === TOP BAR ===
        top_bar = QHBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText("Поиск...")

        self.sync_btn = QPushButton("Синхронизация")
        self.import_btn = QPushButton("Импорт")
        self.export_btn = QPushButton("Экспорт")

        top_bar.addWidget(self.search)
        top_bar.addStretch()
        top_bar.addWidget(self.sync_btn)
        top_bar.addWidget(self.import_btn)
        top_bar.addWidget(self.export_btn)

        # === DATE FILTER ===
        date_layout = QHBoxLayout()

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-30))

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())

        date_layout.addWidget(QLabel("Период:"))
        date_layout.addWidget(self.date_from)
        date_layout.addWidget(self.date_to)
        date_layout.addStretch()

        # === TABLE ===
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Название", "Цена", "Статус",
            "Просмотры", "Звонки", "Сообщения",
            "Лиды", "CTR", "CPL"
        ])

        self.table.horizontalHeader().setStretchLastSection(True)

        self.load_mock_data()

        # === BOTTOM STATS ===
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("Просмотры: 0 | Лиды: 0 | CTR: 0%")
        stats_layout.addWidget(self.stats_label)

        # === ASSEMBLE ===
        right_layout.addLayout(top_bar)
        right_layout.addLayout(date_layout)
        right_layout.addWidget(self.table)
        right_layout.addLayout(stats_layout)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(right_widget)

        # === SIGNALS ===
        self.sync_btn.clicked.connect(self.sync)
        self.date_from.dateChanged.connect(self.filter_table)
        self.date_to.dateChanged.connect(self.filter_table)

    def load_mock_data(self):
        data = [
            [1, "MacBook Pro", 1500, "Active", 10, 2, 3, 5, "2.3%", 250],
            [2, "iPhone 15", 850, "Active", 5, 0, 1, 1, "1.2%", 170],
            [3, "Квартира", 5000, "Inactive", 20, 3, 4, 7, "3.4%", 1000],
            [4, "Дизайнер", 2000, "Blocked", 0, 0, 0, 0, "-", "-"],
        ]

        self.table.setRowCount(len(data))

        for row, item in enumerate(data):
            for col, val in enumerate(item):
                cell = QTableWidgetItem(str(val))

                if col == 3:
                    if val == "Active":
                        cell.setForeground(Qt.green)
                    elif val == "Inactive":
                        cell.setForeground(Qt.yellow)
                    else:
                        cell.setForeground(Qt.red)

                self.table.setItem(row, col, cell)

    def filter_table(self):
        pass

    def sync(self):
        print("🔄 Синхронизация (пока заглушка)")

    def apply_styles(self):
        self.setStyleSheet(
            '''
            QWidget {
                background-color: #0b1220;
                color: #cbd5e1;
                font-size: 13px;
            }

            QLineEdit, QDateEdit {
                background: #111827;
                border: 1px solid #1f2937;
                padding: 5px;
            }

            QPushButton {
                background: #1f2937;
                border: 1px solid #374151;
                padding: 6px;
            }

            QPushButton:hover {
                background: #2563eb;
            }

            QTableWidget {
                background: #020617;
                gridline-color: #1e293b;
            }

            QHeaderView::section {
                background: #0f172a;
                padding: 5px;
            }
            '''
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())


    # =========================
    # 🔐 LOGIN
    # =========================
    def open_login(self):
        dialog = LoginDialog()

        token = dialog.exec_()

        print("LOGIN RESULT:", token)
