#!/bin/bash
set -e

echo "[notary] Applying database migrations..."
alembic upgrade head

echo "[notary] Starting FastAPI server (hot-reload)..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
