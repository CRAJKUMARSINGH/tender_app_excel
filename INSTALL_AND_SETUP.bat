@echo off
title Tender Processing System - Installation & Setup
color 0B

echo.
echo ========================================
echo    TENDER PROCESSING SYSTEM
echo    Installation and Setup
echo ========================================
echo.

:: Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python 3.8 or higher:
    echo 1. Go to https://python.org
    echo 2. Download Python 3.8 or higher
    echo 3. Run the installer
    echo 4. Make sure to check "Add Python to PATH"
    echo 5. Restart this batch file after installation
    echo.
    pause
    exit /b 1
)

echo Python is installed ✓
python --version

:: Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install requirements
echo.
echo Installing required packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install some packages
    echo Please check your internet connection and try again
    echo.
    pause
    exit /b 1
)

:: Create necessary directories
echo.
echo Creating application directories...
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs
if not exist "templates" mkdir templates

:: Test the application
echo.
echo Testing the application...
python test_app.py
if errorlevel 1 (
    echo.
    echo WARNING: Some tests failed, but the application may still work
    echo You can try running START_APP.bat to start the application
    echo.
) else (
    echo.
    echo All tests passed! Application is ready to use ✓
    echo.
)

echo.
echo ========================================
echo    SETUP COMPLETE!
echo ========================================
echo.
echo To start the application:
echo 1. Double-click START_APP.bat
echo 2. Or run: python start_app.py
echo.
echo The application will open in your browser at:
echo http://localhost:5000
echo.
echo For help, read README.md
echo.
pause
