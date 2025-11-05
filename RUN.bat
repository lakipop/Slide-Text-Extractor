@echo off
echo ========================================
echo   Slide Text Extractor
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "%~dp0venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run SETUP.bat first to set up the project.
    echo.
    pause
    exit /b 1
)

echo [1/3] Activating virtual environment...
call "%~dp0venv\Scripts\activate.bat"

echo [2/3] Checking .env file...
if not exist "%~dp0.env" (
    echo [WARNING] .env file not found!
    echo Please rename .env.example to .env and configure your settings.
    echo.
    pause
    exit /b 1
)

echo [3/3] Starting the script...
echo.
python "%~dp0process_slides.py"

echo.
echo ========================================
echo   Processing Complete!
echo ========================================
echo.
pause
