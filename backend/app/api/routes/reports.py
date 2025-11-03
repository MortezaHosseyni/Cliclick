"""
Advanced Reports routes
مسیرهای گزارشات پیشرفته
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from typing import List, Optional
from datetime import date, datetime, timedelta
import csv
import io
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.appointment import Appointment, AppointmentStatus
from app.db.models.patient import Patient
from app.db.models.prescription import Prescription, PrescriptionItem
from app.db.models.medication import Medication
from app.db.models.factor import Factor
from app.db.models.insurance import Insurance
from app.core.security import get_current_admin, get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/reports/advanced", tags=["گزارشات پیشرفته / Advanced Reports"])


# Pydantic schemas for advanced reports
class PatientDetailReport(BaseModel):
    patient_id: int
    full_name: str
    phone_number: str
    national_code: Optional[str]
    gender: Optional[str]
    blood_type: Optional[str]
    age: Optional[int]
    total_appointments: int
    completed_appointments: int
    canceled_appointments: int
    total_prescriptions: int
    total_medications: int
    total_factors: int
    total_factor_units: int
    total_factor_cost: float
    has_insurance: bool
    insurance_company: Optional[str]
    last_appointment_date: Optional[datetime]
    last_prescription_date: Optional[datetime]
    last_factor_date: Optional[datetime]


class FactorDetailReport(BaseModel):
    factor_id: int
    patient_id: int
    patient_name: str
    patient_phone: str
    factor_type: str
    units_administered: int
    administration_date: datetime
    lot_number: Optional[str]
    administered_by: Optional[str]
    cost: Optional[float]
    notes: Optional[str]


class SinglePatientReport(BaseModel):
    # Basic info
    patient_id: int
    full_name: str
    phone_number: str
    national_code: Optional[str]
    date_of_birth: Optional[date]
    age: Optional[int]
    gender: Optional[str]
    blood_type: Optional[str]
    address: Optional[str]
    emergency_contact: Optional[str]
    medical_history: Optional[str]
    
    # Insurance info
    has_insurance: bool
    insurance_company: Optional[str]
    policy_number: Optional[str]
    coverage_type: Optional[str]
    
    # Appointment summary
    total_appointments: int
    pending_appointments: int
    confirmed_appointments: int
    completed_appointments: int
    canceled_appointments: int
    upcoming_appointments: List[dict]
    
    # Prescription summary
    total_prescriptions: int
    unique_medications: int
    recent_prescriptions: List[dict]
    
    # Factor treatment summary
    total_factor_administrations: int
    total_factor_units: int
    total_factor_cost: float
    recent_factors: List[dict]


class PrescriptionDetailReport(BaseModel):
    prescription_id: int
    patient_id: int
    patient_name: str
    patient_phone: str
    doctor_name: Optional[str]
    diagnosis: Optional[str]
    created_at: datetime
    total_medications: int
    medications: List[dict]


class AppointmentDetailReport(BaseModel):
    appointment_id: int
    patient_id: int
    patient_name: str
    patient_phone: str
    appointment_date: datetime
    status: str
    reason: Optional[str]
    notes: Optional[str]
    created_at: datetime


@router.get("/patients", response_model=List[PatientDetailReport], 
            summary="گزارش تفصیلی بیماران")
async def get_detailed_patients_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    has_insurance: Optional[bool] = None,
    min_appointments: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Get detailed report of all patients with their activities (Admin only)
    گزارش تفصیلی تمام بیماران با فعالیت‌هایشان (فقط مدیر)
    """
    # Build base query
    patients = db.query(Patient).join(User).all()
    
    results = []
    for patient in patients:
        # Calculate age
        age = None
        if patient.date_of_birth:
            today = date.today()
            age = today.year - patient.date_of_birth.year - (
                (today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day)
            )
        
        # Get appointment stats
        appointments_query = db.query(Appointment).filter(Appointment.patient_id == patient.id)
        if start_date:
            appointments_query = appointments_query.filter(
                Appointment.appointment_date >= datetime.combine(start_date, datetime.min.time())
            )
        if end_date:
            appointments_query = appointments_query.filter(
                Appointment.appointment_date <= datetime.combine(end_date, datetime.max.time())
            )
        
        total_appointments = appointments_query.count()
        completed = appointments_query.filter(Appointment.status == AppointmentStatus.COMPLETED).count()
        canceled = appointments_query.filter(Appointment.status == AppointmentStatus.CANCELED).count()
        
        # Skip if min_appointments filter doesn't match
        if min_appointments and total_appointments < min_appointments:
            continue
        
        # Get prescription stats
        prescriptions = db.query(Prescription).filter(Prescription.patient_id == patient.id)
        if start_date:
            prescriptions = prescriptions.filter(
                Prescription.created_at >= datetime.combine(start_date, datetime.min.time())
            )
        if end_date:
            prescriptions = prescriptions.filter(
                Prescription.created_at <= datetime.combine(end_date, datetime.max.time())
            )
        
        total_prescriptions = prescriptions.count()
        total_medications = db.query(func.count(PrescriptionItem.id)).join(
            Prescription
        ).filter(Prescription.patient_id == patient.id).scalar() or 0
        
        # Get factor stats
        factors_query = db.query(Factor).filter(Factor.patient_id == patient.id)
        if start_date:
            factors_query = factors_query.filter(
                Factor.administration_date >= datetime.combine(start_date, datetime.min.time())
            )
        if end_date:
            factors_query = factors_query.filter(
                Factor.administration_date <= datetime.combine(end_date, datetime.max.time())
            )
        
        total_factors = factors_query.count()
        total_units = db.query(func.sum(Factor.units_administered)).filter(
            Factor.patient_id == patient.id
        ).scalar() or 0
        total_cost = db.query(func.sum(Factor.cost)).filter(
            Factor.patient_id == patient.id
        ).scalar() or 0.0
        
        # Get insurance info
        insurance = db.query(Insurance).filter(Insurance.patient_id == patient.id).first()
        has_ins = insurance is not None
        
        # Skip if insurance filter doesn't match
        if has_insurance is not None and has_ins != has_insurance:
            continue
        
        # Get last dates
        last_appointment = db.query(Appointment.appointment_date).filter(
            Appointment.patient_id == patient.id
        ).order_by(desc(Appointment.appointment_date)).first()
        
        last_prescription = db.query(Prescription.created_at).filter(
            Prescription.patient_id == patient.id
        ).order_by(desc(Prescription.created_at)).first()
        
        last_factor = db.query(Factor.administration_date).filter(
            Factor.patient_id == patient.id
        ).order_by(desc(Factor.administration_date)).first()
        
        results.append(PatientDetailReport(
            patient_id=patient.id,
            full_name=patient.user.full_name,
            phone_number=patient.user.phone_number,
            national_code=patient.national_code,
            gender=patient.gender.value if patient.gender else None,
            blood_type=patient.blood_type.value if patient.blood_type else None,
            age=age,
            total_appointments=total_appointments,
            completed_appointments=completed,
            canceled_appointments=canceled,
            total_prescriptions=total_prescriptions,
            total_medications=total_medications,
            total_factors=total_factors,
            total_factor_units=int(total_units),
            total_factor_cost=float(total_cost),
            has_insurance=has_ins,
            insurance_company=insurance.insurance_company if insurance else None,
            last_appointment_date=last_appointment[0] if last_appointment else None,
            last_prescription_date=last_prescription[0] if last_prescription else None,
            last_factor_date=last_factor[0] if last_factor else None
        ))
    
    return results


@router.get("/factors", response_model=List[FactorDetailReport],
            summary="گزارش تفصیلی فاکتورها")
async def get_detailed_factors_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    factor_type: Optional[str] = None,
    patient_id: Optional[int] = None,
    min_units: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Get detailed report of all factor administrations (Admin only)
    گزارش تفصیلی تمام تزریقات فاکتور (فقط مدیر)
    """
    # Set default dates
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=180)  # Last 6 months
    
    # Build query
    query = db.query(Factor).join(Patient).join(User).filter(
        and_(
            Factor.administration_date >= datetime.combine(start_date, datetime.min.time()),
            Factor.administration_date <= datetime.combine(end_date, datetime.max.time())
        )
    )
    
    if factor_type:
        query = query.filter(Factor.factor_type.ilike(f"%{factor_type}%"))
    
    if patient_id:
        query = query.filter(Factor.patient_id == patient_id)
    
    if min_units:
        query = query.filter(Factor.units_administered >= min_units)
    
    factors = query.order_by(desc(Factor.administration_date)).all()
    
    results = []
    for factor in factors:
        results.append(FactorDetailReport(
            factor_id=factor.id,
            patient_id=factor.patient_id,
            patient_name=factor.patient.user.full_name,
            patient_phone=factor.patient.user.phone_number,
            factor_type=factor.factor_type,
            units_administered=factor.units_administered,
            administration_date=factor.administration_date,
            lot_number=factor.lot_number,
            administered_by=factor.administered_by,
            cost=factor.cost,
            notes=factor.notes
        ))
    
    return results


@router.get("/patient/{patient_id}", response_model=SinglePatientReport,
            summary="گزارش کامل یک بیمار")
async def get_single_patient_report(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive report for a single patient
    گزارش جامع برای یک بیمار
    
    Patients can only access their own report, admins can access any
    بیماران فقط می‌توانند گزارش خود را ببینند، ادمین‌ها می‌توانند هر گزارشی را ببینند
    """
    # Get patient
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="بیمار یافت نشد")
    
    # Check permissions
    if current_user.role.value == "Patient" and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="شما مجاز به مشاهده این گزارش نیستید")
    
    # Calculate age
    age = None
    if patient.date_of_birth:
        today = date.today()
        age = today.year - patient.date_of_birth.year - (
            (today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day)
        )
    
    # Get insurance info
    insurance = db.query(Insurance).filter(Insurance.patient_id == patient.id).first()
    
    # Get appointment stats
    appointments = db.query(Appointment).filter(Appointment.patient_id == patient.id)
    total_appts = appointments.count()
    pending = appointments.filter(Appointment.status == AppointmentStatus.PENDING).count()
    confirmed = appointments.filter(Appointment.status == AppointmentStatus.CONFIRMED).count()
    completed = appointments.filter(Appointment.status == AppointmentStatus.COMPLETED).count()
    canceled = appointments.filter(Appointment.status == AppointmentStatus.CANCELED).count()
    
    # Get upcoming appointments
    upcoming = db.query(Appointment).filter(
        and_(
            Appointment.patient_id == patient.id,
            Appointment.appointment_date >= datetime.now(),
            Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
        )
    ).order_by(Appointment.appointment_date).limit(5).all()
    
    upcoming_list = [
        {
            "appointment_id": apt.id,
            "date": apt.appointment_date,
            "status": apt.status.value,
            "reason": apt.reason
        }
        for apt in upcoming
    ]
    
    # Get prescription stats
    prescriptions = db.query(Prescription).filter(Prescription.patient_id == patient.id)
    total_prescriptions = prescriptions.count()
    
    unique_meds = db.query(func.count(func.distinct(PrescriptionItem.medication_id))).join(
        Prescription
    ).filter(Prescription.patient_id == patient.id).scalar() or 0
    
    # Get recent prescriptions
    recent_presc = prescriptions.order_by(desc(Prescription.created_at)).limit(5).all()
    recent_presc_list = []
    for presc in recent_presc:
        items = db.query(PrescriptionItem).filter(
            PrescriptionItem.prescription_id == presc.id
        ).join(Medication).all()
        
        recent_presc_list.append({
            "prescription_id": presc.id,
            "created_at": presc.created_at,
            "doctor_name": presc.doctor_name,
            "diagnosis": presc.diagnosis,
            "medications": [
                {
                    "name": item.medication.name,
                    "dosage": item.dosage,
                    "duration": item.duration,
                    "quantity": item.quantity
                }
                for item in items
            ]
        })
    
    # Get factor stats
    factors = db.query(Factor).filter(Factor.patient_id == patient.id)
    total_factors = factors.count()
    total_units = db.query(func.sum(Factor.units_administered)).filter(
        Factor.patient_id == patient.id
    ).scalar() or 0
    total_cost = db.query(func.sum(Factor.cost)).filter(
        Factor.patient_id == patient.id
    ).scalar() or 0.0
    
    # Get recent factors
    recent_factors = factors.order_by(desc(Factor.administration_date)).limit(5).all()
    recent_factors_list = [
        {
            "factor_id": f.id,
            "factor_type": f.factor_type,
            "units": f.units_administered,
            "date": f.administration_date,
            "administered_by": f.administered_by,
            "cost": f.cost
        }
        for f in recent_factors
    ]
    
    return SinglePatientReport(
        patient_id=patient.id,
        full_name=patient.user.full_name,
        phone_number=patient.user.phone_number,
        national_code=patient.national_code,
        date_of_birth=patient.date_of_birth,
        age=age,
        gender=patient.gender.value if patient.gender else None,
        blood_type=patient.blood_type.value if patient.blood_type else None,
        address=patient.address,
        emergency_contact=patient.emergency_contact,
        medical_history=patient.medical_history,
        has_insurance=insurance is not None,
        insurance_company=insurance.insurance_company if insurance else None,
        policy_number=insurance.policy_number if insurance else None,
        coverage_type=insurance.coverage_type if insurance else None,
        total_appointments=total_appts,
        pending_appointments=pending,
        confirmed_appointments=confirmed,
        completed_appointments=completed,
        canceled_appointments=canceled,
        upcoming_appointments=upcoming_list,
        total_prescriptions=total_prescriptions,
        unique_medications=unique_meds,
        recent_prescriptions=recent_presc_list,
        total_factor_administrations=total_factors,
        total_factor_units=int(total_units),
        total_factor_cost=float(total_cost),
        recent_factors=recent_factors_list
    )


@router.get("/prescriptions", response_model=List[PrescriptionDetailReport],
            summary="گزارش تفصیلی نسخه‌ها")
async def get_detailed_prescriptions_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    patient_id: Optional[int] = None,
    medication_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Get detailed report of all prescriptions (Admin only)
    گزارش تفصیلی تمام نسخه‌ها (فقط مدیر)
    """
    # Set default dates
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=90)
    
    # Build query
    query = db.query(Prescription).join(Patient).join(User).filter(
        and_(
            Prescription.created_at >= datetime.combine(start_date, datetime.min.time()),
            Prescription.created_at <= datetime.combine(end_date, datetime.max.time())
        )
    )
    
    if patient_id:
        query = query.filter(Prescription.patient_id == patient_id)
    
    prescriptions = query.order_by(desc(Prescription.created_at)).all()
    
    results = []
    for presc in prescriptions:
        # Get prescription items
        items = db.query(PrescriptionItem).filter(
            PrescriptionItem.prescription_id == presc.id
        ).join(Medication).all()
        
        # Filter by medication name if provided
        if medication_name:
            items = [item for item in items if medication_name.lower() in item.medication.name.lower()]
            if not items:
                continue
        
        medications_list = [
            {
                "medication_name": item.medication.name,
                "dosage": item.dosage,
                "duration": item.duration,
                "quantity": item.quantity,
                "instructions": item.instructions
            }
            for item in items
        ]
        
        results.append(PrescriptionDetailReport(
            prescription_id=presc.id,
            patient_id=presc.patient_id,
            patient_name=presc.patient.user.full_name,
            patient_phone=presc.patient.user.phone_number,
            doctor_name=presc.doctor_name,
            diagnosis=presc.diagnosis,
            created_at=presc.created_at,
            total_medications=len(medications_list),
            medications=medications_list
        ))
    
    return results


@router.get("/appointments", response_model=List[AppointmentDetailReport],
            summary="گزارش تفصیلی نوبت‌ها")
async def get_detailed_appointments_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[AppointmentStatus] = None,
    patient_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Get detailed report of all appointments (Admin only)
    گزارش تفصیلی تمام نوبت‌ها (فقط مدیر)
    """
    # Set default dates
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Build query
    query = db.query(Appointment).join(Patient).join(User).filter(
        and_(
            Appointment.appointment_date >= datetime.combine(start_date, datetime.min.time()),
            Appointment.appointment_date <= datetime.combine(end_date, datetime.max.time())
        )
    )
    
    if status:
        query = query.filter(Appointment.status == status)
    
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)
    
    appointments = query.order_by(desc(Appointment.appointment_date)).all()
    
    results = []
    for apt in appointments:
        results.append(AppointmentDetailReport(
            appointment_id=apt.id,
            patient_id=apt.patient_id,
            patient_name=apt.patient.user.full_name,
            patient_phone=apt.patient.user.phone_number,
            appointment_date=apt.appointment_date,
            status=apt.status.value,
            reason=apt.reason,
            notes=apt.notes,
            created_at=apt.created_at
        ))
    
    return results


@router.get("/export/patients-csv", summary="خروجی CSV بیماران تفصیلی")
async def export_detailed_patients_csv(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Export detailed patients report to CSV (Admin only)
    خروجی CSV گزارش تفصیلی بیماران (فقط مدیر)
    """
    data = await get_detailed_patients_report(start_date, end_date, None, None, db, current_user)
    
    if not data:
        raise HTTPException(status_code=404, detail="داده‌ای برای خروجی یافت نشد")
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        'patient_id', 'full_name', 'phone_number', 'national_code', 'gender', 
        'blood_type', 'age', 'total_appointments', 'completed_appointments', 
        'canceled_appointments', 'total_prescriptions', 'total_medications',
        'total_factors', 'total_factor_units', 'total_factor_cost',
        'has_insurance', 'insurance_company', 'last_appointment_date',
        'last_prescription_date', 'last_factor_date'
    ])
    writer.writeheader()
    
    for item in data:
        writer.writerow(item.model_dump())
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=patients_detailed_report.csv"}
    )


@router.get("/export/factors-csv", summary="خروجی CSV فاکتورهای تفصیلی")
async def export_detailed_factors_csv(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Export detailed factors report to CSV (Admin only)
    خروجی CSV گزارش تفصیلی فاکتورها (فقط مدیر)
    """
    data = await get_detailed_factors_report(start_date, end_date, None, None, None, db, current_user)
    
    if not data:
        raise HTTPException(status_code=404, detail="داده‌ای برای خروجی یافت نشد")
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        'factor_id', 'patient_id', 'patient_name', 'patient_phone',
        'factor_type', 'units_administered', 'administration_date',
        'lot_number', 'administered_by', 'cost', 'notes'
    ])
    writer.writeheader()
    
    for item in data:
        writer.writerow(item.model_dump())
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=factors_detailed_report.csv"}
    )