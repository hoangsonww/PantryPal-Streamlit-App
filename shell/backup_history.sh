#!/usr/bin/env bash
set -euo pipefail

mkdir -p shell/backups
ts=$(date +%Y%m%d_%H%M%S)
cp recipe_history.json shell/backups/recipe_history_${ts}.json
echo "✅ recipe_history.json backed up to shell/backups/recipe_history_${ts}.json"
