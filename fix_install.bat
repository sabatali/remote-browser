@echo off
echo ================================================
echo 🔧 Installation Troubleshooting Script
echo ================================================
echo.

:: Check if running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Warning: Not running as Administrator
    echo    Some installations may fail
    echo.
)

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    echo    Install from: python.org
    pause
    exit /b 1
)

echo ✅ Python found:
python --version
echo.

:: Check Visual Studio Build Tools
where cl >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Visual C++ Build Tools NOT found
    echo.
    echo 📦 Installing Visual Studio Build Tools...
    echo    This will take 10-15 minutes
    echo.
    
    :: Check if Chocolatey is installed
    where choco >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Chocolatey not found
        echo.
        echo Please install Visual Studio Build Tools manually from:
        echo https://visualstudio.microsoft.com/visual-cpp-build-tools/
        echo.
        echo Or install Chocolatey first, then run this script again.
        pause
        exit /b 1
    ) else (
        echo Installing with Chocolatey...
        choco install visualstudio2022buildtools -y
        echo.
        echo ✅ Build Tools installed!
        echo    ⚠️  PLEASE RESTART YOUR COMPUTER before continuing
        echo.
        pause
        exit /b 0
    )
) else (
    echo ✅ Visual C++ Build Tools found
    echo.
)

:: Clean previous installation
echo 🧹 Cleaning previous installation...
if exist "venv\" (
    echo    Removing old virtual environment...
    rmdir /s /q venv
    echo    ✅ Cleaned
) else (
    echo    No previous venv found
)
echo.

:: Create fresh venv
echo 📦 Creating fresh virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment created
echo.

:: Activate venv
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat
echo.

:: Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip
echo.

:: Try installing with different strategies
echo ================================================
echo 📦 Installing Python packages...
echo    Strategy: Try pre-built wheels first
echo ================================================
echo.

:: Install packages that definitely have wheels
echo [1/3] Installing packages with pre-built wheels...
pip install flask flask-cors selenium opencv-python numpy Pillow aiohttp
echo.

:: Try aiortc
echo [2/3] Installing aiortc (WebRTC library)...
pip install aiortc
if %errorlevel% neq 0 (
    echo ⚠️  aiortc installation failed
    echo    This package requires Visual C++ Build Tools
    echo    Please install them and try again
    echo.
) else (
    echo ✅ aiortc installed successfully
    echo.
)

:: Try av (PyAV) with different methods
echo [3/3] Installing av (PyAV) - Media processing...
echo    Trying method 1: Pre-built wheel...
pip install av --only-binary :all: 2>nul
if %errorlevel% neq 0 (
    echo    Method 1 failed, trying method 2: Latest version...
    pip install av
    if %errorlevel% neq 0 (
        echo    Method 2 failed, trying method 3: Specific version...
        pip install av==11.0.0
        if %errorlevel% neq 0 (
            echo.
            echo ================================================
            echo ❌ av (PyAV) installation failed
            echo ================================================
            echo.
            echo This package requires:
            echo   1. Visual C++ Build Tools
            echo   2. FFmpeg development libraries
            echo.
            echo Solutions:
            echo   1. Install Visual Studio Build Tools
            echo      choco install visualstudio2022buildtools -y
            echo.
            echo   2. Use Conda instead:
            echo      choco install miniconda3 -y
            echo      conda install -c conda-forge av
            echo.
            echo   3. Try Python 3.10 instead of 3.12
            echo      (More pre-built wheels available)
            echo.
            echo ================================================
            pause
            exit /b 1
        )
    )
)
echo ✅ av installed successfully
echo.

:: Verify installation
echo ================================================
echo ✅ Verifying installation...
echo ================================================
echo.

python -c "import flask; print('✅ Flask:', flask.__version__)"
python -c "import selenium; print('✅ Selenium:', selenium.__version__)"
python -c "import cv2; print('✅ OpenCV:', cv2.__version__)"
python -c "import aiortc; print('✅ aiortc:', aiortc.__version__)"
python -c "import av; print('✅ av:', av.__version__)"

echo.
echo ================================================
echo ✅ Installation completed successfully!
echo ================================================
echo.
echo 📋 Next steps:
echo    1. Make sure Chrome and ChromeDriver are installed:
echo       choco install googlechrome chromedriver -y
echo.
echo    2. Run the application:
echo       run.bat
echo.
echo    3. Open your browser to:
echo       http://localhost:5000
echo.
echo ================================================

pause

