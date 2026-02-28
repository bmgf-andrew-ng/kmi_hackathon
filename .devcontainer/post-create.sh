#!/usr/bin/env bash
set -euo pipefail

echo "=== DevContainer post-create: starting ==="

# ---------------------------------------------------------------
# 1. Install uv (Python package manager / runner)
# ---------------------------------------------------------------
echo "Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# ---------------------------------------------------------------
# 2. Create poc/.venv and install uv inside it
#    (.mcp.json references poc/.venv/bin/uvx and poc/.venv/bin/uv)
# ---------------------------------------------------------------
echo "Creating poc/.venv with Python 3.12..."
cd /workspaces/gf-hackathon
rm -rf poc/.venv
python3 -m venv poc/.venv
poc/.venv/bin/pip install --quiet uv

# ---------------------------------------------------------------
# 3. Install strategy-review MCP server in development mode
# ---------------------------------------------------------------
echo "Installing strategy-review MCP server..."
VIRTUAL_ENV=poc/.venv poc/.venv/bin/uv pip install -e poc/mcp-servers/strategy-review

echo "=== DevContainer post-create: complete ==="
echo ""
echo "Next steps:"
echo "  1. Seed data stores:   bash .devcontainer/seed.sh"
echo "  2. Neo4j browser:      http://localhost:7474"
echo "  3. Verify MCP tools:   /mcp in Claude Code"
