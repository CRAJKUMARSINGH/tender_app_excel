@echo off
title Tender Processing System - Startup
color 0A

echo.
echo ========================================
echo    TENDER PROCESSING SYSTEM
echo ========================================
echo.
echo Starting the application...
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    echo.
    pause
    exit /b 1
)

:: Check if requirements are installed
echo Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        echo Please check your internet connection and try again
        echo.
        pause
        exit /b 1
    )
)

:: Start the application
echo.
echo Starting Tender Processing Application...
echo.
echo The application will open in your browser automatically.
echo If it doesn't open, go to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the application when done.
echo.

python start_app.py

echo.
echo Application stopped.
pause
