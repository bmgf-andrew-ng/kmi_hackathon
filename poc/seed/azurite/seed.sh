#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Use the poc venv which has azure-storage-blob installed
PYTHON="${REPO_ROOT}/poc/.venv/bin/python3"

if [ ! -x "$PYTHON" ]; then
  echo "ERROR: Python venv not found at $PYTHON"
  echo "Run: python3 -m venv poc/.venv && poc/.venv/bin/pip install uv && cd poc/mcp-servers/strategy-review && ../../.venv/bin/uv sync"
  exit 1
fi

echo "Seeding Azurite blob storage with page images..."

# seed.py reads AZURE_STORAGE_BLOB_ENDPOINT and AZURE_STORAGE_CONTAINER
# from env vars (with sensible defaults for local dev).
# Azurite credentials are hardcoded in seed.py.
"$PYTHON" "$SCRIPT_DIR/seed.py"
