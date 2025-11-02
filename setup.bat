@echo off
echo ================================================
echo 🔧 Remote Browser Streaming - Setup Script
echo ================================================
echo.
echo This script will set up your development environment.
echo.

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    echo    Please install Python 3.10+ from python.org
    echo.
    pause
    exit /b 1
)

echo ✅ Python found
python --version
echo.

:: Create virtual environment
echo 📦 Creating virtual environment...
if exist "venv\" (
    echo    Virtual environment already exists, skipping...
) else (
    python -m venv venv
    echo    ✅ Created venv
)
echo.

:: Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat
echo.

:: Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip
echo.

:: Install dependencies
echo 📦 Installing Python dependencies...
echo    This may take a few minutes...
echo.
pip install -r requirements.txt
echo.

if %errorlevel% equ 0 (
    echo ================================================
    echo ✅ Setup completed successfully!
    echo ================================================
    echo.
    echo 📋 Next steps:
    echo.
    echo    1. Install system dependencies:
    echo       choco install googlechrome chromedriver ffmpeg -y
    echo.
    echo    2. Run the application:
    echo       run.bat
    echo.
    echo    3. Open browser:
    echo       http://localhost:5000
    echo.
    echo ================================================
) else (
    echo ================================================
    echo ❌ Setup failed!
    echo ================================================
    echo.
    echo Please check the error messages above.
    echo.
    echo Common issues:
    echo    - Missing Visual C++ build tools
    echo      Fix: choco install visualstudio2022buildtools -y
    echo.
    echo    - Network connectivity issues
    echo      Fix: Check your internet connection
    echo.
    echo ================================================
)

pause

