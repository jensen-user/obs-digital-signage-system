@echo off
REM Test script for manual content folder override
REM This demonstrates using the sunday_service_slideshow folder without scheduling

echo ========================================
echo Manual Content Folder Override Test
echo ========================================
echo.
echo This will temporarily use sunday_service_slideshow
echo without automatic scheduling.
echo.
echo Press Ctrl+C to stop the system.
echo ========================================
echo.

REM Override environment variables for this session only
set SCHEDULE_ENABLED=false
set MANUAL_CONTENT_FOLDER=vaeveriet_screens_slideshow/sunday_service_slideshow

REM Start the system
python src/main.py

pause
