@echo off
REM Double-click this file on Windows to launch the ThermalMesh Pipeline app.
cd /d "%~dp0"

if not exist ".venv" (
  echo First-time setup: creating environment and installing dependencies.
  echo This can take a minute or two -- please wait...
  python -m venv .venv
  call .venv\Scripts\activate.bat
  pip install --quiet --upgrade pip
  pip install --quiet -e .
) else (
  call .venv\Scripts\activate.bat
)

python scripts\gui.py
if errorlevel 1 (
  echo.
  echo Something went wrong -- see the message above.
  pause
)
