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
                              task_management_id: str = None
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
            
        if task_management_id:
            query = query.filter(TaskManagement.task_management == task_management_id)

        # Pagination
        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all() 

    
    def count_task_managements(self, user_id: str = None,task_management_id: str = None) -> int:
        query = self.db.query(TaskManagement)
        if user_id:
            query = query.filter(TaskManagement.user_id == user_id)
        
        if task_management_id:
            query = query.filter(TaskManagement.task_management == task_management_id)
            
        return query.count()
    
    def read_task_management(self, task_management_id: str):
        return self.db.query(TaskManagement).filter(TaskManagement.id == task_management_id).first()
    
    def update_task_management(self, task_management: TaskManagement):
        # Cari task berdasarkan ID
        exist_task_management = self.db.query(TaskManagement).filter(TaskManagement.id == task_management.id).first()

        if exist_task_management:
            # Perbarui data task
            exist_task_management.task_management = task_management.task_management
            exist_task_management.description = task_management.description
            exist_task_management.priority = task_management.priority
            exist_task_management.date = task_management.date

            # Simpan perubahan di database
            self.db.commit()
            return exist_task_management
        else:
            raise ValueError("TaskManagement not found")
    
    def delete_task_management(self, task_management_id: str):
        # Pastikan task_management_id adalah string atau tipe yang sesuai dengan tipe kolom id
        task_management = self.db.query(TaskManagement).filter(TaskManagement.id == task_management_id).first()

        # Jika tidak ditemukan task management, lemparkan error
        if not task_management:
            raise ValueError("TaskManagement not found")

        # Hapus task_management
        self.db.delete(task_management)
        
        try:
            self.db.commit()  # Commit perubahan
        except Exception as error:
            self.db.rollback()  # Jika terjadi error, rollback perubahan
            raise ValueError(f"Failed to delete TaskManagement: {str(error)}")

    
    def read_task_management_by_user_id(self, user_id: str):
        return self.db.query(TaskManagement).filter(TaskManagement.user_id == user_id).first() 
