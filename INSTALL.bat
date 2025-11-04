@echo off
REM ============================================================================
REM OBS Digital Signage Automation System - Windows Installation Script
REM ============================================================================

echo.
echo ====================================================================
echo  OBS Digital Signage Automation System - Installation
echo ====================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.10 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo [1/5] Python detected
python --version

REM Check Python version (must be 3.10+)
python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.10 or higher is required
    echo.
    pause
    exit /b 1
)

REM Create virtual environment
echo.
echo [2/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping creation
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo.
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo.
echo [4/5] Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install dependencies
echo.
echo [5/6] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

REM Setup configuration files
echo.
echo [6/6] Setting up configuration files...
if not exist "config\windows_test.env" (
    echo Creating config\windows_test.env from example...
    copy "config\windows_test.env.example" "config\windows_test.env" >nul
    echo [IMPORTANT] Please edit config\windows_test.env with your credentials!
) else (
    echo config\windows_test.env already exists, skipping
)

echo.
echo ====================================================================
echo  Installation Complete!
echo ====================================================================
echo.
echo IMPORTANT: Configure your settings before running!
echo   1. Edit config\windows_test.env with your credentials:
echo      - OBS_PASSWORD (if OBS WebSocket has password)
echo      - WEBDAV_HOST, WEBDAV_USERNAME, WEBDAV_PASSWORD
echo      - Or leave WebDAV settings empty for offline mode
echo   2. Install OBS Studio if not already installed
echo   3. Run START.bat to launch the system
echo.
echo For detailed documentation, see README.md
echo.
pause
