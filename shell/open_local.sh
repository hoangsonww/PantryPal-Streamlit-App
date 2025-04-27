#!/usr/bin/env bash
set -euo pipefail

URL="http://localhost:8501"
echo "🎉 Starting PantryPal…"
streamlit run app.py &

# give it a moment to spin up
sleep 2

# open in default browser
if command -v xdg-open >/dev/null; then
  xdg-open "$URL"
elif command -v open >/dev/null; then
  open "$URL"
else
  echo "🔗 Open your browser at $URL"
fi
