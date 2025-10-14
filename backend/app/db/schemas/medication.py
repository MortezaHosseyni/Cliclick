"""
Medication schemas
اسکیماهای دارو
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MedicationBase(BaseModel):
    """Base medication schema / اسکیمای پایه دارو"""
    name: str = Field(..., min_length=1, max_length=255, description="نام دارو")
    generic_name: Optional[str] = Field(None, max_length=255, description="نام ژنریک")
    manufacturer: Optional[str] = Field(None, max_length=255, description="تولیدکننده")
    dosage_form: Optional[str] = Field(None, max_length=100, description="شکل دارویی")
    strength: Optional[str] = Field(None, max_length=50, description="قدرت دارو")
    unit_price: Optional[float] = Field(None, ge=0, description="قیمت واحد")
    stock_quantity: Optional[int] = Field(0, ge=0, description="موجودی انبار")
    description: Optional[str] = Field(None, description="توضیحات")


class MedicationCreate(MedicationBase):
    """Schema for creating medication / اسکیما برای ایجاد دارو"""
    pass


class MedicationUpdate(BaseModel):
    """Schema for updating medication / اسکیما برای بروزرسانی دارو"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    generic_name: Optional[str] = Field(None, max_length=255)
    manufacturer: Optional[str] = Field(None, max_length=255)
    dosage_form: Optional[str] = Field(None, max_length=100)
    strength: Optional[str] = Field(None, max_length=50)
    unit_price: Optional[float] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None


class MedicationResponse(MedicationBase):
    """Schema for medication response / اسکیما برای پاسخ دارو"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True