@echo off
cd /d "%~dp0"
echo 🚀 Starting server...
call venv\Scripts\activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 1212
pause