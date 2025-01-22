import uuid
from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, ForeignKey, String, Boolean, func
from database import Base

class TaskManagement(Base):
    __tablename__ = "task_managements"

    id = Column(String, primary_key=True, index=True, default=str(uuid.uuid4()))  # Menggunakan uuid.uuid4() langsung
    user_id = Column(ForeignKey('users.id', onupdate='CASCADE'), nullable=False)
    task_management = Column(String(256), nullable=False)
    description = Column(String(256), nullable=True)  # Tidak wajib diisi
    date = Column(DateTime, nullable=False)
    priority = Column(Boolean, default=False)  # Nilai default
    created_at = Column(DateTime, server_default=func.NOW(), nullable=False)
    updated_at = Column(DateTime, server_default=func.NOW(), onupdate=func.NOW(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relasi ke User
    user = relationship("User", back_populates="task_managements")
