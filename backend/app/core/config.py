"""
Configuration Settings
تنظیمات پیکربندی سیستم
"""
from pydantic_settings import BaseSettings
from typing import List, Optional, Union


class Settings(BaseSettings):
    """Application settings / تنظیمات برنامه"""
    
    # Database
    DATABASE_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:1212",
        "http://localhost:8000",
        "http://127.0.0.1:1212",
        "http://127.0.0.1:8000"
    ]
    
    # Application
    APP_NAME: str = "Clinic Management System"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()