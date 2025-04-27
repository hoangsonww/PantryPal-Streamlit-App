#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Auto-formatting with Black…"
black .

echo "🔀 Sorting imports with isort…"
isort .

echo "✅ Formatting complete!"
