@echo off
setlocal
pushd %~dp0

if not exist .venv\Scripts\python.exe (
  echo No .venv found. Run START.bat first.
  pause
  popd
  exit /b 1
)

echo Reinstalling numpy (and compatible deps)...
".venv\Scripts\python.exe" -m pip uninstall -y numpy >nul 2>&1
".venv\Scripts\python.exe" -m pip install --no-cache-dir "numpy>=1.24.0,<2.0.0"

echo.
echo Done.
pause
popd
endlocal
