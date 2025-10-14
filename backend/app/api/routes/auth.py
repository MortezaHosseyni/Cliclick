"""
Authentication routes
مسیرهای احراز هویت
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.db.schemas.user import LoginRequest, TokenResponse, UserResponse
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.utils.messages_fa import ERROR_MESSAGES, SUCCESS_MESSAGES

router = APIRouter(prefix="/auth", tags=["احراز هویت / Authentication"])


@router.post("/login", response_model=TokenResponse, summary="ورود به سیستم")
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with phone number and password
    ورود با شماره تلفن و رمز عبور
    """
    # Find user by phone number / یافتن کاربر با شماره تلفن
    user = db.query(User).filter(User.phone_number == login_data.phone_number).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES["invalid_credentials"]
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_MESSAGES["inactive_user"]
        )
    
    # Create tokens / ایجاد توکن‌ها
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/refresh", response_model=TokenResponse, summary="تازه‌سازی توکن")
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token
    تازه‌سازی توکن دسترسی با استفاده از توکن تازه‌سازی
    """
    payload = decode_token(refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES["invalid_token"]
        )
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES["invalid_token"]
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["user_not_found"]
        )
    
    # Create new tokens / ایجاد توکن‌های جدید
    new_access_token = create_access_token(data={"sub": user.id})
    new_refresh_token = create_refresh_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        user=UserResponse.model_validate(user)
    )