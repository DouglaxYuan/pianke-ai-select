#!/bin/zsh
set -e

PORT="${PIC_SELECTER_PORT:-5057}"
SESSION_NAME="pianke-expert"

screen -S "$SESSION_NAME" -X quit >/dev/null 2>&1 || true

PIDS="$(lsof -tiTCP:"$PORT" -sTCP:LISTEN 2>/dev/null || true)"
if [[ -n "$PIDS" ]]; then
  echo "$PIDS" | xargs kill
  sleep 1
fi

if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Pianke may still be running on port $PORT:"
  lsof -nP -iTCP:"$PORT" -sTCP:LISTEN
  exit 1
fi

echo "Pianke stopped."
