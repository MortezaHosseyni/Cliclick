#!/bin/bash
# ==============================================================
# 🏥 Clinic Management System - Automated Setup
# ==============================================================

# ---------------------- Colors ----------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ---------------------- Helpers ----------------------
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }

pause_on_error() {
    echo ""
    read -p "🔻 Press Enter to close window..." _
}

safe_exit() {
    pause_on_error
    exit 1
}

# ---------------------- Banner ----------------------
clear
echo "=============================================================="
echo "🏥 Clinic Management System - Setup Wizard"
echo "=============================================================="
echo ""

# ---------------------- Python Check ----------------------
print_info "Checking Python..."
if ! command -v python &> /dev/null; then
    print_error "Python 3 not found! Please install Python 3.9 or higher."
    safe_exit
fi
print_success "Found Python $(python --version)"

# ---------------------- MySQL Check (XAMPP) ----------------------
print_info "Checking MySQL (XAMPP)..."
XAMPP_MYSQL="/Applications/XAMPP/bin/mysql"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    XAMPP_MYSQL="C:/xampp/mysql/bin/mysql.exe"
fi

if [ ! -f "$XAMPP_MYSQL" ] && ! command -v mysql &> /dev/null; then
    print_error "MySQL not found! Please ensure XAMPP is installed and MySQL is running."
    safe_exit
fi
print_success "MySQL found"

# ---------------------- Virtual Environment ----------------------
print_info "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv || { print_error "Error creating virtual environment!"; safe_exit; }
    print_success "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# ---------------------- Activate venv ----------------------
print_info "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate || { print_error "Failed to activate virtual environment!"; safe_exit; }
else
    source venv/bin/activate || { print_error "Failed to activate virtual environment!"; safe_exit; }
fi
print_success "Virtual environment activated"

# ---------------------- Upgrade pip ----------------------
print_info "Upgrading pip..."
python -m pip install --upgrade pip > /dev/null 2>&1 || { print_error "Pip upgrade failed!"; safe_exit; }
print_success "Pip upgraded"

# ---------------------- Install Requirements ----------------------
print_info "Installing required packages..."
if [ -f "requirements.txt" ]; then
    python -m pip install -r requirements.txt || { print_error "Package installation failed!"; safe_exit; }
    print_success "Packages installed"
else
    print_error "requirements.txt not found!"
    safe_exit
fi

# ---------------------- .env Setup ----------------------
print_info "Checking .env file..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

        # Update .env for XAMPP MySQL (default: no password for root)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/Hyxu2j4qXapTStptQvrZaYvU2LLgcVpa-9517538246/$SECRET_KEY/" .env
            sed -i '' "s/DB_USER=.*/DB_USER=root/" .env
            sed -i '' "s/DB_PASSWORD=.*/DB_PASSWORD=/" .env
            sed -i '' "s/DB_HOST=.*/DB_HOST=localhost/" .env
            sed -i '' "s/DB_PORT=.*/DB_PORT=3306/" .env
        else
            sed -i "s/Hyxu2j4qXapTStptQvrZaYvU2LLgcVpa-9517538246/$SECRET_KEY/" .env
            sed -i "s/DB_USER=.*/DB_USER=root/" .env
            sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=/" .env
            sed -i "s/DB_HOST=.*/DB_HOST=localhost/" .env
            sed -i "s/DB_PORT=.*/DB_PORT=3306/" .env
        fi

        print_success ".env file created with XAMPP MySQL defaults (root user, no password)"
    else
        print_error ".env.example not found!"
        safe_exit
    fi
else
    print_info ".env file already exists"
fi

# ---------------------- Database Setup ----------------------
echo ""
print_info "Would you like to automatically create the database? (y/n)"
read -p "Create database automatically? (y/n): " create_db

if [[ "$create_db" =~ ^[Yy]$ ]]; then
    print_info "Enter MySQL root password (press Enter if no password for XAMPP default):"
    read -sp "MySQL root password: " mysql_root_pass
    echo ""

    print_info "Creating database..."
    
    # Use XAMPP MySQL if available, otherwise use system MySQL
    MYSQL_CMD="mysql"
    if [ -f "$XAMPP_MYSQL" ]; then
        MYSQL_CMD="$XAMPP_MYSQL"
    fi
    
    if [ -z "$mysql_root_pass" ]; then
        $MYSQL_CMD -u root <<EOF
CREATE DATABASE IF NOT EXISTS clinic_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON clinic_db.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
EOF
    else
        $MYSQL_CMD -u root -p"$mysql_root_pass" <<EOF
CREATE DATABASE IF NOT EXISTS clinic_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON clinic_db.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
EOF
    fi

    if [ $? -eq 0 ]; then
        print_success "Database created successfully"
    else
        print_error "Error creating database!"
        safe_exit
    fi
else
    print_info "You can create the database manually."
    print_info "Database name: clinic_db"
    print_info "Or use phpMyAdmin at: http://localhost/phpmyadmin"
fi

# ---------------------- Folder Structure ----------------------
print_info "Creating folder structure..."
mkdir -p app/core app/db/{models,schemas} app/api/routes app/utils app/tests logs
touch app/{__init__.py,core/__init__.py,db/__init__.py,db/models/__init__.py,db/schemas/__init__.py,api/__init__.py,api/routes/__init__.py,utils/__init__.py,tests/__init__.py}
print_success "Folder structure and __init__.py files created"

# ---------------------- Admin Script ----------------------
print_info "Creating admin user creation script..."
cat > create_admin.py <<'EOF'
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
EOF
print_success "create_admin.py script created"

# ---------------------- Run Script ----------------------
print_info "Creating run script..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    cat > run.bat <<'EOF'
@echo off
echo 🚀 Starting server...
call venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
EOF
    print_success "run.bat script created (Windows)"
else
    cat > run.sh <<'EOF'
#!/bin/bash
echo "🚀 Starting server..."
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
EOF
    chmod +x run.sh
    print_success "run.sh script created"
fi

# ---------------------- Test Script ----------------------
print_info "Creating test script..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    cat > test.bat <<'EOF'
@echo off
echo 🧪 Running tests...
call venv\Scripts\activate
pytest -v
pause
EOF
    print_success "test.bat script created (Windows)"
else
    cat > test.sh <<'EOF'
#!/bin/bash
echo "🧪 Running tests..."
source venv/bin/activate
pytest -v
EOF
    chmod +x test.sh
    print_success "test.sh script created"
fi

# ---------------------- Summary ----------------------
echo ""
echo "=============================================================="
print_success "✅ Setup completed successfully!"
echo "=============================================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1️⃣ Make sure XAMPP is running (MySQL service)"
echo "   → Start XAMPP Control Panel"
echo "   → Start MySQL service"
echo ""
echo "2️⃣ Run the application:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   run.bat"
else
    echo "   ./run.sh"
fi
echo ""
echo "3️⃣ Create admin user:"
echo "   python create_admin.py"
echo ""
echo "4️⃣ API Documentation:"
echo "   Swagger UI → http://localhost:8000/docs"
echo "   ReDoc → http://localhost:8000/redoc"
echo ""
echo "5️⃣ Default login credentials:"
echo "   📱 Phone: 09123456789"
echo "   🔑 Password: admin123456"
echo ""
echo "6️⃣ XAMPP phpMyAdmin:"
echo "   → http://localhost/phpmyadmin"
echo ""
echo "=============================================================="
print_info "To activate virtual environment:  source venv/bin/activate"
print_info "To deactivate virtual environment: deactivate"
echo ""
print_success "Good luck! 🚀"
echo "=============================================================="
pause_on_error