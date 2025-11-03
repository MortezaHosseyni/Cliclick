@echo off
echo 🚀 Starting server...
call venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 1212
pause
