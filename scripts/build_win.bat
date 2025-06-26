@echo off
setlocal enabledelayedexpansion

:: Check for Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python not found in PATH
    exit /b 1
)

:: Install requirements
python -m pip install -r requirements.txt

:: Build with PyInstaller
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --icon=src\argus\assets\icon.ico ^
    --name Argus ^
    --add-data "src\argus\assets;assets" ^
    src\argus\main.py

echo Build complete: dist\Argus.exe
endlocal