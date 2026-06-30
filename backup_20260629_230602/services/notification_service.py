"""
Сервис для уведомлений
"""

from PyQt5.QtCore import QObject


class NotificationService(QObject):
    """Сервис для отправки уведомлений"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
    
    def send(self, title: str, message: str, is_important: bool = False):
        """Отправка уведомления"""
        print(f"[УВЕДОМЛЕНИЕ] {title}: {message}")
