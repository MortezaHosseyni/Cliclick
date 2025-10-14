"""
User management routes
مسیرهای مدیریت کاربران
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models.user import User
from app.db.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.security import get_password_hash, get_current_admin, get_current_user
from app.utils.messages_fa import ERROR_MESSAGES, SUCCESS_MESSAGES

router = APIRouter(prefix="/users", tags=["مدیریت کاربران / User Management"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="ایجاد کاربر جدید")
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Create new user (Admin only)
    ایجاد کاربر جدید (فقط مدیر)
    """
    # Check if phone number exists / بررسی وجود شماره تلفن
    existing_user = db.query(User).filter(User.phone_number == user_data.phone_number).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES["phone_exists"]
        )
    
    # Create new user / ایجاد کاربر جدید
    new_user = User(
        phone_number=user_data.phone_number,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse.model_validate(new_user)


@router.get("/", response_model=List[UserResponse], summary="دریافت لیست کاربران")
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Get all users (Admin only)
    دریافت تمام کاربران (فقط مدیر)
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return [UserResponse.model_validate(user) for user in users]


@router.get("/me", response_model=UserResponse, summary="دریافت اطلاعات کاربر جاری")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    دریافت اطلاعات کاربر جاری
    """
    return UserResponse.model_validate(current_user)


@router.get("/{user_id}", response_model=UserResponse, summary="دریافت اطلاعات کاربر")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Get user by ID (Admin only)
    دریافت کاربر با شناسه (فقط مدیر)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["user_not_found"]
        )
    
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse, summary="بروزرسانی کاربر")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Update user (Admin only)
    بروزرسانی کاربر (فقط مدیر)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["user_not_found"]
        )
    
    # Update fields / بروزرسانی فیلدها
    update_data = user_data.model_dump(exclude_unset=True)
    
    if "password" in update_data and update_data["password"]:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="حذف کاربر")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Delete user (Admin only)
    حذف کاربر (فقط مدیر)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["user_not_found"]
        )
    
    db.delete(user)
    db.commit()
    
    return None