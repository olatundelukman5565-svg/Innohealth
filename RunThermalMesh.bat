@echo off
REM Double-click this file on Windows to launch the ThermalMesh Pipeline app.
cd /d "%~dp0"

if not exist ".venv" (
  echo First-time setup: creating environment and installing dependencies.
  echo This can take a few minutes -- please wait...
  python -m venv .venv
  call .venv\Scripts\activate.bat
  REM Using "python -m pip" (not bare "pip") avoids a Windows-only self-upgrade
  REM error where pip.exe cannot overwrite itself while it's the running process.
  python -m pip install --quiet -e .
  if errorlevel 1 (
    echo.
    echo Dependency installation failed -- see the message above.
    echo A common fix: delete the .venv folder next to this script and try again.
    pause
    exit /b 1
  )
) else (
  call .venv\Scripts\activate.bat
)

echo Setup complete. Launching the app...
python scripts\gui.py
if errorlevel 1 (
  echo.
  echo Something went wrong -- see the message above.
  pause
)
