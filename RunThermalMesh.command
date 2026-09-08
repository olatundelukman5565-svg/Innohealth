#!/bin/bash
# Double-click this file on Mac to launch the ThermalMesh Pipeline app.
# First run: right-click -> Open (once) if Mac blocks it as an unidentified
# developer script, then it will open normally from then on.
cd "$(dirname "$0")" || exit 1

if [ ! -d ".venv" ]; then
  echo "First-time setup: creating environment and installing dependencies."
  echo "This can take a few minutes -- please wait..."
  python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python3 -m pip install --quiet -e .
  if [ $? -ne 0 ]; then
    echo ""
    echo "Dependency installation failed -- see the message above."
    echo "A common fix: delete the .venv folder next to this script and try again."
    read -p "Press Enter to close this window..."
    exit 1
  fi
else
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "Setup complete. Launching the app..."
python3 scripts/gui.py
