#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load env vars from poc/.env
source "$SCRIPT_DIR/../../.env"

echo "Seeding Neo4j knowledge graph..."

docker exec -i poc-neo4j-1 cypher-shell \
  -u "$NEO4J_USER" \
  -p "$NEO4J_PASSWORD" \
  < "$SCRIPT_DIR/seed.cypher"

echo "Neo4j seeded successfully."
