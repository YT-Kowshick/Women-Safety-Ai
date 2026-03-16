#!/usr/bin/env bash
set -euo pipefail

# Railway Railpack monorepo fallback start (root deployment)
if command -v python >/dev/null 2>&1; then
	PYTHON_BIN="python"
elif command -v python3 >/dev/null 2>&1; then
	PYTHON_BIN="python3"
else
	echo "Python runtime not found in container"
	exit 1
fi

cd backend

# Safety fallback: if build phase was skipped/cached incorrectly, ensure deps exist.
if ! "$PYTHON_BIN" -c "import uvicorn" >/dev/null 2>&1; then
	"$PYTHON_BIN" -m pip install --no-cache-dir -r requirements.txt
fi

exec "$PYTHON_BIN" -m uvicorn app:app --host 0.0.0.0 --port "${PORT:-8000}"
