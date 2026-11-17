#!/usr/bin/env bash
# Render build & start hook — runs before the app starts
set -e

echo "==> Running Alembic migrations..."
alembic upgrade head || echo "Migration skipped (table may already exist)"

echo "==> Starting TalentMatch AI..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
