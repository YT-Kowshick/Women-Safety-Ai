#!/usr/bin/env bash
set -euo pipefail

# Railway Railpack monorepo fallback build (root deployment)
if command -v python >/dev/null 2>&1; then
	PYTHON_BIN="$(command -v python)"
else
	echo "Python runtime not found in container (expected 'python' binary)"
	exit 1
fi

"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install --no-cache-dir -r backend/requirements.txt
