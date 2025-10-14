"""
User schemas
اسکیماهای کاربر
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from app.db.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema / اسکیمای پایه کاربر"""
    phone_number: str = Field(..., min_length=11, max_length=11, description="شماره تلفن 11 رقمی")
    full_name: str = Field(..., min_length=2, max_length=255, description="نام و نام خانوادگی")
    role: UserRole = Field(default=UserRole.PATIENT, description="نقش کاربر")


class UserCreate(UserBase):
    """Schema for creating user / اسکیما برای ایجاد کاربر"""
    password: str = Field(..., min_length=6, description="رمز عبور حداقل 6 کاراکتر")
    
    @field_validator('phone_number')
    def validate_phone(cls, v):
        if not v.startswith('09') or not v.isdigit():
            raise ValueError('شماره تلفن باید با 09 شروع شود و فقط شامل اعداد باشد')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user / اسکیما برای بروزرسانی کاربر"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response / اسکیما برای پاسخ کاربر"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Schema for login / اسکیما برای ورود"""
    phone_number: str = Field(..., description="شماره تلفن")
    password: str = Field(..., description="رمز عبور")


class TokenResponse(BaseModel):
    """Schema for token response / اسکیما برای پاسخ توکن"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse