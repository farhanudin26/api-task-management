from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, Text
from database import Base

class Diary(Base):
    __tablename__ = "diarys"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(ForeignKey('users.id', onupdate='CASCADE'), nullable=False)
    diary = Column(Text, nullable=False)
    date = Column(DateTime, nullable=False)

    # Relasi ke User
    user = relationship('User', back_populates='diarys')
