"""
Insurance model
مدل بیمه
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Insurance(Base):
    """Insurance model / مدل بیمه"""
    __tablename__ = "insurances"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), unique=True, nullable=False)
    insurance_company = Column(String(255), nullable=False)  # Insurance provider / شرکت بیمه
    policy_number = Column(String(100), unique=True, nullable=False)  # Policy/member number / شماره بیمه‌نامه
    group_number = Column(String(100))  # Group number if applicable / شماره گروه در صورت وجود
    coverage_type = Column(String(100))  # e.g., "Basic", "Supplementary" / مثلا "پایه"، "تکمیلی"
    start_date = Column(Date)  # Coverage start date / تاریخ شروع پوشش
    end_date = Column(Date)  # Coverage end date / تاریخ پایان پوشش
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships / روابط
    patient = relationship("Patient", back_populates="insurance")