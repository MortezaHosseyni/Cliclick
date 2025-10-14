"""
Appointment management routes
مسیرهای مدیریت نوبت‌ها
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.appointment import Appointment, AppointmentStatus
from app.db.models.patient import Patient
from app.db.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse, AppointmentWithPatientResponse
from app.core.security import get_current_user, get_current_secretary_or_admin
from app.utils.messages_fa import ERROR_MESSAGES, SUCCESS_MESSAGES

router = APIRouter(prefix="/appointments", tags=["مدیریت نوبت‌ها / Appointment Management"])


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED, summary="ایجاد نوبت جدید")
async def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Create new appointment (Secretary/Admin only)
    ایجاد نوبت جدید (فقط منشی/مدیر)
    """
    # Check if patient exists / بررسی وجود بیمار
    patient = db.query(Patient).filter(Patient.id == appointment_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["patient_not_found"]
        )
    
    # Check for conflicting appointments (within 30 minutes) / بررسی تداخل نوبت‌ها
    time_range_start = appointment_data.appointment_date - timedelta(minutes=30)
    time_range_end = appointment_data.appointment_date + timedelta(minutes=30)
    
    conflicting = db.query(Appointment).filter(
        Appointment.appointment_date.between(time_range_start, time_range_end),
        Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
    ).first()
    
    if conflicting:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES["appointment_conflict"]
        )
    
    # Create new appointment / ایجاد نوبت جدید
    new_appointment = Appointment(**appointment_data.model_dump())
    
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    
    return AppointmentResponse.model_validate(new_appointment)


@router.get("/", response_model=List[AppointmentWithPatientResponse], summary="دریافت لیست نوبت‌ها")
async def get_appointments(
    skip: int = 0,
    limit: int = 100,
    status_filter: AppointmentStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Get all appointments (Secretary/Admin only)
    دریافت تمام نوبت‌ها (فقط منشی/مدیر)
    """
    query = db.query(Appointment)
    
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    
    appointments = query.order_by(Appointment.appointment_date.desc()).offset(skip).limit(limit).all()
    
    result = []
    for appointment in appointments:
        appt_dict = AppointmentResponse.model_validate(appointment).model_dump()
        appt_dict["patient_name"] = appointment.patient.user.full_name
        appt_dict["patient_phone"] = appointment.patient.user.phone_number
        result.append(AppointmentWithPatientResponse(**appt_dict))
    
    return result


@router.get("/my", response_model=List[AppointmentResponse], summary="دریافت نوبت‌های من")
async def get_my_appointments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's appointments (Patient)
    دریافت نوبت‌های کاربر جاری (بیمار)
    """
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["patient_not_found"]
        )
    
    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient.id
    ).order_by(Appointment.appointment_date.desc()).offset(skip).limit(limit).all()
    
    return [AppointmentResponse.model_validate(appt) for appt in appointments]


@router.get("/{appointment_id}", response_model=AppointmentWithPatientResponse, summary="دریافت اطلاعات نوبت")
async def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Get appointment by ID (Secretary/Admin only)
    دریافت نوبت با شناسه (فقط منشی/مدیر)
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["appointment_not_found"]
        )
    
    appt_dict = AppointmentResponse.model_validate(appointment).model_dump()
    appt_dict["patient_name"] = appointment.patient.user.full_name
    appt_dict["patient_phone"] = appointment.patient.user.phone_number
    
    return AppointmentWithPatientResponse(**appt_dict)


@router.put("/{appointment_id}", response_model=AppointmentResponse, summary="بروزرسانی نوبت")
async def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Update appointment (Secretary/Admin only)
    بروزرسانی نوبت (فقط منشی/مدیر)
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["appointment_not_found"]
        )
    
    # Update fields / بروزرسانی فیلدها
    update_data = appointment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(appointment, field, value)
    
    db.commit()
    db.refresh(appointment)
    
    return AppointmentResponse.model_validate(appointment)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="حذف نوبت")
async def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Delete appointment (Secretary/Admin only)
    حذف نوبت (فقط منشی/مدیر)
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["appointment_not_found"]
        )
    
    db.delete(appointment)
    db.commit()
    
    return None