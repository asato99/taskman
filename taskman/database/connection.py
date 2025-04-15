"""
Database connection utilities
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from taskman.config.database import db_settings

# Create database URL
DATABASE_URL = f"mysql://{db_settings.user}:{db_settings.password}@{db_settings.host}:{db_settings.port}/{db_settings.database}"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """
    Get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 