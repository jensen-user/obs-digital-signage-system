@echo off
title OBS Digital Signage System (Production)
echo ===================================================
echo OBS Digital Signage Automation System - PRODUCTION
echo ===================================================
echo.

cd /d "%~dp0"

REM Set production environment
set ENVIRONMENT=production

echo Using production configuration (windows_prod.env)
echo.

echo Checking OBS connection...
echo.

REM Check if OBS is running
tasklist /FI "IMAGENAME eq obs64.exe" 2>NUL | find /I /N "obs64.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo WARNING: OBS Studio is not running
    echo The system will attempt to start OBS automatically
    echo.
)

echo Starting Digital Signage System...
echo.
echo Press Ctrl+C to stop the system
echo.
echo Log files location: %~dp0logs\
echo.

python src\main.py

if %errorlevel% neq 0 (
    echo.
    echo ===================================================
    echo System exited with error
    echo ===================================================
    echo.
    echo Check the logs for details:
    echo - %~dp0logs\digital_signage.log
    echo - %~dp0logs\errors.log
    echo.
)

pause
