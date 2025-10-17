"""
Clinic Management System - Main Application Entry Point
سیستم مدیریت کلینیک - نقطه ورود اصلی برنامه

This file initializes the FastAPI application and includes all routers.
این فایل برنامه FastAPI را راه‌اندازی کرده و تمام روترها را اضافه می‌کند.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.database import engine, Base
from app.api.routes import (
    auth,
    users,
    patients,
    appointments,
    medications,
    prescriptions,
    factors,
    insurances,
    settings as settings_routes,
    support,
    reports
)


# Lifespan context manager for startup and shutdown events
# مدیریت رویدادهای راه‌اندازی و خاموش‌سازی
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application
    مدیریت چرخه حیات برنامه
    """
    # Startup: Create database tables
    # راه‌اندازی: ایجاد جداول دیتابیس
    print("🚀 راه‌اندازی برنامه...")
    print("🚀 Starting application...")
    
    # Create all tables (if not using Alembic)
    # ایجاد تمام جداول (در صورت عدم استفاده از Alembic)
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Shutdown: Cleanup
    # خاموش‌سازی: پاکسازی
    print("🛑 خاموش‌سازی برنامه...")
    print("🛑 Shutting down application...")


# Initialize FastAPI application
# راه‌اندازی برنامه FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    # سیستم مدیریت کلینیک 🏥
    
    این سیستم برای مدیریت کلینیک‌های پزشکی طراحی شده است.
    
    ## ویژگی‌های اصلی:
    - مدیریت کاربران و احراز هویت
    - مدیریت بیماران
    - مدیریت نوبت‌ها
    - مدیریت داروها و نسخه‌ها
    - مدیریت فاکتورها
    - مدیریت بیمه
    - پشتیبانی آنلاین (WebSocket)
    - گزارش‌گیری جامع
    
    ## Clinic Management System 🏥
    
    This system is designed for medical clinic management.
    
    ### Main Features:
    - User Management & Authentication
    - Patient Management
    - Appointment Scheduling
    - Medication & Prescription Management
    - Factor Management
    - Insurance Management
    - Online Support (WebSocket)
    - Comprehensive Reporting
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
# تنظیمات CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
# اضافه کردن روترها
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["احراز هویت / Authentication"]
)

app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["کاربران / Users"]
)

app.include_router(
    patients.router,
    prefix="/api/v1/patients",
    tags=["بیماران / Patients"]
)

app.include_router(
    appointments.router,
    prefix="/api/v1/appointments",
    tags=["نوبت‌ها / Appointments"]
)

app.include_router(
    medications.router,
    prefix="/api/v1/medications",
    tags=["داروها / Medications"]
)

app.include_router(
    prescriptions.router,
    prefix="/api/v1/prescriptions",
    tags=["نسخه‌ها / Prescriptions"]
)

app.include_router(
    factors.router,
    prefix="/api/v1/factors",
    tags=["فاکتورها / Factors"]
)

app.include_router(
    insurances.router,
    prefix="/api/v1/insurances",
    tags=["بیمه / Insurance"]
)

app.include_router(
    settings_routes.router,
    prefix="/api/v1/settings",
    tags=["تنظیمات / Settings"]
)

app.include_router(
    support.router,
    prefix="/api/v1/support",
    tags=["پشتیبانی / Support"]
)

app.include_router(
    reports.router,
    prefix="/api/v1/reports",
    tags=["گزارش‌ها / Reports"]
)


# Root endpoint
# نقطه ورود اصلی
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - Health check
    نقطه ورود اصلی - بررسی سلامت سیستم
    """
    return {
        "message": "سیستم مدیریت کلینیک - فعال است",
        "message_en": "Clinic Management System - Active",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Health check endpoint
# بررسی سلامت سیستم
@app.get("/health", tags=["Root"])
async def health_check():
    """
    Health check endpoint
    بررسی سلامت سیستم
    """
    return {
        "status": "healthy",
        "message": "سیستم به درستی کار می‌کند"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )