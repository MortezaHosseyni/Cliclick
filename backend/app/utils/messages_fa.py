"""
Farsi (Persian) messages for responses and errors
پیام‌های فارسی برای پاسخ‌ها و خطاها
"""

# Error Messages / پیام‌های خطا
ERROR_MESSAGES = {
    # Authentication / احراز هویت
    "invalid_credentials": "شماره تلفن یا رمز عبور نادرست است",
    "invalid_token": "توکن نامعتبر است",
    "token_expired": "توکن منقضی شده است",
    "inactive_user": "حساب کاربری غیرفعال است",
    "user_not_found": "کاربر یافت نشد",
    
    # Authorization / مجوزدهی
    "admin_only": "فقط مدیران اجازه دسترسی دارند",
    "secretary_or_admin_only": "فقط منشی‌ها و مدیران اجازه دسترسی دارند",
    "permission_denied": "شما مجوز انجام این عملیات را ندارید",
    
    # User Management / مدیریت کاربران
    "phone_exists": "این شماره تلفن قبلاً ثبت شده است",
    "user_create_failed": "ایجاد کاربر با خطا مواجه شد",
    "user_update_failed": "بروزرسانی کاربر با خطا مواجه شد",
    "user_delete_failed": "حذف کاربر با خطا مواجه شد",
    
    # Patient Management / مدیریت بیماران
    "patient_not_found": "بیمار یافت نشد",
    "patient_create_failed": "ایجاد بیمار با خطا مواجه شد",
    "patient_update_failed": "بروزرسانی بیمار با خطا مواجه شد",
    
    # Appointments / نوبت‌ها
    "appointment_not_found": "نوبت یافت نشد",
    "appointment_create_failed": "ایجاد نوبت با خطا مواجه شد",
    "appointment_conflict": "در این زمان نوبت دیگری وجود دارد",
    
    # Medications / داروها
    "medication_not_found": "دارو یافت نشد",
    "medication_exists": "این دارو قبلاً ثبت شده است",
    
    # Prescriptions / نسخه‌ها
    "prescription_not_found": "نسخه یافت نشد",
    "prescription_create_failed": "ایجاد نسخه با خطا مواجه شد",
    
    # Factors / فاکتورها
    "factor_not_found": "فاکتور یافت نشد",
    
    # Insurance / بیمه
    "insurance_not_found": "بیمه یافت نشد",
    
    # Settings / تنظیمات
    "settings_not_found": "تنظیمات یافت نشد",
    "settings_update_failed": "بروزرسانی تنظیمات با خطا مواجه شد",
    
    # Support / پشتیبانی
    "support_chat_not_found": "گفتگو یافت نشد",
    
    # General / عمومی
    "internal_error": "خطای داخلی سرور",
    "validation_error": "اطلاعات ورودی نامعتبر است",
    "not_found": "مورد درخواستی یافت نشد",
}

# Success Messages / پیام‌های موفقیت
SUCCESS_MESSAGES = {
    # Authentication / احراز هویت
    "login_success": "ورود با موفقیت انجام شد",
    "logout_success": "خروج با موفقیت انجام شد",
    "token_refreshed": "توکن با موفقیت تازه‌سازی شد",
    
    # User Management / مدیریت کاربران
    "user_created": "کاربر با موفقیت ایجاد شد",
    "user_updated": "کاربر با موفقیت بروزرسانی شد",
    "user_deleted": "کاربر با موفقیت حذف شد",
    
    # Patient Management / مدیریت بیماران
    "patient_created": "بیمار با موفقیت ایجاد شد",
    "patient_updated": "بیمار با موفقیت بروزرسانی شد",
    "patient_deleted": "بیمار با موفقیت حذف شد",
    
    # Appointments / نوبت‌ها
    "appointment_created": "نوبت با موفقیت ایجاد شد",
    "appointment_updated": "نوبت با موفقیت بروزرسانی شد",
    "appointment_deleted": "نوبت با موفقیت حذف شد",
    "appointment_confirmed": "نوبت تایید شد",
    "appointment_completed": "نوبت تکمیل شد",
    "appointment_canceled": "نوبت لغو شد",
    
    # Medications / داروها
    "medication_created": "دارو با موفقیت ایجاد شد",
    "medication_updated": "دارو با موفقیت بروزرسانی شد",
    "medication_deleted": "دارو با موفقیت حذف شد",
    
    # Prescriptions / نسخه‌ها
    "prescription_created": "نسخه با موفقیت ایجاد شد",
    "prescription_updated": "نسخه با موفقیت بروزرسانی شد",
    
    # Factors / فاکتورها
    "factor_created": "فاکتور با موفقیت ایجاد شد",
    "factor_updated": "فاکتور با موفقیت بروزرسانی شد",
    "factor_deleted": "فاکتور با موفقیت حذف شد",
    
    # Insurance / بیمه
    "insurance_created": "بیمه با موفقیت ایجاد شد",
    "insurance_updated": "بیمه با موفقیت بروزرسانی شد",
    "insurance_deleted": "بیمه با موفقیت حذف شد",
    
    # Settings / تنظیمات
    "settings_updated": "تنظیمات با موفقیت بروزرسانی شد",
    
    # Support / پشتیبانی
    "message_sent": "پیام با موفقیت ارسال شد",
    
    # Reports / گزارشات
    "report_generated": "گزارش با موفقیت تولید شد",
    "report_exported": "گزارش با موفقیت خروجی گرفته شد",
}