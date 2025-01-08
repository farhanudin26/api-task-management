from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String(36), unique=True, nullable=False)
    name = Column(String(36), unique=True, nullable=False)
    email = Column(String(256), unique=True, nullable=False)
    password = Column(String(512), nullable=False)
    is_active = Column(Boolean)
    created_at = Column(DateTime, server_default=func.NOW(), nullable=False)
    updated_at = Column(DateTime, server_default=func.NOW(), onupdate=func.NOW(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relasi ke Role
    role = relationship("Role", back_populates="User") 
    diary = relationship('Diary', back_populates='user')
    task_management = relationship('TaskManagement', back_populates='user')
