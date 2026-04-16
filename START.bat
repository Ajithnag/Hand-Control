@echo off
setlocal ENABLEDELAYEDEXPANSION
pushd %~dp0

echo ========================================
echo  Hand Gesture Control
echo ========================================
echo.

REM Prefer venv + pinned deps for reliability
if not exist .venv\Scripts\python.exe (
  echo Creating virtual environment...
  python -m venv .venv
  if errorlevel 1 (
    echo.
    echo ERROR: Python not found or venv creation failed.
    echo Install Python 3.10/3.11 (64-bit) and try again.
    echo.
    pause
    popd
    exit /b 1
  )
)

echo Installing/updating dependencies (first run can take a minute)...
".venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>&1
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo ========================================
  echo Dependency install failed.
  echo ========================================
  echo Try running as Administrator, or open PowerShell and run:
  echo   .venv\Scripts\python.exe -m pip install -r requirements.txt
  echo.
  pause
  popd
  exit /b 1
)

echo.
echo Launching...
start "Hand Gesture Control" ".venv\Scripts\pythonw.exe" main.py

popd
endlocal

