from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, Text
from database import Base

class TaskManagement(Base):
    __tablename__ = "task_managements"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(ForeignKey('users.id', onupdate='CASCADE'), nullable=False)
    task_management = Column(String(256), nullable=False)
    description = Column(String(256), nullable=False)
    date = Column(DateTime, nullable=False)

    # Relasi ke User
    user = relationship('User', back_populates='task_managements')
