#!/usr/bin/env bash
set -euo pipefail

# activate venv if it exists
if [ -f .venv/bin/activate ]; then
  echo "🖥️ Activating virtualenv…"
  source .venv/bin/activate
fi

echo "🎉 Launching PantryPal locally…"
streamlit run app.py
