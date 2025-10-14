"""
Database connection and session management
مدیریت اتصال و نشست پایگاه داده
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database engine / ایجاد موتور پایگاه داده
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Create session factory / ایجاد کارخانه نشست
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models / کلاس پایه برای مدل‌ها
Base = declarative_base()


def get_db():
    """
    Dependency to get database session
    وابستگی برای دریافت نشست پایگاه داده
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database and create tables
    مقداردهی اولیه پایگاه داده و ایجاد جداول
    """
    Base.metadata.create_all(bind=engine)