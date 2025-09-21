@echo off
echo 🚀 Installing Microservice Chatbot Locally (Windows)
echo ===============================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.10+ first.
    echo Download from: https://python.org
    pause
    exit /b 1
)

REM Run the Python installation script
python install_local.py

echo.
echo 📋 Installation complete! Next steps:
echo 1. Edit .env file with your OpenAI API key
echo 2. Run: start_local.bat
echo.
pause