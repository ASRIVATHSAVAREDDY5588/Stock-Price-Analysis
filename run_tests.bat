@echo off
setlocal
title Stock Market Distribution Analyzer - Automated Tests

echo ===============================================================================
echo          STOCK MARKET DISTRIBUTION ANALYZER - RUN AUTOMATED TESTS
echo ===============================================================================
echo.

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    set PYTHON_CMD=python
) else (
    set PYTHON_CMD=python
)

echo [INFO] Running pytest test suite...
%PYTHON_CMD% -m pytest tests -v

echo.
if %ERRORLEVEL% equ 0 (
    echo ===============================================================================
    echo                    ALL AUTOMATED TESTS PASSED (100%%)
    echo ===============================================================================
) else (
    echo ===============================================================================
    echo                 [WARNING] SOME TESTS ENCOUNTERED FAILURES
    echo ===============================================================================
)
echo.
pause
