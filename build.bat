@echo off
setlocal enabledelayedexpansion

echo =======================================================
echo        AeroChart Inspector - Build Script
echo =======================================================
echo.

:: 1. Check Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in your PATH.
    echo Please install Python 3.10+ and add it to PATH.
    echo.
    pause
    exit /b 1
)

echo [1/4] Checking Python environment...
python --version

:: 2. Check & install dependencies
echo.
echo [2/4] Ensuring required dependencies are installed...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Failed to install some dependencies via requirements.txt.
    echo Attempting direct install of core dependencies...
    pip install PySide6 pymupdf reportlab pyinstaller
)

:: 3. Clean previous build temporary folders
echo.
echo [3/4] Cleaning previous build cache...
if exist "build" rmdir /s /q "build"

:: 4. Run PyInstaller
echo.
echo [4/4] Compiling standalone executable via PyInstaller...
python -m PyInstaller --clean AeroChartInspector.spec

if %errorlevel% equ 0 (
    echo.
    echo =======================================================
    echo [SUCCESS] Compilation completed successfully!
    echo Executable path: dist\AeroChartInspector.exe
    echo =======================================================
) else (
    echo.
    echo =======================================================
    echo [ERROR] Compilation failed. Please inspect logs above.
    echo =======================================================
)

echo.
pause
