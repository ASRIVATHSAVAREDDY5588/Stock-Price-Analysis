@echo off
setlocal enabledelayedexpansion
title Stock Market Distribution Analyzer - Windows Setup

echo ===============================================================================
echo            STOCK MARKET DISTRIBUTION ANALYZER - WINDOWS SETUP
echo ===============================================================================
echo.

:: 1. Verify Python installation
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not found in your system PATH.
    echo Please install Python 3.10, 3.11, or 3.12 from https://www.python.org/
    echo Make sure to check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
echo [OK] Detected Python %PYTHON_VERSION%

:: 2. Create local virtual environment (.venv)
if not exist ".venv" (
    echo [INFO] Creating isolated virtual environment in .venv ...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created successfully.
) else (
    echo [INFO] Virtual environment .venv already exists.
)

:: 3. Activate venv and upgrade pip
call .venv\Scripts\activate.bat
echo [INFO] Updating pip ...
python -m pip install --upgrade pip >nul 2>&1

:: 4. Install dependencies
echo [INFO] Installing required packages from requirements.txt ...
echo (This may take 1-2 minutes on first run...)
python -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Dependency installation encountered an issue.
    echo Please review network connection or check TROUBLESHOOTING.md.
    pause
    exit /b 1
)
echo [OK] All dependencies installed successfully.

:: 5. Create default .env if missing
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [OK] Created .env configuration from .env.example.
    )
)

:: 6. Ensure sample CSV data is generated
python -c "import sys; sys.path.append('.'); from data.csv_provider import generate_sample_csv_files; generate_sample_csv_files()" >nul 2>&1

echo.
echo ===============================================================================
echo                  SETUP COMPLETED SUCCESSFULLY!
echo ===============================================================================
echo.
echo Next steps:
echo   1. (Optional) Edit .env to add your OPENAI_API_KEY if you want LLM insights.
echo      Note: The app works 100%% offline without any API key using synthetic demo.
echo   2. Run 'start_dashboard.bat' to launch the web interface.
echo   3. Run 'run_tests.bat' to verify automated statistical tests.
echo.
pause
