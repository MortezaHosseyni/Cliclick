"""
Settings schemas
اسکیماهای تنظیمات
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SettingBase(BaseModel):
    """Base setting schema / اسکیمای پایه تنظیمات"""
    clinic_name: str = Field(..., max_length=255, description="نام کلینیک")
    clinic_description: Optional[str] = Field(None, description="توضیحات کلینیک")
    clinic_address: Optional[str] = Field(None, description="آدرس کلینیک")
    clinic_phone: Optional[str] = Field(None, max_length=20, description="تلفن کلینیک")
    clinic_email: Optional[str] = Field(None, max_length=255, description="ایمیل کلینیک")
    working_hours: Optional[str] = Field(None, max_length=255, description="ساعات کاری")


class SettingCreate(SettingBase):
    """Schema for creating settings / اسکیما برای ایجاد تنظیمات"""
    pass


class SettingUpdate(BaseModel):
    """Schema for updating settings / اسکیما برای بروزرسانی تنظیمات"""
    clinic_name: Optional[str] = Field(None, max_length=255)
    clinic_description: Optional[str] = None
    clinic_address: Optional[str] = None
    clinic_phone: Optional[str] = Field(None, max_length=20)
    clinic_email: Optional[str] = Field(None, max_length=255)
    working_hours: Optional[str] = Field(None, max_length=255)


class SettingResponse(SettingBase):
    """Schema for settings response / اسکیما برای پاسخ تنظیمات"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True