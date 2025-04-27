#!/usr/bin/env bash
set -euo pipefail

echo "📦 Building Docker image…"
docker-compose build

echo "🐳 Starting containers…"
docker-compose up -d

echo "🚀 PantryPal should now be available at http://localhost:8501"
