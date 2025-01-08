from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class AuthLogin(BaseModel):
    username_or_email: str = Field(..., min_length=1, max_length=256)
    password: str = Field(..., min_length=1, max_length=512)

class AuthProfilePassword(BaseModel):
    old_password: str = Field(..., min_length=1, max_length=512)
    new_password: str = Field(..., min_length=1, max_length=512)
    confirm_new_password: str = Field(..., min_length=1, max_length=512)

class EmailSchema(BaseModel):
    email: EmailStr = Field(..., min_length=1, max_length=256)
class ResetPassword(BaseModel):
    reset_password_token: str
    new_password: str = Field(..., min_length=1, max_length=512)
    confirm_new_password: str = Field(..., min_length=1, max_length=512)