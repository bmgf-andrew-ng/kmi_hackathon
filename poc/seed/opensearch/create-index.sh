#!/usr/bin/env bash
set -euo pipefail

# Delete index if it exists (idempotent)
curl -sf -X DELETE "http://localhost:9200/strategy-chunks" > /dev/null 2>&1 || true

# Create index with mapping
curl -sf -X PUT "http://localhost:9200/strategy-chunks" \
  -H "Content-Type: application/json" \
  -d '{
  "mappings": {
    "properties": {
      "chunk_id":      { "type": "keyword" },
      "doc_id":        { "type": "keyword" },
      "doc_title":     { "type": "text" },
      "doc_year":      { "type": "integer" },
      "organization":  { "type": "keyword" },
      "chunk_text":    { "type": "text", "analyzer": "standard" },
      "section":       { "type": "keyword" },
      "page_number":   { "type": "integer" },
      "themes":        { "type": "keyword" },
      "countries":     { "type": "keyword" },
      "chunk_order":   { "type": "integer" }
    }
  }
}'

echo ""
echo "Index 'strategy-chunks' created."
