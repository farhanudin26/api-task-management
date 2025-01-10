from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from dtos.auth import AuthLogin
from repositories.auth_repository import AuthRepository
from repositories.user_repository import UserRepository
from services.user_service import UserService
import jwt
from config import config  # Pastikan config diimport
from models.user import User
from jose import JWTError, jwt


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.auth_repository = AuthRepository(db)
        self.private_key = config.PRIVATE_KEY  # Gunakan PRIVATE_KEY untuk RS256
        self.access_token_expire_minutes = config.ACCESS_TOKEN_EXPIRATION
        self.refresh_token_expire_minutes = config.REFRESH_TOKEN_EXPIRATION
        self.algorithm = "RS256"  # Algoritma RS256
        
    def auth_login(self, auth_login: AuthLogin):
        user = self.user_repository.get_user_by_credential(auth_login.username_or_email)
        if not user:
            raise ValueError('Credential failed')
        
        if not user.is_active:
            raise ValueError('User is not active')
        
        user_service = UserService(self.db)
        is_password_valid = user_service.verify_password(auth_login.password, user.password)
        return self.auth_repository.auth_login(user, is_password_valid)