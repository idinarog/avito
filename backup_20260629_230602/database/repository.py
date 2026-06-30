"""
Репозиторий для работы с базой данных
"""

from sqlalchemy.exc import IntegrityError
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from .models import DatabaseManager, User, Project, Item, SyncLog, Favorite, Settings


class UserRepository:
    """Репозиторий для работы с пользователями"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def create(self, username: str, user_id_avito: str, 
               access_token: str = None, refresh_token: str = None) -> Optional[int]:
        """Создание нового пользователя — возвращает ID"""
        session = self.db.get_session()
        try:
            user = User(
                username=username,
                user_id_avito=user_id_avito,
                access_token=access_token,
                refresh_token=refresh_token
            )
            session.add(user)
            session.commit()
            
            # Создаем настройки для пользователя
            settings = Settings(user_id=user.id)
            session.add(settings)
            session.commit()
            
            user_id = user.id
            print(f"✅ Пользователь создан: {username} (ID: {user_id})")
            return user_id
            
        except IntegrityError:
            session.rollback()
            print(f"❌ Пользователь {username} уже существует")
            return None
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка создания пользователя: {e}")
            return None
        finally:
            session.close()
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        session = self.db.get_session()
        try:
            return session.query(User).filter(User.id == user_id).first()
        finally:
            session.close()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Получение пользователя по имени"""
        session = self.db.get_session()
        try:
            return session.query(User).filter(User.username == username).first()
        finally:
            session.close()
    
    def get_all_active(self) -> List[User]:
        """Получение всех активных пользователей"""
        session = self.db.get_session()
        try:
            return session.query(User).filter(User.is_active == True).all()
        finally:
            session.close()
    
    def update(self, user: User) -> bool:
        """Обновление пользователя"""
        session = self.db.get_session()
        try:
            merged_user = session.merge(user)
            merged_user.updated_at = datetime.now()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка обновления: {e}")
            return False
        finally:
            session.close()


class ProjectRepository:
    """Репозиторий для работы с проектами"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def create(self, user_id: int, name: str, description: str = "") -> Optional[Project]:
        session = self.db.get_session()
        try:
            project = Project(
                user_id=user_id,
                name=name,
                description=description
            )
            session.add(project)
            session.commit()
            print(f"✅ Проект создан: {name}")
            return project
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка создания проекта: {e}")
            return None
        finally:
            session.close()
    
    def get_by_user(self, user_id: int) -> List[Project]:
        session = self.db.get_session()
        try:
            return session.query(Project).filter(
                Project.user_id == user_id,
                Project.is_active == True
            ).all()
        finally:
            session.close()


class ItemRepository:
    """Репозиторий для работы с объявлениями"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def save_from_api(self, project_id: int, item_data: Dict[str, Any]) -> Optional[Item]:
        session = self.db.get_session()
        try:
            item = session.query(Item).filter(
                Item.project_id == project_id,
                Item.item_id_avito == item_data.get('id')
            ).first()
            
            if item:
                item.title = item_data.get('title', item.title)
                item.description = item_data.get('description', item.description)
                item.price = item_data.get('price', item.price)
                item.status = item_data.get('status', item.status)
                item.updated_at = datetime.now()
            else:
                item = Item(
                    project_id=project_id,
                    item_id_avito=item_data.get('id'),
                    title=item_data.get('title', 'Без названия'),
                    description=item_data.get('description', ''),
                    price=item_data.get('price', 0),
                    status=item_data.get('status', 'unknown')
                )
                session.add(item)
            
            session.commit()
            return item
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка сохранения объявления: {e}")
            return None
        finally:
            session.close()
    
    def get_by_project(self, project_id: int) -> List[Item]:
        session = self.db.get_session()
        try:
            return session.query(Item).filter(
                Item.project_id == project_id,
                Item.is_active == True
            ).order_by(Item.created_at.desc()).all()
        finally:
            session.close()
    
    def delete(self, item_id: int) -> bool:
        session = self.db.get_session()
        try:
            item = session.query(Item).filter(Item.id == item_id).first()
            if item:
                item.is_active = False
                item.updated_at = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка удаления: {e}")
            return False
        finally:
            session.close()