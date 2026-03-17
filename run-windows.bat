@echo off
setlocal

REM Run from source on Windows
cd /d "%~dp0"

set "PYTHON_CMD="
where py >nul 2>&1 && set "PYTHON_CMD=py"
if not defined PYTHON_CMD (
    where python >nul 2>&1 && set "PYTHON_CMD=python"
)
if not defined PYTHON_CMD (
    echo ERROR: Python launcher not found. Install Python 3.9+ and ensure 'py' or 'python' is on PATH.
    goto :error
)

if not exist requirements.txt (
    echo ERROR: requirements.txt not found in %cd%
    goto :error
)

if not exist .venv (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 goto :error
)

call .venv\Scripts\activate.bat
if errorlevel 1 goto :error

python -m pip install --upgrade pip
if errorlevel 1 goto :error
pip install -r requirements.txt
if errorlevel 1 goto :error

python app.py
if errorlevel 1 goto :error

exit /b 0

:error
echo.
echo Run failed. See errors above.
pause
exit /b 1
