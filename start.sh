#!/usr/bin/env bash
set -euo pipefail

# Railway Railpack monorepo fallback start (root deployment)
cd backend

if command -v python >/dev/null 2>&1; then
	exec python -m uvicorn app:app --host 0.0.0.0 --port "${PORT:-8000}"
else
	exec python3 -m uvicorn app:app --host 0.0.0.0 --port "${PORT:-8000}"
fi
