@echo off
setlocal ENABLEDELAYEDEXPANSION
pushd %~dp0

REM Ensure venv exists
if not exist .venv\Scripts\python.exe (
  echo Creating virtual environment...
  python -m venv .venv
)

REM Install/upgrade dependencies
".venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>&1
".venv\Scripts\python.exe" -m pip install -r requirements.txt

REM Launch app without console window and detach
start "Hand Gesture Control" ".venv\Scripts\pythonw.exe" main.py

popd
endlocal
