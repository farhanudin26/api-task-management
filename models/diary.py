import uuid
from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, Text, func
from database import Base

class Diary(Base):
    __tablename__ = "diarys"

    id = Column(String, primary_key=True, index=True, default=str(uuid.uuid4()))  # Menggunakan uuid.uuid4() langsung
    user_id = Column(ForeignKey('users.id', onupdate='CASCADE'), nullable=False)
    diary = Column(Text, nullable=False)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.NOW(), nullable=False)
    updated_at = Column(DateTime, server_default=func.NOW(), onupdate=func.NOW(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)    

    # Relasi ke User
    user = relationship("User", back_populates="diarys")
