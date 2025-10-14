"""
Patient management routes
مسیرهای مدیریت بیماران
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.patient import Patient
from app.db.schemas.patient import PatientCreate, PatientUpdate, PatientResponse, PatientWithUserResponse
from app.core.security import get_current_user, get_current_secretary_or_admin
from app.utils.messages_fa import ERROR_MESSAGES, SUCCESS_MESSAGES

router = APIRouter(prefix="/patients", tags=["مدیریت بیماران / Patient Management"])


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED, summary="ایجاد بیمار جدید")
async def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Create new patient (Secretary/Admin only)
    ایجاد بیمار جدید (فقط منشی/مدیر)
    """
    # Check if user exists / بررسی وجود کاربر
    user = db.query(User).filter(User.id == patient_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["user_not_found"]
        )
    
    # Check if patient already exists / بررسی وجود قبلی بیمار
    existing_patient = db.query(Patient).filter(Patient.user_id == patient_data.user_id).first()
    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این کاربر قبلاً به عنوان بیمار ثبت شده است"
        )
    
    # Create new patient / ایجاد بیمار جدید
    new_patient = Patient(**patient_data.model_dump())
    
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    
    return PatientResponse.model_validate(new_patient)


@router.get("/", response_model=List[PatientWithUserResponse], summary="دریافت لیست بیماران")
async def get_patients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Get all patients (Secretary/Admin only)
    دریافت تمام بیماران (فقط منشی/مدیر)
    """
    patients = db.query(Patient).offset(skip).limit(limit).all()
    
    result = []
    for patient in patients:
        patient_dict = PatientResponse.model_validate(patient).model_dump()
        patient_dict["user_full_name"] = patient.user.full_name
        patient_dict["user_phone"] = patient.user.phone_number
        result.append(PatientWithUserResponse(**patient_dict))
    
    return result


@router.get("/me", response_model=PatientResponse, summary="دریافت اطلاعات بیمار جاری")
async def get_my_patient_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's patient information
    دریافت اطلاعات بیمار کاربر جاری
    """
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["patient_not_found"]
        )
    
    return PatientResponse.model_validate(patient)


@router.get("/{patient_id}", response_model=PatientWithUserResponse, summary="دریافت اطلاعات بیمار")
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Get patient by ID (Secretary/Admin only)
    دریافت بیمار با شناسه (فقط منشی/مدیر)
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["patient_not_found"]
        )
    
    patient_dict = PatientResponse.model_validate(patient).model_dump()
    patient_dict["user_full_name"] = patient.user.full_name
    patient_dict["user_phone"] = patient.user.phone_number
    
    return PatientWithUserResponse(**patient_dict)


@router.put("/{patient_id}", response_model=PatientResponse, summary="بروزرسانی بیمار")
async def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Update patient (Secretary/Admin only)
    بروزرسانی بیمار (فقط منشی/مدیر)
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["patient_not_found"]
        )
    
    # Update fields / بروزرسانی فیلدها
    update_data = patient_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    db.commit()
    db.refresh(patient)
    
    return PatientResponse.model_validate(patient)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT, summary="حذف بیمار")
async def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Delete patient (Secretary/Admin only)
    حذف بیمار (فقط منشی/مدیر)
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["patient_not_found"]
        )
    
    db.delete(patient)
    db.commit()
    
    return None