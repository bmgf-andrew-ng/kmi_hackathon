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

# ---------------------------------------------------------------
# 4. Install web app dependencies
# ---------------------------------------------------------------
echo "Installing web app dependencies..."
cd /workspaces/gf-hackathon/poc/web
npm install

# ---------------------------------------------------------------
# 5. Install Claude Code CLI (for skills/agents development)
# ---------------------------------------------------------------
echo "Installing Claude Code CLI..."
npm install -g @anthropic-ai/claude-code

cd /workspaces/gf-hackathon

echo "=== DevContainer post-create: complete ==="
echo ""
echo "Next steps:"
echo "  1. Seed data stores:   bash .devcontainer/seed.sh"
echo "  2. Start web app:      cd poc/web && npm run dev"
echo "  3. Neo4j browser:      http://localhost:7474"
echo "  4. Web UI:             http://localhost:3001"
echo "  5. Verify MCP tools:   /mcp in Claude Code"
