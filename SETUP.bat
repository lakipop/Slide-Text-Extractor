@echo off
echo ========================================
echo   Slide Text Extractor - Setup
echo ========================================
echo.

echo [1/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    echo Make sure Python is installed and added to PATH.
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo [4/4] Checking configuration...
if not exist ".env" (
    echo.
    echo [ACTION REQUIRED] Please configure your .env file:
    echo   1. Rename .env.example to .env
    echo   2. Add your Azure credentials and settings
    echo   3. See GUIDE.md for detailed instructions
    echo.
) else (
    echo .env file found!
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Configure your .env file (if not done already)
echo   2. Double-click RUN.bat to start processing
echo.
pause
