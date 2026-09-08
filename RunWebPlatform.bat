@echo off
REM Double-click this file on Windows to start the ThermalMesh web platform
REM (backend API + web app) and open it in your browser.
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python 3.11+ from https://python.org and try again.
  pause
  exit /b 1
)
where node >nul 2>nul
if errorlevel 1 (
  echo Node.js was not found. Install Node.js 18+ from https://nodejs.org and try again.
  pause
  exit /b 1
)

echo ============================================
echo  Setting up the backend (first run only)...
echo ============================================
cd web\backend
if not exist ".venv" (
  python -m venv .venv
  call .venv\Scripts\activate.bat
  echo Installing Python dependencies -- this can take a few minutes on first
  echo run ^(numpy/scipy/opencv are large^). You will see pip's normal output
  echo below; it is NOT frozen even if it pauses for a while between lines.
  python -m pip install -r requirements.txt
  if errorlevel 1 (
    echo.
    echo Backend dependency installation failed -- see the message above.
    pause
    exit /b 1
  )
) else (
  call .venv\Scripts\activate.bat
)
if not exist ".env" copy .env.example .env >nul
cd ..\..

echo ============================================
echo  Setting up the web app (first run only)...
echo ============================================
cd web\frontend
if not exist "node_modules" (
  call npm install
  if errorlevel 1 (
    echo.
    echo Frontend dependency installation failed -- see the message above.
    pause
    exit /b 1
  )
)
if not exist ".env.local" copy .env.example .env.local >nul
cd ..\..

echo Starting the backend and web app in their own windows...
start "ThermalMesh Backend (keep this open)" cmd /k "cd /d "%~dp0web\backend" && call .venv\Scripts\activate.bat && uvicorn app.main:app --host 127.0.0.1 --port 8000"
start "ThermalMesh Web App (keep this open)" cmd /k "cd /d "%~dp0web\frontend" && npm run dev"

echo.
echo Waiting for the servers to start (the backend seeds demo data the very
echo first time, which can take about a minute)...
timeout /t 10 /nobreak >nul
start http://localhost:3000

echo.
echo Two windows just opened: "ThermalMesh Backend" and "ThermalMesh Web App".
echo Leave both open while you use the platform -- closing them stops the app.
echo If the page in your browser shows an error, wait a bit and refresh --
echo the backend may still be finishing its first-time setup.
echo.
echo Demo login: demo@innohealth.com / demo1234  (admin: admin@innohealth.com / admin123)
echo.
pause
