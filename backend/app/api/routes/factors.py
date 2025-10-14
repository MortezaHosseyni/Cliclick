"""
Factor management routes
مسیرهای مدیریت فاکتورها
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.factor import Factor
from app.db.models.patient import Patient
from app.db.schemas.factor import FactorCreate, FactorUpdate, FactorResponse, FactorWithPatientResponse
from app.core.security import get_current_user, get_current_secretary_or_admin
from app.utils.messages_fa import ERROR_MESSAGES, SUCCESS_MESSAGES

router = APIRouter(prefix="/factors", tags=["مدیریت فاکتورها / Factor Management"])


@router.post("/", response_model=FactorResponse, status_code=status.HTTP_201_CREATED, summary="ایجاد فاکتور جدید")
async def create_factor(
    factor_data: FactorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Create new factor record (Secretary/Admin only)
    ایجاد رکورد فاکتور جدید (فقط منشی/مدیر)
    """
    # Check if patient exists / بررسی وجود بیمار
    patient = db.query(Patient).filter(Patient.id == factor_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["patient_not_found"]
        )
    
    # Create new factor / ایجاد فاکتور جدید
    new_factor = Factor(**factor_data.model_dump())
    
    db.add(new_factor)
    db.commit()
    db.refresh(new_factor)
    
    return FactorResponse.model_validate(new_factor)


@router.get("/", response_model=List[FactorWithPatientResponse], summary="دریافت لیست فاکتورها")
async def get_factors(
    skip: int = 0,
    limit: int = 100,
    patient_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Get all factors (Secretary/Admin only)
    دریافت تمام فاکتورها (فقط منشی/مدیر)
    """
    query = db.query(Factor)
    
    if patient_id:
        query = query.filter(Factor.patient_id == patient_id)
    
    factors = query.order_by(Factor.administration_date.desc()).offset(skip).limit(limit).all()
    
    result = []
    for factor in factors:
        factor_dict = FactorResponse.model_validate(factor).model_dump()
        factor_dict["patient_name"] = factor.patient.user.full_name
        result.append(FactorWithPatientResponse(**factor_dict))
    
    return result


@router.get("/my", response_model=List[FactorResponse], summary="دریافت فاکتورهای من")
async def get_my_factors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's factors (Patient)
    دریافت فاکتورهای کاربر جاری (بیمار)
    """
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["patient_not_found"]
        )
    
    factors = db.query(Factor).filter(
        Factor.patient_id == patient.id
    ).order_by(Factor.administration_date.desc()).offset(skip).limit(limit).all()
    
    return [FactorResponse.model_validate(factor) for factor in factors]


@router.get("/{factor_id}", response_model=FactorWithPatientResponse, summary="دریافت اطلاعات فاکتور")
async def get_factor(
    factor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get factor by ID
    دریافت فاکتور با شناسه
    """
    factor = db.query(Factor).filter(Factor.id == factor_id).first()
    if not factor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["factor_not_found"]
        )
    
    # Check access / بررسی دسترسی
    if current_user.role == "Patient":
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient or factor.patient_id != patient.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES["permission_denied"]
            )
    
    factor_dict = FactorResponse.model_validate(factor).model_dump()
    factor_dict["patient_name"] = factor.patient.user.full_name
    
    return FactorWithPatientResponse(**factor_dict)


@router.put("/{factor_id}", response_model=FactorResponse, summary="بروزرسانی فاکتور")
async def update_factor(
    factor_id: int,
    factor_data: FactorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Update factor (Secretary/Admin only)
    بروزرسانی فاکتور (فقط منشی/مدیر)
    """
    factor = db.query(Factor).filter(Factor.id == factor_id).first()
    if not factor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["factor_not_found"]
        )
    
    # Update fields / بروزرسانی فیلدها
    update_data = factor_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(factor, field, value)
    
    db.commit()
    db.refresh(factor)
    
    return FactorResponse.model_validate(factor)


@router.delete("/{factor_id}", status_code=status.HTTP_204_NO_CONTENT, summary="حذف فاکتور")
async def delete_factor(
    factor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Delete factor (Secretary/Admin only)
    حذف فاکتور (فقط منشی/مدیر)
    """
    factor = db.query(Factor).filter(Factor.id == factor_id).first()
    if not factor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["factor_not_found"]
        )
    
    db.delete(factor)
    db.commit()
    
    return None