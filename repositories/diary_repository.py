from datetime import datetime
from sqlalchemy.orm import Session
from models.diary import Diary  
from sqlalchemy import asc, desc
from models.user import User


class DiaryRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def convert_datetime_to_str(self, diary: Diary) -> dict:
        """Mengonversi objek datetime menjadi string dalam format ISO 8601"""
        diary_dict = diary.__dict__
        for key, value in diary_dict.items():
            if isinstance(value, datetime):
                diary_dict[key] = value.isoformat()
        return diary_dict

    def create_diary(self, diary: Diary):
        self.db.add(diary)
        self.db.commit()
        self.db.refresh(diary)
        return diary
    
    def read_diarys(self, offset: int = None, size: int = None, sort_by: str = None, sort_order: str = 'asc',user_id: str = None,
                              diary_id: str = None
) -> list[Diary]:
        query = self.db.query(Diary)
        query = query.join(User, Diary.user_id == User.id)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(Diary, sort_by):
                query = query.order_by(asc(getattr(Diary, sort_by)))
            elif sort_order == 'desc' and hasattr(Diary, sort_by):
                query = query.order_by(desc(getattr(Diary, sort_by)))
                
        if user_id:
            query = query.filter(Diary.user_id == user_id)
            
        if diary_id:
            query = query.filter(Diary.diary == diary_id)

        # Pagination
        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all() 

    
    def count_diarys(self, user_id: str = None,diary_id: str = None) -> int:
        query = self.db.query(Diary)
        if user_id:
            query = query.filter(Diary.user_id == user_id)
        
        if diary_id:
            query = query.filter(Diary.diary == diary_id)
            
        return query.count()
    
    def read_diary(self, diary_id: str):
        return self.db.query(Diary).filter(Diary.id == diary_id).first()
    
    def update_diary(self, diary: Diary):
        # Cari task berdasarkan ID
        exist_diary = self.db.query(Diary).filter(Diary.id == diary.id).first()

        if exist_diary:
            # Perbarui data task
            exist_diary.diary = diary.diary
            exist_diary.date = diary.date

            # Simpan perubahan di database
            self.db.commit()
            return exist_diary
        else:
            raise ValueError("Diary not found")
    
    def delete_diary(self, diary_id: str):
        # Pastikan diary_id adalah string atau tipe yang sesuai dengan tipe kolom id
        diary = self.db.query(Diary).filter(Diary.id == diary_id).first()

        # Jika tidak ditemukan task management, lemparkan error
        if not diary:
            raise ValueError("Diary not found")

        # Hapus diary
        self.db.delete(diary)
        
        try:
            self.db.commit()  # Commit perubahan
        except Exception as error:
            self.db.rollback()  # Jika terjadi error, rollback perubahan
            raise ValueError(f"Failed to delete Diary: {str(error)}")

    
    def read_diary_by_user_id(self, user_id: str):
        return self.db.query(Diary).filter(Diary.user_id == user_id).first()
