"""
Security utilities for authentication and authorization
ابزارهای امنیتی برای احراز هویت و مجوزدهی
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import get_db
from app.db.models.user import User
from app.utils.messages_fa import ERROR_MESSAGES

# Password hashing context / رمزنگاری رمز عبور
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token security / امنیت توکن Bearer
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password / تایید رمز عبور"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password / رمزنگاری رمز عبور"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token / ایجاد توکن دسترسی"""
    to_encode = data.copy()
    
    # Use timezone-aware datetime
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.now(timezone.utc)  # Issued at time
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token / ایجاد توکن تازه‌سازی"""
    to_encode = data.copy()
    
    # Use timezone-aware datetime
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.now(timezone.utc)  # Issued at time
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode JWT token / رمزگشایی توکن"""
    try:
        # PyJWT automatically validates exp claim
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "require": ["exp", "type"]
            }
        )
        return payload
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.get("invalid_token", "Invalid token"),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.get("invalid_token", "Could not validate credentials"),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user / دریافت کاربر احراز هویت شده"""
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        # Verify token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.get("invalid_token", "Invalid token type"),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user ID from token
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.get("invalid_credentials", "Could not validate credentials"),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Query user from database
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.get("user_not_found", "User not found"),
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.get("inactive_user", "Inactive user"),
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.get("invalid_credentials", "Could not validate credentials"),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Verify user is admin / تایید کاربر به عنوان مدیر"""
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_MESSAGES.get("admin_only", "Admin access required"),
        )
    return current_user


async def get_current_secretary_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Verify user is secretary or admin / تایید کاربر به عنوان منشی یا مدیر"""
    if current_user.role not in ["Admin", "Secretary"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_MESSAGES.get("secretary_or_admin_only", "Secretary or Admin access required"),
        )
    return current_user


# Optional: Function to verify refresh token
async def verify_refresh_token(token: str) -> dict:
    """Verify refresh token / تایید توکن تازه‌سازی"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
            }
        )
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.get("invalid_token", "Invalid token type"),
            )
        
        return payload
        
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.get("invalid_token", "Invalid refresh token"),
        )