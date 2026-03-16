#!/usr/bin/env bash
set -euo pipefail

# Railway Railpack monorepo fallback build (root deployment)
python -m pip install --upgrade pip
python -m pip install --no-cache-dir -r backend/requirements.txt
