#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Creating OpenSearch index..."
bash "$SCRIPT_DIR/create-index.sh"

echo "Bulk indexing document chunks..."
curl -sf -X POST "http://localhost:9200/_bulk" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary "@$SCRIPT_DIR/chunks.ndjson"

echo ""
echo "OpenSearch seeded successfully."
