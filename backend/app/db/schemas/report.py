"""
Report schemas
اسکیماهای گزارش
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date


class DailyAppointmentReport(BaseModel):
    """Daily appointment report schema / اسکیمای گزارش نوبت‌های روزانه"""
    date: date
    total_appointments: int
    pending: int
    confirmed: int
    completed: int
    canceled: int


class ActivePatientReport(BaseModel):
    """Active patient report schema / اسکیمای گزارش بیماران فعال"""
    total_patients: int
    patients_with_appointments: int
    patients_with_prescriptions: int
    patients_with_factors: int


class MedicationUsageReport(BaseModel):
    """Medication usage report schema / اسکیمای گزارش مصرف دارو"""
    medication_id: int
    medication_name: str
    total_prescribed: int
    total_quantity: int


class FactorUsageReport(BaseModel):
    """Factor usage report schema / اسکیمای گزارش مصرف فاکتور"""
    patient_id: int
    patient_name: str
    factor_type: str
    total_units: int
    total_cost: float
    administration_count: int


class ReportExportRequest(BaseModel):
    """Report export request schema / اسکیمای درخواست خروجی گزارش"""
    format: str = Field(..., description="فرمت خروجی: csv یا json")
    report_type: str = Field(..., description="نوع گزارش")
    start_date: Optional[date] = Field(None, description="تاریخ شروع")
    end_date: Optional[date] = Field(None, description="تاریخ پایان")