"""
Database connection setup
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.declarative import declared_attr

from taskman.config.database import db_settings

# DBへの接続設定
DATABASE_URL = os.environ.get("DATABASE_URL") or f"mysql://{db_settings.user}:{db_settings.password}@{db_settings.host}:{db_settings.port}/{db_settings.database}"

# エンジン作成
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# セッションファクトリを作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Baseクラスを作成 - これを継承して各モデルを定義する
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