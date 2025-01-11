from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(String, primary_key=True, index=True)
    code = Column(String(36), unique=True, nullable=False)
    level = Column(Integer, nullable=False, default=0)
    name = Column(String(126), unique=True, nullable=False)
    description = Column(String(256), nullable=True)
    is_active = Column(Boolean)

    # Relasi ke User
    users = relationship('User', back_populates='role', cascade='save-update')
