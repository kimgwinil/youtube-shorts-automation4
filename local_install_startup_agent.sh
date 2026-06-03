#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_ID="com.kimgwinil.youtube-shorts-automation4.health-startup"
AGENT_DIR="$HOME/Library/LaunchAgents"
PLIST="$AGENT_DIR/$AGENT_ID.plist"

mkdir -p "$AGENT_DIR" "$ROOT/logs"
chmod +x "$ROOT/local_run_health_upload.sh"

cat >"$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$AGENT_ID</string>
  <key>ProgramArguments</key>
  <array>
    <string>$ROOT/local_run_health_upload.sh</string>
  </array>
  <key>WorkingDirectory</key>
  <string>$ROOT</string>
  <key>RunAtLoad</key>
  <true/>
  <key>StandardOutPath</key>
  <string>$ROOT/logs/launchd-health-upload.out.log</string>
  <key>StandardErrorPath</key>
  <string>$ROOT/logs/launchd-health-upload.err.log</string>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl kickstart -k "gui/$(id -u)/$AGENT_ID"

echo "Installed and started $AGENT_ID"
echo "Logs:"
echo "  $ROOT/logs/startup-health-upload.log"
echo "  $ROOT/logs/launchd-health-upload.out.log"
echo "  $ROOT/logs/launchd-health-upload.err.log"
