import os
import uuid
import bcrypt
import pandas as pd
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from typing import List
from models.user import User
from repositories.user_repository import UserRepository
from utils.handling_file import delete_file, upload_file
from typing import Optional
# from google.cloud import vision

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.static_folder_image = "static/images/user/image"
        
    def get_password_hash(self, password: str) -> str:
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
        return hashed_password.decode('utf-8')

    def verify_password(self, plain_password, hashed_password):
        password_byte_enc = plain_password.encode('utf-8')
        hashed_password_byte_enc = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password_byte_enc)
    
    def create_user(self, user: User, image: UploadFile = None, file_extension=None):
        # Proses upload gambar jika ada
        user.image_url = upload_file(image, self.static_folder_image, file_extension, user.username) if image else ''

        # Menambahkan pengguna ke database
        user.is_active = True
        user.id = str(uuid.uuid4())        
        self.db.add(user)
        self.db.commit()  # Commit perubahan ke database
        self.db.refresh(user)  # Refresh objek untuk mendapatkan id yang di-generate oleh DB

        return user  # Mengembalikan objek user yang sudah disimpan
    
    def validation_unique_based_other_user(self, exist_user: User, user: User):
        if user.username:
            exist_username = self.user_repository.get_user_by_username(user.username)
            if exist_username and (exist_user.id != exist_username.id):
                raise ValueError('Username already used in other account')
            exist_user.username = user.username
        
        if user.email:
            exist_email = self.user_repository.get_user_by_email(user.email)
            if exist_email and (exist_user.id != exist_email.id):
                raise ValueError('Email already used in other account')
            exist_user.email = user.email

    def update_user(
            self, 
            exist_user: User, 
            user: User, 
            ):
        self.validation_unique_based_other_user(exist_user, user)
        
        if user.username:
            exist_user.username = user.username
        
        exist_user.role_id = user.role_id
        exist_user.is_active = user.is_active

        if user.password:
            exist_user.password = user.password

        return self.user_repository.update_user(exist_user)
    
    def update_user_password(self, exist_user: User, user: User):
        if user.password:
            exist_user.password = user.password

        return self.user_repository.update_user(exist_user)
    
    def delete_user(self, user_id: str):
        user = self.user_repository.read_user(user_id)
        if not user:
            raise ValueError("User not found")
        return self.user_repository.delete_user(user)
    
    def get_all_users(self, is_active: Optional[bool] = None):
        query = self.db.query(User)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        return query.all()
    
    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()
