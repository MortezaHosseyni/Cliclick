"""
Create Admin User Script
"""
import asyncio
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.db.models.user import User
from app.core.security import get_password_hash

async def create_admin():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.phone_number == "09123456789").first()
        if existing_admin:
            print("❌ Admin user already exists")
            return

        admin = User(
            phone_number="09123456789",
            hashed_password=get_password_hash("admin123456"),
            full_name="System Administrator",
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("✅ Admin user created successfully")
        print(f"📱 Phone: {admin.phone_number}")
        print(f"🔑 Password: admin123456")
        print(f"👤 Name: {admin.full_name}")
        print(f"👑 Role: {admin.role}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(create_admin())
