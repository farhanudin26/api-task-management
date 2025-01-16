from datetime import datetime
from sqlalchemy.orm import Session
from models.task_management import TaskManagement  
from sqlalchemy import asc, desc
from models.user import User


class TaskManagementRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def convert_datetime_to_str(self, task_management: TaskManagement) -> dict:
        """Mengonversi objek datetime menjadi string dalam format ISO 8601"""
        task_management_dict = task_management.__dict__
        for key, value in task_management_dict.items():
            if isinstance(value, datetime):
                task_management_dict[key] = value.isoformat()
        return task_management_dict

    def create_task_management(self, task_management: TaskManagement):
        task_management.priority = False
        self.db.add(task_management)
        self.db.commit()
        self.db.refresh(task_management)
        return task_management
    
    def read_task_managements(self, offset: int = None, size: int = None, sort_by: str = None, sort_order: str = 'asc',user_id: str = None,
) -> list[TaskManagement]:
        query = self.db.query(TaskManagement)
        query = query.join(User, TaskManagement.user_id == User.id)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(TaskManagement, sort_by):
                query = query.order_by(asc(getattr(TaskManagement, sort_by)))
            elif sort_order == 'desc' and hasattr(TaskManagement, sort_by):
                query = query.order_by(desc(getattr(TaskManagement, sort_by)))
                
        if user_id:
            query = query.filter(TaskManagement.user_id == user_id)

        # Pagination
        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all() 

    
    def count_task_managements(self, user_id: str = None,) -> int:
        query = self.db.query(TaskManagement)
        if user_id:
            query = query.filter(TaskManagement.user_id == user_id)
            
        return query.count()
    
    def read_task_management(self, task_management_id: str):
        return self.db.query(TaskManagement).filter(TaskManagement.id == task_management_id).first()
    
    def update_task_management(self, task_management: TaskManagement):
        self.db.commit()
        return task_management
    
    def delete_task_management(self, task_management_id: int):
        task_management = self.db.query(TaskManagement).filter(TaskManagement.id == task_management_id).first()

        if not task_management:
            raise ValueError("TaskManagement status not found")

        self.db.delete(task_management)
        self.db.commit()
    
    def read_task_management_by_user_id(self, user_id: str):
        return self.db.query(TaskManagement).filter(TaskManagement.user_id == user_id).first()
