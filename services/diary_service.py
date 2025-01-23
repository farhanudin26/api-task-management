import os
from sqlalchemy.orm import Session
from fastapi import UploadFile
from models.diary import Diary
from repositories.diary_repository import Diary, DiaryRepository
from utils.handling_file import delete_file, upload_file 


class DiaryService:
    def __init__(self, db: Session):
        self.db = db
        self.diary_repository = DiaryRepository(db)
    
    def create_diary(self, diary: Diary):
        self.db.add(diary)
        self.db.commit()
        self.db.refresh(diary)  # Pastikan ID terupdate
        return diary
    
    def update_diary(self, exist_diary: Diary, diary: Diary):
        exist_diary = self.db.query(Diary).filter(Diary.id == diary.id).first()

        if exist_diary:
            exist_diary.diary = diary.diary
            exist_diary.date = diary.date

            self.db.commit()
            return exist_diary
        else:
            raise ValueError("Diary not found")

