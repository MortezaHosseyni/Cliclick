"""
Patient model
مدل بیمار
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class Gender(str, enum.Enum):
    """Gender options / جنسیت"""
    MALE = "Male"
    FEMALE = "Female"


class BloodType(str, enum.Enum):
    """Blood type options / گروه خونی"""
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"


class Patient(Base):
    """Patient model / مدل بیمار"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    national_code = Column(String(10), unique=True, index=True)
    date_of_birth = Column(Date)
    gender = Column(Enum(Gender))
    blood_type = Column(Enum(BloodType))
    address = Column(Text)
    emergency_contact = Column(String(11))
    medical_history = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships / روابط
    user = relationship("User", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    prescriptions = relationship("Prescription", back_populates="patient", cascade="all, delete-orphan")
    factors = relationship("Factor", back_populates="patient", cascade="all, delete-orphan")
    insurance = relationship("Insurance", back_populates="patient", uselist=False, cascade="all, delete-orphan")