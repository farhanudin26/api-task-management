from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import config

DATABASE_URL = config.DB

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False)

# Create a SessionLocal class for handling database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
