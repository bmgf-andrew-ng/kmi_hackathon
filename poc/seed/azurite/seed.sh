#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Use the strategy-review venv which has azure-storage-blob installed
PYTHON="${REPO_ROOT}/poc/mcp-servers/strategy-review/.venv/bin/python3"

if [ ! -x "$PYTHON" ]; then
  echo "ERROR: Python venv not found at $PYTHON"
  echo "Run: cd poc/mcp-servers/strategy-review && uv sync"
  exit 1
fi

ACCT="${AZURE_STORAGE_ACCOUNT_NAME:-devstoreaccount1}"
KEY="${AZURE_STORAGE_ACCOUNT_KEY:-Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==}"
ENDPOINT="${AZURE_STORAGE_BLOB_ENDPOINT:-http://127.0.0.1:10000/devstoreaccount1}"
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=http;AccountName=${ACCT};AccountKey=${KEY};BlobEndpoint=${ENDPOINT}"
export AZURE_STORAGE_CONTAINER="${AZURE_STORAGE_CONTAINER:-strategy-pages}"

"$PYTHON" "$SCRIPT_DIR/seed.py"
