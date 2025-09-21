@echo off
echo 🚀 Starting Microservice Chatbot Locally (Windows)
echo =============================================

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found. Please run install_local.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment and run startup script
venv\Scripts\python.exe start_local.py

pause