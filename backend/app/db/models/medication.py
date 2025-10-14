"""
Medication model
مدل دارو
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Medication(Base):
    """Medication model / مدل دارو"""
    __tablename__ = "medications"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    generic_name = Column(String(255))
    manufacturer = Column(String(255))
    dosage_form = Column(String(100))  # Tablet, Capsule, Syrup, etc. / قرص، کپسول، شربت و غیره
    strength = Column(String(50))  # e.g., "500mg" / مثلا "500 میلی‌گرم"
    unit_price = Column(Float)
    stock_quantity = Column(Integer, default=0)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships / روابط
    prescription_items = relationship("PrescriptionItem", back_populates="medication")