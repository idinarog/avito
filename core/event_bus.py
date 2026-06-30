"""
Шина событий для коммуникации между компонентами
"""

from typing import Dict, List, Callable, Any
from PyQt5.QtCore import QObject, pyqtSignal


class EventBus(QObject):
    """
    Центральная шина событий
    """
    
    # Сигналы для разных типов событий
    user_logged_in = pyqtSignal(object)  # user
    user_logged_out = pyqtSignal()
    project_changed = pyqtSignal(object)  # project
    items_updated = pyqtSignal()
    sync_started = pyqtSignal()
    sync_finished = pyqtSignal(int)  # count
    error_occurred = pyqtSignal(str)
    notification = pyqtSignal(str, str)  # title, message
    
    def __init__(self):
        super().__init__()
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, callback: Callable):
        """
        Подписаться на событие
        
        Аргументы:
            event_type: Тип события
            callback: Функция-обработчик
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Отписаться от события"""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)
    
    def emit(self, event_type: str, data: Any = None):
        """
        Отправить событие
        
        Аргументы:
            event_type: Тип события
            data: Данные события
        """
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Ошибка в обработчике {event_type}: {e}")
        
        # Отправляем через Qt сигналы
        if event_type == "user_logged_in":
            self.user_logged_in.emit(data)
        elif event_type == "user_logged_out":
            self.user_logged_out.emit()
        elif event_type == "project_changed":
            self.project_changed.emit(data)
        elif event_type == "items_updated":
            self.items_updated.emit()
        elif event_type == "sync_started":
            self.sync_started.emit()
        elif event_type == "sync_finished":
            self.sync_finished.emit(data)
        elif event_type == "error_occurred":
            self.error_occurred.emit(data)
        elif event_type == "notification":
            title, message = data
            self.notification.emit(title, message)
