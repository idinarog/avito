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
