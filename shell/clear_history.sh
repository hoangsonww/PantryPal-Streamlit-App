#!/usr/bin/env bash
set -euo pipefail

HIST="recipe_history.json"
if [ -f "$HIST" ]; then
  ts=$(date +%Y%m%d_%H%M%S)
  cp "$HIST" "${HIST}.bak.${ts}"
  echo "📦 Backup created: ${HIST}.bak.${ts}"
  echo "[]" > "$HIST"
  echo "🗑️  Cleared ${HIST}"
else
  echo "❌ ${HIST} not found."
fi
