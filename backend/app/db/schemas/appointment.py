"""
Appointment schemas
اسکیماهای نوبت
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.db.models.appointment import AppointmentStatus


class AppointmentBase(BaseModel):
    """Base appointment schema / اسکیمای پایه نوبت"""
    appointment_date: datetime = Field(..., description="تاریخ و زمان نوبت")
    reason: Optional[str] = Field(None, description="دلیل مراجعه")
    notes: Optional[str] = Field(None, description="یادداشت‌ها")


class AppointmentCreate(AppointmentBase):
    """Schema for creating appointment / اسکیما برای ایجاد نوبت"""
    patient_id: int = Field(..., description="شناسه بیمار")


class AppointmentUpdate(BaseModel):
    """Schema for updating appointment / اسکیما برای بروزرسانی نوبت"""
    appointment_date: Optional[datetime] = None
    status: Optional[AppointmentStatus] = None
    reason: Optional[str] = None
    notes: Optional[str] = None


class AppointmentResponse(AppointmentBase):
    """Schema for appointment response / اسکیما برای پاسخ نوبت"""
    id: int
    patient_id: int
    status: AppointmentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AppointmentWithPatientResponse(AppointmentResponse):
    """Schema for appointment with patient info / اسکیما برای نوبت با اطلاعات بیمار"""
    patient_name: Optional[str] = None
    patient_phone: Optional[str] = None