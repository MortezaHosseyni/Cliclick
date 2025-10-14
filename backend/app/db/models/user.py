"""
User model
مدل کاربر
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class UserRole(str, enum.Enum):
    """User roles / نقش‌های کاربر"""
    ADMIN = "Admin"
    SECRETARY = "Secretary"
    PATIENT = "Patient"


class User(Base):
    """User model / مدل کاربر"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(11), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.PATIENT, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships / روابط
    patient = relationship("Patient", back_populates="user", uselist=False, cascade="all, delete-orphan")
    support_chats = relationship("SupportChat", back_populates="patient_user", cascade="all, delete-orphan")