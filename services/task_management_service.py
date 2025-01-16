import os
from sqlalchemy.orm import Session
from fastapi import UploadFile
from models.task_management import TaskManagement
from repositories.task_management_repository import TaskManagement, TaskManagementRepository
from utils.handling_file import delete_file, upload_file 


class TaskManagementService:
    def __init__(self, db: Session):
        self.db = db
        self.task_management_repository = TaskManagementRepository(db)
        self.static_folder_image = "static/images/task_management"
    
    def create_task_management(self, task_management: TaskManagement):
        task_management.priority = False    
        self.db.add(task_management)
        self.db.commit()
        self.db.refresh(task_management)
        return task_management
    
    def update_task_management(self, exist_task_management: TaskManagement, task_management: TaskManagement):
        exist_task_management = self.db.query(TaskManagement).filter(TaskManagement.id == task_management.id).first()

        if exist_task_management:
            exist_task_management.task_management = task_management.task_management
            exist_task_management.description = task_management.description
            exist_task_management.priority = task_management.priority
            exist_task_management.date = task_management.date


            self.db.commit()
            return exist_task_management
        else:
            raise ValueError("TaskManagement not found")

