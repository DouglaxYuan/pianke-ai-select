#!/bin/zsh
set -e

APP_DIR="/Volumes/英睿达 P3/AI选片/pianke"
PORT="${PIC_SELECTER_PORT:-5057}"
SESSION_NAME="pianke-expert"

cd "$APP_DIR"

if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Pianke is already listening on http://127.0.0.1:$PORT"
  open "http://127.0.0.1:$PORT"
  exit 0
fi

if ! command -v screen >/dev/null 2>&1; then
  echo "screen is not available. Please use 启动-片刻专家版.command instead."
  read -k 1 -s '?Press any key to close...'
  exit 1
fi

screen -S "$SESSION_NAME" -X quit >/dev/null 2>&1 || true
screen -dmS "$SESSION_NAME" zsh -lc '
  cd "/Volumes/英睿达 P3/AI选片/pianke"
  source ".venv/bin/activate"
  CERT_PATH="$(python - <<'"'"'PY'"'"'
import certifi
print(certifi.where())
PY
)"
  export SSL_CERT_FILE="$CERT_PATH"
  export REQUESTS_CA_BUNDLE="$CERT_PATH"
  export PIC_SELECTER_RUNTIME="${PIC_SELECTER_RUNTIME:-auto}"
  unset HF_ENDPOINT
  exec .venv/bin/python -u app.py --port '"$PORT"' --no-browser >> pianke-server.log 2>&1
'

sleep 1
if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Pianke is running at http://127.0.0.1:$PORT"
  open "http://127.0.0.1:$PORT"
else
  echo "Pianke did not start. Latest log:"
  tail -n 80 "$APP_DIR/pianke-server.log" 2>/dev/null || true
  read -k 1 -s '?Press any key to close...'
  exit 1
fi
