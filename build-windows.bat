@echo off
setlocal

REM Build a single-file Windows EXE using PyInstaller
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
    echo [1/5] Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 goto :error
)

echo [2/5] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 goto :error

echo [3/5] Installing dependencies...
python -m pip install --upgrade pip
if errorlevel 1 goto :error
pip install -r requirements.txt
if errorlevel 1 goto :error
pip install pyinstaller
if errorlevel 1 goto :error

echo [4/5] Cleaning previous build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist app.spec del /q app.spec

echo [5/5] Building single-file EXE...
pyinstaller --noconfirm --clean --onefile --windowed --name pdf-to-png-gui app.py
if errorlevel 1 goto :error

echo.
echo Build complete.
echo EXE location: %cd%\dist\pdf-to-png-gui.exe
echo.
pause
exit /b 0

:error
echo.
echo Build failed. See errors above.
pause
exit /b 1
