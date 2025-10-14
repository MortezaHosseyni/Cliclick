"""
Support schemas
اسکیماهای پشتیبانی
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SupportMessageBase(BaseModel):
    """Base support message schema / اسکیمای پایه پیام پشتیبانی"""
    message: str = Field(..., min_length=1, description="متن پیام")


class SupportMessageCreate(SupportMessageBase):
    """Schema for creating support message / اسکیما برای ایجاد پیام پشتیبانی"""
    chat_id: int = Field(..., description="شناسه گفتگو")


class SupportMessageResponse(SupportMessageBase):
    """Schema for support message response / اسکیما برای پاسخ پیام پشتیبانی"""
    id: int
    chat_id: int
    sender_user_id: int
    is_read: bool
    created_at: datetime
    sender_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class SupportChatBase(BaseModel):
    """Base support chat schema / اسکیمای پایه گفتگوی پشتیبانی"""
    subject: Optional[str] = Field(None, max_length=255, description="موضوع گفتگو")


class SupportChatCreate(SupportChatBase):
    """Schema for creating support chat / اسکیما برای ایجاد گفتگوی پشتیبانی"""
    pass


class SupportChatResponse(SupportChatBase):
    """Schema for support chat response / اسکیما برای پاسخ گفتگوی پشتیبانی"""
    id: int
    patient_user_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    patient_name: Optional[str] = None
    messages: List[SupportMessageResponse] = []
    
    class Config:
        from_attributes = True