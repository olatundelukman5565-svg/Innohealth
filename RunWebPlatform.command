#!/bin/bash
# Double-click this file on Mac to start the ThermalMesh web platform
# (backend API + web app) and open it in your browser.
# First run: right-click -> Open once if macOS blocks it as unidentified.
cd "$(dirname "$0")" || exit 1
ROOT_DIR="$(pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python was not found. Install Python 3.11+ from https://python.org and try again."
  read -p "Press Enter to close..."
  exit 1
fi
if ! command -v node >/dev/null 2>&1; then
  echo "Node.js was not found. Install Node.js 18+ from https://nodejs.org and try again."
  read -p "Press Enter to close..."
  exit 1
fi

echo "============================================"
echo " Setting up the backend (first run only)..."
echo "============================================"
cd "$ROOT_DIR/web/backend" || exit 1
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  source .venv/bin/activate
  python3 -m pip install --quiet -r requirements.txt
  if [ $? -ne 0 ]; then
    echo ""
    echo "Backend dependency installation failed -- see the message above."
    read -p "Press Enter to close..."
    exit 1
  fi
fi
[ -f .env ] || cp .env.example .env

echo "============================================"
echo " Setting up the web app (first run only)..."
echo "============================================"
cd "$ROOT_DIR/web/frontend" || exit 1
if [ ! -d "node_modules" ]; then
  npm install
  if [ $? -ne 0 ]; then
    echo ""
    echo "Frontend dependency installation failed -- see the message above."
    read -p "Press Enter to close..."
    exit 1
  fi
fi
[ -f .env.local ] || cp .env.example .env.local

echo "Starting the backend and web app in their own Terminal windows..."
osascript -e "tell application \"Terminal\" to do script \"cd '$ROOT_DIR/web/backend' && source .venv/bin/activate && uvicorn app.main:app --host 127.0.0.1 --port 8000\""
osascript -e "tell application \"Terminal\" to do script \"cd '$ROOT_DIR/web/frontend' && npm run dev\""

echo ""
echo "Waiting for the servers to start (the backend seeds demo data the very"
echo "first time, which can take about a minute)..."
sleep 10
open http://localhost:3000

echo ""
echo "Two Terminal windows just opened for the backend and web app."
echo "Leave both open while you use the platform -- closing them stops the app."
echo "If the page in your browser shows an error, wait a bit and refresh --"
echo "the backend may still be finishing its first-time setup."
echo ""
echo "Demo login: demo@innohealth.com / demo1234  (admin: admin@innohealth.com / admin123)"
echo ""
read -p "Press Enter to close this window (the app keeps running)..."
