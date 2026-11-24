#!/usr/bin/env bash
# Oracle Bone and TCM Codex - local server (macOS / Linux)
cd "$(dirname "$0")" || exit 1
echo '========================================'
echo '  Oracle Bone and TCM Codex - Server'
echo '========================================'
PORT="${1:-8138}"
if command -v node >/dev/null 2>&1 && node -e '1' >/dev/null 2>&1; then
  echo '[Start] Using Node.js ...'
  exec node serve.mjs "$PORT" --host 127.0.0.1
elif command -v bun >/dev/null 2>&1 && bun -e '1' >/dev/null 2>&1; then
  echo '[Start] Using Bun ...'
  exec bun serve.mjs "$PORT" --host 127.0.0.1
elif command -v python3 >/dev/null 2>&1 && python3 -c 'print(1)' >/dev/null 2>&1; then
  echo '[Start] Using Python ...'
  exec python3 serve.py "$PORT" --host 127.0.0.1
else
  echo '[ERROR] Node.js / Bun / Python3 not found. Install Node.js: https://nodejs.org/'
  exit 1
fi
