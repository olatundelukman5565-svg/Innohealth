#!/bin/bash
# Double-click this file on Linux to launch the ThermalMesh Pipeline app
# (your file manager may ask to "Run" vs "Run in Terminal" -- either works).
cd "$(dirname "$0")" || exit 1

if [ ! -d ".venv" ]; then
  echo "First-time setup: creating environment and installing dependencies."
  echo "This can take a minute or two -- please wait..."
  python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip install --quiet --upgrade pip
  pip install --quiet -e .
else
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

python3 scripts/gui.py
