"""
Settings management routes
مسیرهای مدیریت تنظیمات
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.settings import Setting
from app.db.schemas.setting import SettingCreate, SettingUpdate, SettingResponse
from app.core.security import get_current_admin, get_current_user
from app.utils.messages_fa import ERROR_MESSAGES, SUCCESS_MESSAGES

router = APIRouter(prefix="/settings", tags=["تنظیمات / Settings"])


@router.get("/", response_model=SettingResponse, summary="دریافت تنظیمات کلینیک")
async def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get clinic settings
    دریافت تنظیمات کلینیک
    """
    settings = db.query(Setting).first()
    
    if not settings:
        # Create default settings if not exists / ایجاد تنظیمات پیش‌فرض در صورت عدم وجود
        settings = Setting(
            clinic_name="کلینیک",
            clinic_description="سیستم مدیریت کلینیک",
            clinic_address="آدرس کلینیک",
            clinic_phone="021-12345678",
            working_hours="شنبه تا چهارشنبه: 8 صبح تا 8 شب"
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return SettingResponse.model_validate(settings)


@router.post("/", response_model=SettingResponse, status_code=status.HTTP_201_CREATED, summary="ایجاد تنظیمات")
async def create_settings(
    setting_data: SettingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Create clinic settings (Admin only)
    ایجاد تنظیمات کلینیک (فقط مدیر)
    """
    # Check if settings already exist / بررسی وجود تنظیمات
    existing = db.query(Setting).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="تنظیمات قبلاً ایجاد شده است. از بروزرسانی استفاده کنید"
        )
    
    # Create settings / ایجاد تنظیمات
    new_settings = Setting(**setting_data.model_dump())
    
    db.add(new_settings)
    db.commit()
    db.refresh(new_settings)
    
    return SettingResponse.model_validate(new_settings)


@router.put("/", response_model=SettingResponse, summary="بروزرسانی تنظیمات")
async def update_settings(
    setting_data: SettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Update clinic settings (Admin only)
    بروزرسانی تنظیمات کلینیک (فقط مدیر)
    """
    settings = db.query(Setting).first()
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["settings_not_found"]
        )
    
    # Update fields / بروزرسانی فیلدها
    update_data = setting_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    
    return SettingResponse.model_validate(settings)