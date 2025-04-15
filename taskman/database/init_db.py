"""
Database initialization script
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from taskman.config.database import db_settings
from taskman.database.connection import Base, engine
from taskman.models import Objective, Process, Task, Workflow

def create_database():
    """
    Create the database if it doesn't exist
    """
    # Create a connection without specifying the database
    temp_engine = create_engine(
        f"mysql://{db_settings.user}:{db_settings.password}@{db_settings.host}:{db_settings.port}"
    )
    
    with temp_engine.connect() as conn:
        # Create database if it doesn't exist
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_settings.database}"))
        conn.execute(text(f"USE {db_settings.database}"))
        conn.commit()

def init_db():
    """
    Initialize the database by creating all tables
    """
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except SQLAlchemyError as e:
        print(f"Error creating database tables: {e}")
        sys.exit(1)

def main():
    """
    Main function to initialize the database
    """
    print("Initializing database...")
    create_database()
    init_db()
    print("Database initialization completed successfully!")

if __name__ == "__main__":
    main() 