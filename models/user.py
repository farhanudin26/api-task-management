import uuid
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Enum, Integer, String, DateTime, ForeignKey, Boolean, func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True,default=str(uuid.uuid4()))
    username = Column(String(36), unique=True, nullable=False)
    role_id = Column(ForeignKey('roles.id', onupdate='CASCADE'), nullable=False, index=True)
    name = Column(String(36), unique=True, nullable=False)
    email = Column(String(256), unique=True, nullable=False)
    password = Column(String(512), nullable=False)
    is_active = Column(Boolean)
    image_url = Column(String(512), unique=False, nullable=True)
    gender = Column(Enum('male', 'female'), nullable=True)  
    last_login_at = Column(DateTime, nullable=True)      
    created_at = Column(DateTime, server_default=func.NOW(), nullable=False)
    updated_at = Column(DateTime, server_default=func.NOW(), onupdate=func.NOW(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relasi ke Role
    role = relationship('Role', back_populates='users')
    task_managements = relationship("TaskManagement", back_populates="user")

    # diary = relationship('Diary', back_populates='users')
    # task_management = relationship('TaskManagement', back_populates='users')
