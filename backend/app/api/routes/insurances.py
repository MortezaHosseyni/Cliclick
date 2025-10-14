"""
Insurance management routes
مسیرهای مدیریت بیمه‌ها
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.insurance import Insurance
from app.db.models.patient import Patient
from app.db.schemas.insurance import InsuranceCreate, InsuranceUpdate, InsuranceResponse, InsuranceWithPatientResponse
from app.core.security import get_current_user, get_current_secretary_or_admin
from app.utils.messages_fa import ERROR_MESSAGES, SUCCESS_MESSAGES

router = APIRouter(prefix="/insurances", tags=["مدیریت بیمه‌ها / Insurance Management"])


@router.post("/", response_model=InsuranceResponse, status_code=status.HTTP_201_CREATED, summary="ایجاد بیمه جدید")
async def create_insurance(
    insurance_data: InsuranceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Create new insurance (Secretary/Admin only)
    ایجاد بیمه جدید (فقط منشی/مدیر)
    """
    # Check if patient exists / بررسی وجود بیمار
    patient = db.query(Patient).filter(Patient.id == insurance_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["patient_not_found"]
        )
    
    # Check if insurance already exists for this patient / بررسی وجود بیمه برای این بیمار
    existing = db.query(Insurance).filter(Insurance.patient_id == insurance_data.patient_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این بیمار قبلاً دارای بیمه است"
        )
    
    # Create new insurance / ایجاد بیمه جدید
    new_insurance = Insurance(**insurance_data.model_dump())
    
    db.add(new_insurance)
    db.commit()
    db.refresh(new_insurance)
    
    return InsuranceResponse.model_validate(new_insurance)


@router.get("/", response_model=List[InsuranceWithPatientResponse], summary="دریافت لیست بیمه‌ها")
async def get_insurances(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Get all insurances (Secretary/Admin only)
    دریافت تمام بیمه‌ها (فقط منشی/مدیر)
    """
    insurances = db.query(Insurance).offset(skip).limit(limit).all()
    
    result = []
    for insurance in insurances:
        ins_dict = InsuranceResponse.model_validate(insurance).model_dump()
        ins_dict["patient_name"] = insurance.patient.user.full_name
        result.append(InsuranceWithPatientResponse(**ins_dict))
    
    return result


@router.get("/my", response_model=InsuranceResponse, summary="دریافت بیمه من")
async def get_my_insurance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's insurance (Patient)
    دریافت بیمه کاربر جاری (بیمار)
    """
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["patient_not_found"]
        )
    
    insurance = db.query(Insurance).filter(Insurance.patient_id == patient.id).first()
    if not insurance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["insurance_not_found"]
        )
    
    return InsuranceResponse.model_validate(insurance)


@router.get("/{insurance_id}", response_model=InsuranceWithPatientResponse, summary="دریافت اطلاعات بیمه")
async def get_insurance(
    insurance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get insurance by ID
    دریافت بیمه با شناسه
    """
    insurance = db.query(Insurance).filter(Insurance.id == insurance_id).first()
    if not insurance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["insurance_not_found"]
        )
    
    # Check access / بررسی دسترسی
    if current_user.role == "Patient":
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient or insurance.patient_id != patient.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES["permission_denied"]
            )
    
    ins_dict = InsuranceResponse.model_validate(insurance).model_dump()
    ins_dict["patient_name"] = insurance.patient.user.full_name
    
    return InsuranceWithPatientResponse(**ins_dict)


@router.put("/{insurance_id}", response_model=InsuranceResponse, summary="بروزرسانی بیمه")
async def update_insurance(
    insurance_id: int,
    insurance_data: InsuranceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Update insurance (Secretary/Admin only)
    بروزرسانی بیمه (فقط منشی/مدیر)
    """
    insurance = db.query(Insurance).filter(Insurance.id == insurance_id).first()
    if not insurance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["insurance_not_found"]
        )
    
    # Update fields / بروزرسانی فیلدها
    update_data = insurance_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(insurance, field, value)
    
    db.commit()
    db.refresh(insurance)
    
    return InsuranceResponse.model_validate(insurance)


@router.delete("/{insurance_id}", status_code=status.HTTP_204_NO_CONTENT, summary="حذف بیمه")
async def delete_insurance(
    insurance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Delete insurance (Secretary/Admin only)
    حذف بیمه (فقط منشی/مدیر)
    """
    insurance = db.query(Insurance).filter(Insurance.id == insurance_id).first()
    if not insurance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["insurance_not_found"]
        )
    
    db.delete(insurance)
    db.commit()
    
    return None