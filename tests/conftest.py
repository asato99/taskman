"""
Pytest configuration file
"""
import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# プロジェクトのルートディレクトリをPythonパスに追加
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# この修正後にimport
from taskman.database.connection import Base

# テスト用のインメモリSQLiteデータベースを設定
TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    """テスト用のデータベースエンジンを作成"""
    return create_engine(TEST_DB_URL)


@pytest.fixture(scope="session")
def session_factory(engine):
    """テスト用のセッションファクトリを作成"""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session(engine, session_factory):
    """テストごとに新しいセッションを作成"""
    Base.metadata.create_all(bind=engine)
    session = session_factory()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


# 結合テスト用の一時データベースパス
@pytest.fixture(scope="function")
def temp_db_path():
    """テスト用の一時データベースファイルパスを返す"""
    import tempfile
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    db_url = f"sqlite:///{path}"
    yield db_url
    # テスト後にファイルを削除
    os.unlink(path)


# 統合テスト用のDBフィクスチャ
@pytest.fixture(scope="function")
def test_db(monkeypatch):
    """
    統合テスト用の一時データベースを設定する
    
    このフィクスチャは以下を行います：
    1. 一時的なSQLiteデータベースファイルを作成
    2. データベース接続設定を一時ファイルに向ける
    3. テスト後にデータベースをクリーンアップ
    """
    import tempfile
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from taskman.database.connection import Base
    
    # 一時データベースファイルを作成
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    db_url = f"sqlite:///{path}"
    
    # データベースエンジンとセッションを作成
    test_engine = create_engine(db_url)
    test_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    # テーブルを作成
    Base.metadata.create_all(bind=test_engine)
    
    # 環境変数をパッチして一時DBを使用
    monkeypatch.setenv("DATABASE_URL", db_url)
    
    # データベース接続関数をモンキーパッチ
    original_engine = __import__('taskman.database.connection', fromlist=['engine']).engine
    original_session_local = __import__('taskman.database.connection', fromlist=['SessionLocal']).SessionLocal
    
    __import__('taskman.database.connection', fromlist=['engine']).engine = test_engine
    __import__('taskman.database.connection', fromlist=['SessionLocal']).SessionLocal = test_session_factory
    
    # フィクスチャを提供
    yield
    
    # クリーンアップ - 元の設定に戻す
    __import__('taskman.database.connection', fromlist=['engine']).engine = original_engine
    __import__('taskman.database.connection', fromlist=['SessionLocal']).SessionLocal = original_session_local
    
    # データベースファイルを削除
    try:
        os.unlink(path)
    except OSError:
        pass 