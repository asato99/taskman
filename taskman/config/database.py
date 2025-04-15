"""
Database configuration settings
"""
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    host: str = "localhost"
    port: int = 3306
    user: str = "kazuasato"
    password: str = "password"
    database: str = "taskman_db"

    class Config:
        """Pydantic config"""
        env_prefix = "DB_"

# Create a global instance
db_settings = DatabaseSettings() 