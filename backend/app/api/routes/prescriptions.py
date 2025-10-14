"""
Prescription management routes
مسیرهای مدیریت نسخه‌ها
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.prescription import Prescription, PrescriptionItem
from app.db.models.patient import Patient
from app.db.models.medication import Medication
from app.db.schemas.prescription import PrescriptionCreate, PrescriptionUpdate, PrescriptionResponse, PrescriptionWithPatientResponse
from app.core.security import get_current_user, get_current_secretary_or_admin
from app.utils.messages_fa import ERROR_MESSAGES, SUCCESS_MESSAGES

router = APIRouter(prefix="/prescriptions", tags=["مدیریت نسخه‌ها / Prescription Management"])


@router.post("/", response_model=PrescriptionResponse, status_code=status.HTTP_201_CREATED, summary="ایجاد نسخه جدید")
async def create_prescription(
    prescription_data: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Create new prescription (Secretary/Admin only)
    ایجاد نسخه جدید (فقط منشی/مدیر)
    """
    # Check if patient exists / بررسی وجود بیمار
    patient = db.query(Patient).filter(Patient.id == prescription_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["patient_not_found"]
        )
    
    # Verify all medications exist / بررسی وجود تمام داروها
    for item in prescription_data.items:
        medication = db.query(Medication).filter(Medication.id == item.medication_id).first()
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"دارو با شناسه {item.medication_id} یافت نشد"
            )
    
    # Create prescription / ایجاد نسخه
    new_prescription = Prescription(
        patient_id=prescription_data.patient_id,
        doctor_name=prescription_data.doctor_name,
        diagnosis=prescription_data.diagnosis,
        notes=prescription_data.notes
    )
    
    db.add(new_prescription)
    db.flush()
    
    # Create prescription items / ایجاد آیتم‌های نسخه
    for item_data in prescription_data.items:
        item = PrescriptionItem(
            prescription_id=new_prescription.id,
            **item_data.model_dump()
        )
        db.add(item)
    
    db.commit()
    db.refresh(new_prescription)
    
    # Load items with medication names / بارگذاری آیتم‌ها با نام داروها
    result = PrescriptionResponse.model_validate(new_prescription)
    for item in result.items:
        medication = db.query(Medication).filter(Medication.id == item.medication_id).first()
        item.medication_name = medication.name if medication else None
    
    return result


@router.get("/", response_model=List[PrescriptionWithPatientResponse], summary="دریافت لیست نسخه‌ها")
async def get_prescriptions(
    skip: int = 0,
    limit: int = 100,
    patient_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Get all prescriptions (Secretary/Admin only)
    دریافت تمام نسخه‌ها (فقط منشی/مدیر)
    """
    query = db.query(Prescription)
    
    if patient_id:
        query = query.filter(Prescription.patient_id == patient_id)
    
    prescriptions = query.order_by(Prescription.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for prescription in prescriptions:
        presc_dict = PrescriptionResponse.model_validate(prescription).model_dump()
        presc_dict["patient_name"] = prescription.patient.user.full_name
        
        # Add medication names / افزودن نام داروها
        for i, item in enumerate(presc_dict["items"]):
            medication = db.query(Medication).filter(Medication.id == item["medication_id"]).first()
            presc_dict["items"][i]["medication_name"] = medication.name if medication else None
        
        result.append(PrescriptionWithPatientResponse(**presc_dict))
    
    return result


@router.get("/my", response_model=List[PrescriptionResponse], summary="دریافت نسخه‌های من")
async def get_my_prescriptions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's prescriptions (Patient)
    دریافت نسخه‌های کاربر جاری (بیمار)
    """
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["patient_not_found"]
        )
    
    prescriptions = db.query(Prescription).filter(
        Prescription.patient_id == patient.id
    ).order_by(Prescription.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for prescription in prescriptions:
        presc_response = PrescriptionResponse.model_validate(prescription)
        # Add medication names / افزودن نام داروها
        for item in presc_response.items:
            medication = db.query(Medication).filter(Medication.id == item.medication_id).first()
            item.medication_name = medication.name if medication else None
        result.append(presc_response)
    
    return result


@router.get("/{prescription_id}", response_model=PrescriptionWithPatientResponse, summary="دریافت اطلاعات نسخه")
async def get_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get prescription by ID
    دریافت نسخه با شناسه
    """
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["prescription_not_found"]
        )
    
    # Check access / بررسی دسترسی
    if current_user.role == "Patient":
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient or prescription.patient_id != patient.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES["permission_denied"]
            )
    
    presc_dict = PrescriptionResponse.model_validate(prescription).model_dump()
    presc_dict["patient_name"] = prescription.patient.user.full_name
    
    # Add medication names / افزودن نام داروها
    for i, item in enumerate(presc_dict["items"]):
        medication = db.query(Medication).filter(Medication.id == item["medication_id"]).first()
        presc_dict["items"][i]["medication_name"] = medication.name if medication else None
    
    return PrescriptionWithPatientResponse(**presc_dict)


@router.put("/{prescription_id}", response_model=PrescriptionResponse, summary="بروزرسانی نسخه")
async def update_prescription(
    prescription_id: int,
    prescription_data: PrescriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Update prescription (Secretary/Admin only)
    بروزرسانی نسخه (فقط منشی/مدیر)
    """
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["prescription_not_found"]
        )
    
    # Update fields / بروزرسانی فیلدها
    update_data = prescription_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prescription, field, value)
    
    db.commit()
    db.refresh(prescription)
    
    result = PrescriptionResponse.model_validate(prescription)
    for item in result.items:
        medication = db.query(Medication).filter(Medication.id == item.medication_id).first()
        item.medication_name = medication.name if medication else None
    
    return result


@router.delete("/{prescription_id}", status_code=status.HTTP_204_NO_CONTENT, summary="حذف نسخه")
async def delete_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Delete prescription (Secretary/Admin only)
    حذف نسخه (فقط منشی/مدیر)
    """
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["prescription_not_found"]
        )
    
    db.delete(prescription)
    db.commit()
    
    return None