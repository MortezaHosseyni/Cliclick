"""
Reports routes
مسیرهای گزارشات
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List
from datetime import date, datetime, timedelta
import csv
import json
import io
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.appointment import Appointment, AppointmentStatus
from app.db.models.patient import Patient
from app.db.models.prescription import Prescription, PrescriptionItem
from app.db.models.medication import Medication
from app.db.models.factor import Factor
from app.db.schemas.report import (
    DailyAppointmentReport,
    ActivePatientReport,
    MedicationUsageReport,
    FactorUsageReport
)
from app.core.security import get_current_admin
from app.utils.messages_fa import SUCCESS_MESSAGES

router = APIRouter(prefix="/reports", tags=["گزارشات / Reports"])


@router.get("/daily-appointments", response_model=List[DailyAppointmentReport], summary="گزارش نوبت‌های روزانه")
async def get_daily_appointments_report(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Get daily appointment statistics (Admin only)
    دریافت آمار نوبت‌های روزانه (فقط مدیر)
    """
    # Set default dates if not provided / تنظیم تاریخ‌های پیش‌فرض
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Query appointments grouped by date / پرس و جو نوبت‌ها گروه‌بندی شده بر اساس تاریخ
    results = []
    current_date = start_date
    
    while current_date <= end_date:
        start_datetime = datetime.combine(current_date, datetime.min.time())
        end_datetime = datetime.combine(current_date, datetime.max.time())
        
        total = db.query(func.count(Appointment.id)).filter(
            and_(
                Appointment.appointment_date >= start_datetime,
                Appointment.appointment_date <= end_datetime
            )
        ).scalar()
        
        pending = db.query(func.count(Appointment.id)).filter(
            and_(
                Appointment.appointment_date >= start_datetime,
                Appointment.appointment_date <= end_datetime,
                Appointment.status == AppointmentStatus.PENDING
            )
        ).scalar()
        
        confirmed = db.query(func.count(Appointment.id)).filter(
            and_(
                Appointment.appointment_date >= start_datetime,
                Appointment.appointment_date <= end_datetime,
                Appointment.status == AppointmentStatus.CONFIRMED
            )
        ).scalar()
        
        completed = db.query(func.count(Appointment.id)).filter(
            and_(
                Appointment.appointment_date >= start_datetime,
                Appointment.appointment_date <= end_datetime,
                Appointment.status == AppointmentStatus.COMPLETED
            )
        ).scalar()
        
        canceled = db.query(func.count(Appointment.id)).filter(
            and_(
                Appointment.appointment_date >= start_datetime,
                Appointment.appointment_date <= end_datetime,
                Appointment.status == AppointmentStatus.CANCELED
            )
        ).scalar()
        
        results.append(DailyAppointmentReport(
            date=current_date,
            total_appointments=total or 0,
            pending=pending or 0,
            confirmed=confirmed or 0,
            completed=completed or 0,
            canceled=canceled or 0
        ))
        
        current_date += timedelta(days=1)
    
    return results


@router.get("/active-patients", response_model=ActivePatientReport, summary="گزارش بیماران فعال")
async def get_active_patients_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Get active patient statistics (Admin only)
    دریافت آمار بیماران فعال (فقط مدیر)
    """
    # Total patients / تعداد کل بیماران
    total_patients = db.query(func.count(Patient.id)).scalar()
    
    # Patients with appointments / بیماران با نوبت
    patients_with_appointments = db.query(func.count(func.distinct(Appointment.patient_id))).scalar()
    
    # Patients with prescriptions / بیماران با نسخه
    patients_with_prescriptions = db.query(func.count(func.distinct(Prescription.patient_id))).scalar()
    
    # Patients with factors / بیماران با فاکتور
    patients_with_factors = db.query(func.count(func.distinct(Factor.patient_id))).scalar()
    
    return ActivePatientReport(
        total_patients=total_patients or 0,
        patients_with_appointments=patients_with_appointments or 0,
        patients_with_prescriptions=patients_with_prescriptions or 0,
        patients_with_factors=patients_with_factors or 0
    )


@router.get("/medication-usage", response_model=List[MedicationUsageReport], summary="گزارش مصرف داروها")
async def get_medication_usage_report(
    start_date: date = None,
    end_date: date = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Get medication usage statistics (Admin only)
    دریافت آمار مصرف داروها (فقط مدیر)
    """
    # Set default dates if not provided / تنظیم تاریخ‌های پیش‌فرض
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=365)
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Query medication usage / پرس و جو مصرف داروها
    usage_data = db.query(
        Medication.id,
        Medication.name,
        func.count(PrescriptionItem.id).label('prescribed_count'),
        func.sum(PrescriptionItem.quantity).label('total_quantity')
    ).join(
        PrescriptionItem, PrescriptionItem.medication_id == Medication.id
    ).join(
        Prescription, Prescription.id == PrescriptionItem.prescription_id
    ).filter(
        and_(
            Prescription.created_at >= start_datetime,
            Prescription.created_at <= end_datetime
        )
    ).group_by(
        Medication.id, Medication.name
    ).order_by(
        func.count(PrescriptionItem.id).desc()
    ).limit(limit).all()
    
    results = []
    for row in usage_data:
        results.append(MedicationUsageReport(
            medication_id=row.id,
            medication_name=row.name,
            total_prescribed=row.prescribed_count or 0,
            total_quantity=int(row.total_quantity) if row.total_quantity else 0
        ))
    
    return results


@router.get("/factor-usage", response_model=List[FactorUsageReport], summary="گزارش مصرف فاکتورها")
async def get_factor_usage_report(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Get factor usage statistics (Admin only)
    دریافت آمار مصرف فاکتورها (فقط مدیر)
    """
    # Set default dates if not provided / تنظیم تاریخ‌های پیش‌فرض
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=365)
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Query factor usage by patient / پرس و جو مصرف فاکتور بر اساس بیمار
    usage_data = db.query(
        Patient.id,
        User.full_name,
        Factor.factor_type,
        func.sum(Factor.units_administered).label('total_units'),
        func.sum(Factor.cost).label('total_cost'),
        func.count(Factor.id).label('administration_count')
    ).join(
        Factor, Factor.patient_id == Patient.id
    ).join(
        User, User.id == Patient.user_id
    ).filter(
        and_(
            Factor.administration_date >= start_datetime,
            Factor.administration_date <= end_datetime
        )
    ).group_by(
        Patient.id, User.full_name, Factor.factor_type
    ).order_by(
        func.sum(Factor.units_administered).desc()
    ).all()
    
    results = []
    for row in usage_data:
        results.append(FactorUsageReport(
            patient_id=row.id,
            patient_name=row.full_name,
            factor_type=row.factor_type,
            total_units=int(row.total_units) if row.total_units else 0,
            total_cost=float(row.total_cost) if row.total_cost else 0.0,
            administration_count=row.administration_count or 0
        ))
    
    return results


@router.get("/export", summary="خروجی گزارشات")
async def export_reports(
    report_type: str,
    format: str = "csv",
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Export reports to CSV or JSON (Admin only)
    خروجی گزارشات به فرمت CSV یا JSON (فقط مدیر)
    
    report_type: daily-appointments, active-patients, medication-usage, factor-usage
    format: csv or json
    """
    # Get report data based on type / دریافت داده‌های گزارش بر اساس نوع
    if report_type == "daily-appointments":
        data = await get_daily_appointments_report(start_date, end_date, db, current_user)
    elif report_type == "active-patients":
        data = [await get_active_patients_report(db, current_user)]
    elif report_type == "medication-usage":
        data = await get_medication_usage_report(start_date, end_date, 100, db, current_user)
    elif report_type == "factor-usage":
        data = await get_factor_usage_report(start_date, end_date, db, current_user)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="نوع گزارش نامعتبر است"
        )
    
    # Convert to dict / تبدیل به دیکشنری
    data_dicts = [item.model_dump() for item in data]
    
    if format == "json":
        # Export as JSON / خروجی به فرمت JSON
        json_str = json.dumps(data_dicts, ensure_ascii=False, indent=2, default=str)
        return Response(
            content=json_str,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={report_type}_report.json"}
        )
    
    elif format == "csv":
        # Export as CSV / خروجی به فرمت CSV
        if not data_dicts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="داده‌ای برای خروجی یافت نشد"
            )
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data_dicts[0].keys())
        writer.writeheader()
        writer.writerows(data_dicts)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={report_type}_report.csv"}
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="فرمت نامعتبر است. از csv یا json استفاده کنید"
        )