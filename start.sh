#!/usr/bin/env bash
set -euo pipefail

# Railway Railpack monorepo fallback start (root deployment)
cd backend
exec uvicorn app:app --host 0.0.0.0 --port "${PORT:-8000}"
