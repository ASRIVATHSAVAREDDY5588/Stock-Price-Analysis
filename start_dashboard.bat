@echo off
setlocal enabledelayedexpansion
title Stock Market Distribution Analyzer - Web Server

echo ===============================================================================
echo            STOCK MARKET DISTRIBUTION ANALYZER - DASHBOARD LAUNCHER
echo ===============================================================================
echo.

:: 1. Check for Virtual Environment or System Python
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    set PYTHON_CMD=python
) else (
    python --version >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Virtual environment (.venv) was not found and Python is not in PATH.
        echo Please run 'setup_windows.bat' first to set up the environment.
        echo.
        pause
        exit /b 1
    )
    set PYTHON_CMD=python
    echo [WARNING] .venv not found; running with system Python.
)

:: 2. Check for app.py
if not exist "app.py" (
    echo [ERROR] app.py was not found in the current directory: %CD%
    echo Please make sure you are running this script from the project folder.
    echo.
    pause
    exit /b 1
)

:: 3. Determine Port (Default 5000)
set LAB_PORT=5000
for /f "tokens=1,2 delims==" %%a in (.env 2^>nul) do (
    if "%%a"=="LAB_PORT" set LAB_PORT=%%b
)
set APP_URL=http://127.0.0.1:%LAB_PORT%

:: 4. Check if port is already in use
netstat -ano | findstr /R /C:":%LAB_PORT% .*LISTENING" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [WARNING] Port %LAB_PORT% is already in use by another process.
    echo Checking if Stock Market Distribution Analyzer is already active...
    powershell -Command "try { $r = Invoke-WebRequest -Uri '%APP_URL%/health' -TimeoutSec 2 -UseBasicParsing; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        echo [OK] An instance is already running at %APP_URL%.
        echo Opening browser...
        start "" "%APP_URL%"
        echo Server is active. Press any key to close this launcher.
        pause >nul
        exit /b 0
    ) else (
        echo [ERROR] Port %LAB_PORT% is occupied by an unrelated program.
        echo Please change LAB_PORT in .env or stop the conflicting application.
        pause
        exit /b 1
    )
)

echo [INFO] Starting Flask Server on %APP_URL% ...
echo [INFO] Terminal will stay open for server logs. Press Ctrl+C to stop.
echo.

:: Launch server in background thread of this cmd, then monitor startup
start "" /B %PYTHON_CMD% app.py

:: 5. Wait for server to respond to health check (up to 15 seconds)
echo [INFO] Waiting for web application to initialize...
set READY=0
for /l %%i in (1,1,15) do (
    powershell -Command "try { $r = Invoke-WebRequest -Uri '%APP_URL%/health' -TimeoutSec 1 -UseBasicParsing; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        set READY=1
        goto :SERVER_UP
    )
    timeout /t 1 /nobreak >nul
)

:SERVER_UP
if "%READY%"=="1" (
    echo [OK] Server is ready and healthy!
    echo [INFO] Opening default browser at %APP_URL% ...
    start "" "%APP_URL%"
) else (
    echo [WARNING] Server startup timed out or responded slowly.
    echo You may manually open %APP_URL% in your web browser.
)

echo.
echo ===============================================================================
echo Server is actively running. Press Ctrl+C in this window to stop the server.
echo ===============================================================================
echo.

:: Keep process attached to capture stdout / stderr
cmd /k
