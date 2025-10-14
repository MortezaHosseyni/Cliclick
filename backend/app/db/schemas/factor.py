"""
Factor schemas
اسکیماهای فاکتور
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FactorBase(BaseModel):
    """Base factor schema / اسکیمای پایه فاکتور"""
    factor_type: str = Field(..., max_length=100, description="نوع فاکتور")
    units_administered: int = Field(..., gt=0, description="واحدهای تزریق شده")
    administration_date: datetime = Field(..., description="تاریخ تزریق")
    lot_number: Optional[str] = Field(None, max_length=100, description="شماره دسته")
    administered_by: Optional[str] = Field(None, max_length=255, description="تزریق شده توسط")
    notes: Optional[str] = Field(None, description="یادداشت‌ها")
    cost: Optional[float] = Field(None, ge=0, description="هزینه")


class FactorCreate(FactorBase):
    """Schema for creating factor / اسکیما برای ایجاد فاکتور"""
    patient_id: int = Field(..., description="شناسه بیمار")


class FactorUpdate(BaseModel):
    """Schema for updating factor / اسکیما برای بروزرسانی فاکتور"""
    factor_type: Optional[str] = Field(None, max_length=100)
    units_administered: Optional[int] = Field(None, gt=0)
    administration_date: Optional[datetime] = None
    lot_number: Optional[str] = Field(None, max_length=100)
    administered_by: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None
    cost: Optional[float] = Field(None, ge=0)


class FactorResponse(FactorBase):
    """Schema for factor response / اسکیما برای پاسخ فاکتور"""
    id: int
    patient_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class FactorWithPatientResponse(FactorResponse):
    """Schema for factor with patient info / اسکیما برای فاکتور با اطلاعات بیمار"""
    patient_name: Optional[str] = None