"""
Factor model
مدل فاکتور (درمان با فاکتور)
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Factor(Base):
    """Factor model for tracking factor treatments / مدل فاکتور برای پیگیری درمان‌های فاکتوری"""
    __tablename__ = "factors"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    factor_type = Column(String(100), nullable=False)  # e.g., "Factor VIII", "Factor IX" / مثلا "فاکتور 8"، "فاکتور 9"
    units_administered = Column(Integer, nullable=False)  # Units given / واحدهای تزریق شده
    administration_date = Column(DateTime, nullable=False)
    lot_number = Column(String(100))  # Batch/lot number / شماره دسته
    administered_by = Column(String(255))  # Staff name / نام پرسنل
    notes = Column(Text)
    cost = Column(Float)  # Cost of treatment / هزینه درمان
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships / روابط
    patient = relationship("Patient", back_populates="factors")