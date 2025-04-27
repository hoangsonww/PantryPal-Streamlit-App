#!/usr/bin/env bash
set -euo pipefail

echo "📝 Regenerating requirements.txt…"
pip freeze > requirements.txt
echo "✅ requirements.txt updated."
