"""
Сервис для работы с проектами
"""

from typing import Optional
from database.repository import ProjectRepository
from core.event_bus import EventBus


class ProjectService:
    """Сервис для управления проектами"""
    
    def __init__(self, project_repo: ProjectRepository, event_bus: EventBus):
        self.project_repo = project_repo
        self.event_bus = event_bus
    
    def create_project(self, user_id: int, name: str, description: str = "") -> Optional[dict]:
        """Создание нового проекта"""
        project = self.project_repo.create(user_id, name, description)
        if project:
            self.event_bus.emit("project_changed", project)
            return project.__dict__
        return None
