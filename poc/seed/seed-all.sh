#!/usr/bin/env bash
# seed-all.sh — One command to seed all three data stores.
# Usage: bash poc/seed/seed-all.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Seeding all data stores ==="

# ---------------------------------------------------------------
# 1. Neo4j — knowledge graph
# ---------------------------------------------------------------
echo ""
echo "--- Neo4j ---"
bash "$SCRIPT_DIR/neo4j/seed.sh"

# ---------------------------------------------------------------
# 2. OpenSearch — document chunks
# ---------------------------------------------------------------
echo ""
echo "--- OpenSearch ---"
bash "$SCRIPT_DIR/opensearch/seed.sh"

# ---------------------------------------------------------------
# 3. Azurite — page images
# ---------------------------------------------------------------
echo ""
echo "--- Azurite ---"
bash "$SCRIPT_DIR/azurite/seed.sh"

echo ""
echo "=== All data stores seeded successfully ==="
