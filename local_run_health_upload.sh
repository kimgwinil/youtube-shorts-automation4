#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$ROOT/logs"
LOCK_DIR="$ROOT/.local-health-upload.lock"
mkdir -p "$LOG_DIR"

exec >>"$LOG_DIR/startup-health-upload.log" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] startup health upload requested"

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] another upload is already running; exiting"
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] missing .env"
  exit 1
fi

if [[ ! -f token.json ]]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] missing token.json"
  exit 1
fi

set -a
source .env
set +a

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export TTS_PROVIDER="${LOCAL_TTS_PROVIDER:-macos}"
export MACOS_SAY_VOICE="${LOCAL_MACOS_SAY_VOICE:-Yuna}"
export TTS_ALLOW_FALLBACK="${TTS_ALLOW_FALLBACK:-false}"
export YOUTUBE_PRIVACY="${YOUTUBE_PRIVACY:-public}"
export IMAGE_PROVIDER="${IMAGE_PROVIDER:-gemini}"
export ENABLE_BGM="${ENABLE_BGM:-false}"
export ENABLE_SLIDE_CAPTIONS="${ENABLE_SLIDE_CAPTIONS:-false}"
export ENABLE_SLIDE_MOTION="${ENABLE_SLIDE_MOTION:-false}"
export BURN_IN_SUBTITLES="${BURN_IN_SUBTITLES:-true}"
export UPLOAD_YOUTUBE_CAPTIONS="${UPLOAD_YOUTUBE_CAPTIONS:-false}"

/usr/bin/python3 -m pip install -r longform_automation/requirements.txt
/usr/bin/python3 longform_automation/daily_longform_upload_v2.py

echo "[$(date '+%Y-%m-%d %H:%M:%S')] startup health upload finished"
