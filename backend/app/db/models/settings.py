"""
Settings model
مدل تنظیمات
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.db.database import Base

class Setting(Base):
    """Settings model for clinic information / مدل تنظیمات برای اطلاعات کلینیک"""
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    clinic_name = Column(String(255), default="کلینیک")
    clinic_description = Column(Text)
    clinic_address = Column(Text)
    clinic_phone = Column(String(20))
    clinic_email = Column(String(255))
    working_hours = Column(String(255))  # e.g., "8:00 AM - 8:00 PM" / مثلا "8 صبح تا 8 شب"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())