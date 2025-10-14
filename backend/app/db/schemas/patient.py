"""
Patient schemas
اسکیماهای بیمار
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from app.db.models.patient import Gender, BloodType


class PatientBase(BaseModel):
    """Base patient schema / اسکیمای پایه بیمار"""
    national_code: Optional[str] = Field(None, min_length=10, max_length=10, description="کد ملی 10 رقمی")
    date_of_birth: Optional[date] = Field(None, description="تاریخ تولد")
    gender: Optional[Gender] = Field(None, description="جنسیت")
    blood_type: Optional[BloodType] = Field(None, description="گروه خونی")
    address: Optional[str] = Field(None, description="آدرس")
    emergency_contact: Optional[str] = Field(None, min_length=11, max_length=11, description="شماره تماس اضطراری")
    medical_history: Optional[str] = Field(None, description="سابقه پزشکی")


class PatientCreate(PatientBase):
    """Schema for creating patient / اسکیما برای ایجاد بیمار"""
    user_id: int = Field(..., description="شناسه کاربر")


class PatientUpdate(PatientBase):
    """Schema for updating patient / اسکیما برای بروزرسانی بیمار"""
    pass


class PatientResponse(PatientBase):
    """Schema for patient response / اسکیما برای پاسخ بیمار"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PatientWithUserResponse(PatientResponse):
    """Schema for patient with user info / اسکیما برای بیمار با اطلاعات کاربر"""
    user_full_name: Optional[str] = None
    user_phone: Optional[str] = None