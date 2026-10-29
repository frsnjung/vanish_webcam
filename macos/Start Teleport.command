#!/bin/bash
set -euo pipefail
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
export PYTHONUNBUFFERED=1
mkdir -p "$APP_DIR/logs"
if ! "$APP_DIR/.venv/bin/python" "$APP_DIR/teleport.py" "$@" 2>&1 | tee "$APP_DIR/logs/teleport.log"; then
    printf '\nTeleport could not start. Quit other VanishCam instances and OBS, then retry.\n'
    read -r -p "Press Return to close. " answer
    exit 1
fi