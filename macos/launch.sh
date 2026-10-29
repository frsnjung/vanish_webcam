#!/bin/bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_DIR="$(cd "$APP_DIR/.." && pwd)"
PYTHON="$APP_DIR/.venv/bin/python"
export PYTHONUNBUFFERED=1
export PYGAME_HIDE_SUPPORT_PROMPT=1

fail() {
    printf '\n%s\n' "$1" >&2
    if [[ -t 0 ]]; then
        read -r -p "Press Return to close. " answer
    fi
    exit 1
}

[[ -x "$PYTHON" ]] || fail "VanishCam's Python environment is missing. See the setup notes."

if [[ "${1:-}" == "--check" ]]; then
    "$PYTHON" "$SOURCE_DIR/vanish_cam.py" --self-test
    exit 0
fi

OUTPUT=(--virtual-camera --virtual-backend obs)
if [[ "${1:-}" == "--preview" ]]; then
    OUTPUT=(--no-virtual-camera)
    shift
else
    [[ -d /Applications/OBS.app ]] || fail "Install OBS Studio 30 or newer in /Applications, open it once, and approve its camera extension in System Settings."
fi

mkdir -p "$APP_DIR/logs"
printf '%s\n' \
    "VanishCam for Teams" \
    "Step out of view for the first 4 seconds to capture the background." \
    "In Teams, select OBS Virtual Camera and turn off background effects." \
    "Use a V hand gesture to vanish in Normal mode; join your hands in Naruto mode." \
    "Click the preview before using R to return, Space to recapture, or Q to quit." \
    "Keep OBS's own virtual-camera output stopped."

cd "$SOURCE_DIR"
if ! "$PYTHON" vanish_cam.py --mode normal --width 1280 --height 720 --fps 30 --no-mirror "${OUTPUT[@]}" "$@" 2>&1 | tee "$APP_DIR/logs/latest.log"; then
    fail "VanishCam could not start. Check the message above or logs/latest.log. Allow camera access for Terminal, stop OBS's virtual camera, and consult the setup notes."
fi