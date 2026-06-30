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
