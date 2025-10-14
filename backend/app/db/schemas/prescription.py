"""
Prescription schemas
اسکیماهای نسخه
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PrescriptionItemBase(BaseModel):
    """Base prescription item schema / اسکیمای پایه آیتم نسخه"""
    medication_id: int = Field(..., description="شناسه دارو")
    dosage: str = Field(..., description="دوز مصرف")
    duration: Optional[str] = Field(None, description="مدت زمان مصرف")
    quantity: Optional[int] = Field(None, ge=1, description="تعداد")
    instructions: Optional[str] = Field(None, description="دستورالعمل مصرف")


class PrescriptionItemCreate(PrescriptionItemBase):
    """Schema for creating prescription item / اسکیما برای ایجاد آیتم نسخه"""
    pass


class PrescriptionItemResponse(PrescriptionItemBase):
    """Schema for prescription item response / اسکیما برای پاسخ آیتم نسخه"""
    id: int
    prescription_id: int
    medication_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class PrescriptionBase(BaseModel):
    """Base prescription schema / اسکیمای پایه نسخه"""
    doctor_name: Optional[str] = Field(None, max_length=255, description="نام پزشک")
    diagnosis: Optional[str] = Field(None, description="تشخیص")
    notes: Optional[str] = Field(None, description="یادداشت‌ها")


class PrescriptionCreate(PrescriptionBase):
    """Schema for creating prescription / اسکیما برای ایجاد نسخه"""
    patient_id: int = Field(..., description="شناسه بیمار")
    items: List[PrescriptionItemCreate] = Field(..., min_length=1, description="لیست داروها")


class PrescriptionUpdate(PrescriptionBase):
    """Schema for updating prescription / اسکیما برای بروزرسانی نسخه"""
    pass


class PrescriptionResponse(PrescriptionBase):
    """Schema for prescription response / اسکیما برای پاسخ نسخه"""
    id: int
    patient_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[PrescriptionItemResponse] = []
    
    class Config:
        from_attributes = True


class PrescriptionWithPatientResponse(PrescriptionResponse):
    """Schema for prescription with patient info / اسکیما برای نسخه با اطلاعات بیمار"""
    patient_name: Optional[str] = None