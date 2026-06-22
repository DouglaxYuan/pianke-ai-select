#!/bin/zsh
set -e

cd "/Volumes/英睿达 P3/AI选片/pianke"

if [[ ! -d ".venv" ]]; then
  echo "Virtual environment not found: .venv"
  echo "Please reinstall Pianke dependencies first."
  read -k 1 -s '?Press any key to close...'
  exit 1
fi

source ".venv/bin/activate"

CERT_PATH="$(python - <<'PY'
import certifi
print(certifi.where())
PY
)"

export SSL_CERT_FILE="$CERT_PATH"
export REQUESTS_CA_BUNDLE="$CERT_PATH"
export PIC_SELECTER_RUNTIME="auto"
unset HF_ENDPOINT

echo "Starting Pianke expert-ready server..."
echo "Open http://127.0.0.1:5057 if the browser does not open automatically."
python app.py --port 5057
