#!/usr/bin/env bash
# seed.sh — DevContainer-aware seed runner.
# Uses Docker Compose service names (neo4j, opensearch) instead of
# localhost, and cypher-shell directly instead of docker exec.
set -euo pipefail

REPO_ROOT="/workspaces/gf-hackathon"
SEED_DIR="$REPO_ROOT/poc/seed"

echo "=== Seeding data stores (DevContainer mode) ==="

# ---------------------------------------------------------------
# 1. Neo4j — seed via HTTP API (no cypher-shell needed)
# ---------------------------------------------------------------
echo ""
echo "Seeding Neo4j knowledge graph..."

NEO4J_HTTP="http://neo4j:7474"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASS="${NEO4J_PASSWORD:-password}"

# Strip comments, collapse into statements, send via HTTP transactional endpoint
python3 -c "
import re, json, urllib.request

cypher = open('$SEED_DIR/neo4j/seed.cypher').read()
# Remove // comments
cypher = re.sub(r'//.*', '', cypher)
# Split on semicolons, filter empty
stmts = [s.strip() for s in cypher.split(';') if s.strip()]

payload = json.dumps({'statements': [{'statement': s} for s in stmts]}).encode()
req = urllib.request.Request(
    '$NEO4J_HTTP/db/neo4j/tx/commit',
    data=payload,
    headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + __import__('base64').b64encode(
            '$NEO4J_USER:$NEO4J_PASS'.encode()).decode()
    },
)
resp = json.loads(urllib.request.urlopen(req).read())
errors = resp.get('errors', [])
if errors:
    print('Neo4j seed errors:', json.dumps(errors, indent=2))
    raise SystemExit(1)
print(f'Neo4j seeded: {len(stmts)} statement(s) executed.')
"

echo "Neo4j seeded successfully."

# ---------------------------------------------------------------
# 2. OpenSearch — create index and bulk-load chunks
# ---------------------------------------------------------------
echo ""
echo "Creating OpenSearch index..."

# Delete index if it exists (idempotent)
curl -sf -X DELETE "http://opensearch:9200/strategy-chunks" > /dev/null 2>&1 || true

# Create index with mapping
curl -sf -X PUT "http://opensearch:9200/strategy-chunks" \
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

echo "Bulk indexing document chunks..."
curl -sf -X POST "http://opensearch:9200/_bulk" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary "@$SEED_DIR/opensearch/chunks.ndjson"

echo ""
echo "OpenSearch seeded successfully."

# ---------------------------------------------------------------
# 3. Azurite — upload page images to blob storage
# ---------------------------------------------------------------
echo ""
echo "Seeding Azurite blob storage with page images..."

AZURE_STORAGE_BLOB_ENDPOINT="${AZURE_STORAGE_BLOB_ENDPOINT:-http://azurite:10000/devstoreaccount1}" \
AZURE_STORAGE_CONTAINER="${AZURE_STORAGE_CONTAINER:-strategy-pages}" \
  python3 "$SEED_DIR/azurite/seed.py"

echo "Azurite seeded successfully."

echo ""
echo "=== All data stores seeded ==="
