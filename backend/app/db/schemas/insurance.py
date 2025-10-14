"""
Insurance schemas
اسکیماهای بیمه
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class InsuranceBase(BaseModel):
    """Base insurance schema / اسکیمای پایه بیمه"""
    insurance_company: str = Field(..., max_length=255, description="شرکت بیمه")
    policy_number: str = Field(..., max_length=100, description="شماره بیمه‌نامه")
    group_number: Optional[str] = Field(None, max_length=100, description="شماره گروه")
    coverage_type: Optional[str] = Field(None, max_length=100, description="نوع پوشش")
    start_date: Optional[date] = Field(None, description="تاریخ شروع")
    end_date: Optional[date] = Field(None, description="تاریخ پایان")


class InsuranceCreate(InsuranceBase):
    """Schema for creating insurance / اسکیما برای ایجاد بیمه"""
    patient_id: int = Field(..., description="شناسه بیمار")


class InsuranceUpdate(BaseModel):
    """Schema for updating insurance / اسکیما برای بروزرسانی بیمه"""
    insurance_company: Optional[str] = Field(None, max_length=255)
    policy_number: Optional[str] = Field(None, max_length=100)
    group_number: Optional[str] = Field(None, max_length=100)
    coverage_type: Optional[str] = Field(None, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class InsuranceResponse(InsuranceBase):
    """Schema for insurance response / اسکیما برای پاسخ بیمه"""
    id: int
    patient_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class InsuranceWithPatientResponse(InsuranceResponse):
    """Schema for insurance with patient info / اسکیما برای بیمه با اطلاعات بیمار"""
    patient_name: Optional[str] = None