#!/usr/bin/env bash
# start-claude.sh — Export env vars and launch Claude Code
# Usage: source poc/start-claude.sh
set -a

# MCP server env vars (resolves ${VAR} references in .mcp.json)
source "$(dirname "$0")/.env.docker"

# Claude Code — use AWS Bedrock
CLAUDE_CODE_USE_BEDROCK=1
AWS_REGION=us-east-1

set +a

echo "Env vars exported:"
echo "  NEO4J_URI=$NEO4J_URI"
echo "  OPENSEARCH_URL=$OPENSEARCH_URL"
echo "  CLAUDE_CODE_USE_BEDROCK=$CLAUDE_CODE_USE_BEDROCK"
echo "  AWS_REGION=$AWS_REGION"
echo ""
echo "Opening VS Code..."
code /Users/andrew/Desktop/PoC/gf-hackathon
