@echo off
echo ====================================
echo 🌐 Remote Browser Streaming Server
echo ====================================
echo.

:: Check if venv exists
if not exist "venv\" (
    echo ❌ Virtual environment not found!
    echo.
    echo Creating virtual environment...
    python -m venv venv
    echo.
    echo ✅ Virtual environment created
    echo.
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r requirements.txt
    echo.
    echo ✅ Dependencies installed
    echo.
)

:: Activate venv
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated
echo.

:: Check if Chrome is installed
where chrome >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Warning: Chrome not found in PATH
    echo    Make sure Chrome is installed!
    echo.
)

:: Check if ChromeDriver is installed
where chromedriver >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Warning: ChromeDriver not found in PATH
    echo    Install with: choco install chromedriver -y
    echo.
)

echo 🚀 Starting server...
echo.
echo 📡 Server will be available at: http://localhost:5000
echo 🛑 Press Ctrl+C to stop
echo.
echo ====================================
echo.

:: Run the app
python app.py

:: Deactivate on exit
call venv\Scripts\deactivate.bat

