@echo off
REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo ========================================
echo   Slide Text Extractor - Setup
echo ========================================
echo.

echo [1/4] Checking Python installation...
python --version
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo.
echo [2/4] Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo [SUCCESS] Virtual environment created
) else (
    echo [INFO] Virtual environment already exists
)

echo.
echo [3/4] Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat

echo [3/4] Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [4/4] Creating environment file...
if not exist .env (
    copy .env.example .env
    echo [INFO] Created .env file from template
    echo [ACTION REQUIRED] Please edit .env and add your Azure credentials!
) else (
    echo [INFO] .env file already exists
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Edit .env file with your Azure credentials
echo   2. Place screenshot images in the configured folder
echo   3. Run RUN.bat to start processing
echo.

REM Only pause if run from double-click (not from terminal)
if "%TERM_PROGRAM%"=="" pause
