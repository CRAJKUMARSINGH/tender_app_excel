@echo off
title Tender Processing System - Enhanced Startup
color 0A

echo.
echo ========================================
echo    TENDER PROCESSING SYSTEM
echo    Enhanced Version 2.0
echo ========================================
echo.

:: Check if running in PowerShell and adjust accordingly
echo Checking environment...
if "%POWERSHELL%"=="1" (
    echo Running in PowerShell mode...
    set PS_MODE=1
) else (
    echo Running in Command Prompt mode...
    set PS_MODE=0
)

:: Check if Python is installed
echo.
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Python is not installed or not in PATH
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

echo ✅ Python is installed
python --version

:: Check if requirements are installed
echo.
echo Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo.
    echo 📦 Installing required packages...
    echo This may take a few minutes...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ❌ ERROR: Failed to install dependencies
        echo Please check your internet connection and try again
        echo.
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully
) else (
    echo ✅ Dependencies are already installed
)

:: Check for required directories and files
echo.
echo Checking application files...
if not exist "app.py" (
    echo ❌ ERROR: app.py not found
    echo Please ensure you're running this from the correct directory
    echo.
    pause
    exit /b 1
)

if not exist "templates" (
    echo Creating templates directory...
    mkdir templates
)

if not exist "uploads" (
    echo Creating uploads directory...
    mkdir uploads
)

if not exist "outputs" (
    echo Creating outputs directory...
    mkdir outputs
)

:: Check for box image
if not exist "Attached_assets\box.png" (
    echo ⚠️  WARNING: Box image not found
    echo The comparison sheet may not display the box image correctly
    echo.
)

:: Start the application
echo.
echo 🚀 Starting Tender Processing Application...
echo.
echo The application will open in your browser automatically.
echo If it doesn't open, go to: http://localhost:5000
echo.
echo 📊 Application features:
echo    • Modern web interface
echo    • Real-time progress tracking
echo    • Enhanced error handling
echo    • Analytics and monitoring
echo    • Professional template generation
echo.
echo Press Ctrl+C to stop the application when done.
echo.

:: Start the application with enhanced error handling
python start_app.py
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Application failed to start
    echo.
    echo Possible solutions:
    echo 1. Check if port 5000 is already in use
    echo 2. Try running: netstat -ano ^| findstr :5000
    echo 3. Kill any process using port 5000
    echo 4. Restart your computer
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Application stopped successfully.
echo.
pause
