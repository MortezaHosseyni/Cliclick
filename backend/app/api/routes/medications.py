"""
Medication management routes
مسیرهای مدیریت داروها
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.medication import Medication
from app.db.schemas.medication import MedicationCreate, MedicationUpdate, MedicationResponse
from app.core.security import get_current_admin, get_current_user
from app.utils.messages_fa import ERROR_MESSAGES, SUCCESS_MESSAGES

router = APIRouter(prefix="/medications", tags=["مدیریت داروها / Medication Management"])


@router.post("/", response_model=MedicationResponse, status_code=status.HTTP_201_CREATED, summary="ایجاد دارو جدید")
async def create_medication(
    medication_data: MedicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Create new medication (Admin only)
    ایجاد دارو جدید (فقط مدیر)
    """
    # Check if medication name exists / بررسی وجود نام دارو
    existing = db.query(Medication).filter(Medication.name == medication_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES["medication_exists"]
        )
    
    # Create new medication / ایجاد دارو جدید
    new_medication = Medication(**medication_data.model_dump())
    
    db.add(new_medication)
    db.commit()
    db.refresh(new_medication)
    
    return MedicationResponse.model_validate(new_medication)


@router.get("/", response_model=List[MedicationResponse], summary="دریافت لیست داروها")
async def get_medications(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all medications
    دریافت تمام داروها
    """
    query = db.query(Medication)
    
    if search:
        query = query.filter(Medication.name.contains(search))
    
    medications = query.offset(skip).limit(limit).all()
    return [MedicationResponse.model_validate(med) for med in medications]


@router.get("/{medication_id}", response_model=MedicationResponse, summary="دریافت اطلاعات دارو")
async def get_medication(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get medication by ID
    دریافت دارو با شناسه
    """
    medication = db.query(Medication).filter(Medication.id == medication_id).first()
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["medication_not_found"]
        )
    
    return MedicationResponse.model_validate(medication)


@router.put("/{medication_id}", response_model=MedicationResponse, summary="بروزرسانی دارو")
async def update_medication(
    medication_id: int,
    medication_data: MedicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Update medication (Admin only)
    بروزرسانی دارو (فقط مدیر)
    """
    medication = db.query(Medication).filter(Medication.id == medication_id).first()
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["medication_not_found"]
        )
    
    # Update fields / بروزرسانی فیلدها
    update_data = medication_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(medication, field, value)
    
    db.commit()
    db.refresh(medication)
    
    return MedicationResponse.model_validate(medication)


@router.delete("/{medication_id}", status_code=status.HTTP_204_NO_CONTENT, summary="حذف دارو")
async def delete_medication(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Delete medication (Admin only)
    حذف دارو (فقط مدیر)
    """
    medication = db.query(Medication).filter(Medication.id == medication_id).first()
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["medication_not_found"]
        )
    
    db.delete(medication)
    db.commit()
    
    return None