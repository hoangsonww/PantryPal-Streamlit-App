#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Running formatter (Black)…"
black --check .

echo "🔀 Checking import order (isort)…"
isort --check-only .

echo "🐍 Linting with Flake8…"
flake8 .

echo "✅ All checks passed!"
