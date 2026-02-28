# PoC: Claude Plugin for Accelerating Development

Proof-of-concept validating the end-to-end pattern: **skill → sub-agent → MCP server → data store → synthesised results**.

A three-store RAG architecture where Claude accesses Neo4j (graph), OpenSearch (text), and Azurite (images) through MCP servers, orchestrated by Claude Code skills and sub-agents.

---

## Project Structure

### Under `poc/` — Infrastructure, Data & Application Code

```
poc/
├── plan.md                                  # Implementation plan & ADO board reference
├── create-ado-board.py                      # Azure DevOps work item generator
├── README.md                                # ← You are here
│
├── docker-compose.yml                       # Infrastructure: Neo4j, OpenSearch, Azurite
├── .env.example                             # Template for connection strings
├── .env                                     # Local connection strings (gitignored)
│
├── seed/                                    # Data Layer — seed scripts & data
│   ├── seed-all.sh                          # One-command runner for all stores
│   ├── neo4j/
│   │   ├── seed.cypher                      # Knowledge graph: Documents, Themes,
│   │   │                                    #   Indicators, Countries, FundingAreas
│   │   └── seed.sh                          # Runs cypher-shell against Neo4j container
│   ├── opensearch/
│   │   ├── create-index.sh                  # Index mapping for strategy-chunks
│   │   ├── chunks.ndjson                    # 10-20 representative document chunks
│   │   └── seed.sh                          # Bulk-indexes chunks into OpenSearch
│   └── azurite/
│       ├── seed.sh                          # Uploads page images to Azurite
│       ├── seed.py                          # Python upload script (azure-storage-blob)
│       ├── GH_2024/page_001.png … page_005.png
│       ├── TB_2025/page_001.png … page_003.png
│       └── GE_2023/page_001.png … page_004.png
│
├── mcp-servers/                             # MCP Server Layer — custom servers
│   └── strategy-review/
│       ├── pyproject.toml                   # Python deps: mcp[cli], opensearch-py,
│       │                                    #   azure-storage-blob
│       └── strategy_review_mcp/
│           ├── __init__.py
│           └── server.py                    # FastMCP server exposing:
│                                            #   search_documents(query, top_k)
│                                            #   search_chunks(query, doc_id, top_k)
│                                            #   get_page_image(doc_id, page_num)
│
└── (mcp-servers, seed data, docker-compose)
```

### At Repo Root

`.devcontainer/` lives at the repo root (required by VS Code):

```
.devcontainer/
├── devcontainer.json                        # Python 3.12, Node 22, port forwarding
├── docker-compose.devcontainer.yml          # Workspace container linked to data tier
├── post-create.sh                           # Post-create setup script
└── seed.sh                                  # Container-aware seed runner
```

### At Repo Root — Claude Code Conventions

These files must live at the repo root per Claude Code's conventions:

```
.claude/
├── agents/                                  # Agent Layer — sub-agent definitions
│   ├── explorer.md                          # (existing) Read-only codebase explorer
│   ├── architect-reviewer.md                # (existing) Solution architecture reviewer
│   ├── graph-traversal.md                   # Neo4j Cypher specialist (Sonnet)
│   ├── document-search.md                   # Text search specialist (Sonnet)
│   └── image-retrieval.md                   # Blob retrieval specialist (Haiku)
├── skills/                                  # Skill Layer — user-facing slash commands
│   ├── greet/SKILL.md                       # (existing) Example greeting skill
│   ├── review-architecture/SKILL.md         # (existing) Architecture review skill
│   ├── strategy-review/SKILL.md             # /strategy-review — graph + text queries
│   ├── gender-tech-review/SKILL.md          # /gender-tech-review — gender equality focus
│   └── budget-review/SKILL.md               # /budget-review — funding & allocation focus
└── settings.local.json                      # (gitignored) Hooks, tokens & MCP env vars

.mcp.json                                   # MCP server registry
                                             #   ado-mcp (docker exec → running container)
                                             #   neo4j (uvx mcp-neo4j-cypher)
                                             #   strategy-review (uv run)
```

---

## Layer Descriptions

| Layer | Location | Purpose | Delivered By |
|-------|----------|---------|-------------|
| **Infrastructure** | `poc/docker-compose.yml`, `poc/.env` | Neo4j 5.26, OpenSearch 2.17, Azurite 3.33 containers | Epic 1: Data Tier Infrastructure |
| **Data/Seed** | `poc/seed/` | Knowledge graph data, document chunks, page images | Epic 1: Data Tier Infrastructure |
| **MCP Servers** | `poc/mcp-servers/`, `.mcp.json` | Custom FastMCP server + Neo4j MCP config | Epic 2: MCP Server Integration |
| **Agents** | `.claude/agents/` | Graph-traversal, document-search, image-retrieval sub-agents | Epic 3: Sub-Agents & Strategy Review Skill |
| **Skills** | `.claude/skills/` | Strategy, gender-tech, budget review slash commands | Epic 3 + Epic 5 |
| **DevContainer** | `.devcontainer/` (repo root) | VS Code dev container with all services | Epic 4: Developer Experience |

---

## Component Location Rationale

**Why `poc/` for infrastructure and application code?**
- Isolates the PoC from the learning playground (concept maps, architecture reviews)
- Self-contained: `docker compose up` from `poc/` starts the full data tier
- Reproducible: seed scripts reset data stores to a known state
- Portable: the entire `poc/` folder can be extracted into a standalone repo

**Why repo root for `.claude/` and `.mcp.json`?**
- Claude Code discovers agents from `.claude/agents/*.md` relative to the repo root
- Claude Code discovers skills from `.claude/skills/*/SKILL.md` relative to the repo root
- MCP server registry (`.mcp.json`) must be at the repo root for Claude Code to load it
- These are Claude Code runtime conventions — moving them under `poc/` would break discovery

### Component → Location Mapping

| Component | Location | Constraint | Rationale |
|-----------|----------|-----------|-----------|
| Docker Compose | `poc/docker-compose.yml` | — | Isolates PoC infrastructure from repo root |
| Environment config | `poc/.env` / `poc/.env.example` | — | Scoped to PoC data tier; `.env` gitignored |
| Neo4j seed data | `poc/seed/neo4j/` | — | Co-located with the infrastructure it seeds |
| OpenSearch seed data | `poc/seed/opensearch/` | — | Co-located with the infrastructure it seeds |
| Azurite seed data | `poc/seed/azurite/` | — | Co-located with the infrastructure it seeds |
| Unified seed runner | `poc/seed/seed-all.sh` | — | Orchestrates all seed scripts in one command |
| Strategy Review MCP server | `poc/mcp-servers/strategy-review/` | — | Python application code; isolated package with `pyproject.toml` |
| DevContainer config | `.devcontainer/` (repo root) | — | Binds to `poc/docker-compose.yml` services |
| MCP server registry | `.mcp.json` (repo root) | **Claude Code convention** | Claude Code loads `.mcp.json` from repo root only; cannot be nested |
| graph-traversal agent | `.claude/agents/graph-traversal.md` (repo root) | **Claude Code convention** | Agent discovery requires `.claude/agents/` at repo root |
| document-search agent | `.claude/agents/document-search.md` (repo root) | **Claude Code convention** | Agent discovery requires `.claude/agents/` at repo root |
| image-retrieval agent | `.claude/agents/image-retrieval.md` (repo root) | **Claude Code convention** | Agent discovery requires `.claude/agents/` at repo root |
| strategy-review skill | `.claude/skills/strategy-review/SKILL.md` (repo root) | **Claude Code convention** | Skill discovery requires `.claude/skills/` at repo root |
| gender-tech-review skill | `.claude/skills/gender-tech-review/SKILL.md` (repo root) | **Claude Code convention** | Skill discovery requires `.claude/skills/` at repo root |
| budget-review skill | `.claude/skills/budget-review/SKILL.md` (repo root) | **Claude Code convention** | Skill discovery requires `.claude/skills/` at repo root |
| Claude settings | `.claude/settings.local.json` (repo root) | **Claude Code convention** | Hooks and tokens; gitignored |

---

## Getting Started

Two ways to run the stack — pick whichever suits your workflow.

### Option A: Local Docker (run on host)

Runs the three data-tier services in Docker while you work from your native terminal.

**Prerequisites:** Docker Desktop running, Python 3.10+, `uv` installed.

**1. Create the environment file**

```bash
cp poc/.env.example poc/.env.docker
```

Or use the provided `poc/.env.docker` if it already exists.

**2. Start the data tier**

```bash
cd poc
docker compose --env-file .env.docker up -d
```

**3. Wait for healthy services**

```bash
docker compose ps
```

All three (neo4j, opensearch, azurite) should show `healthy` — takes ~30–60s on first boot.

**4. Seed the data stores**

```bash
bash poc/seed/neo4j/seed.sh
bash poc/seed/opensearch/seed.sh
bash poc/seed/azurite/seed.sh
```

**5. Verify services**

```bash
# Neo4j — should return a node count
curl -s -u neo4j:password http://localhost:7474/db/neo4j/tx/commit \
  -H "Content-Type: application/json" \
  -d '{"statements":[{"statement":"MATCH (n) RETURN count(n) AS count"}]}'

# OpenSearch — should return cluster health
curl -s http://localhost:9200/_cluster/health | python3 -m json.tool

# Azurite — should succeed
nc -z localhost 10000 && echo "Azurite is up"
```

**6. Configure Claude Code env vars**

MCP env vars are read from `.claude/settings.local.json` (gitignored). Create it with:

```bash
cat > .claude/settings.local.json << 'EOF'
{
  "env": {
    "NEO4J_URI": "bolt://localhost:7687",
    "NEO4J_USER": "neo4j",
    "NEO4J_PASSWORD": "password",
    "OPENSEARCH_URL": "http://localhost:9200",
    "OPENSEARCH_USER": "admin",
    "OPENSEARCH_PASSWORD": "admin",
    "AZURE_STORAGE_BLOB_ENDPOINT": "http://127.0.0.1:10000/devstoreaccount1",
    "AZURE_STORAGE_CONTAINER": "strategy-pages"
  }
}
EOF
```

> **Note:** Azurite account name and key are well-known constants hardcoded in the
> MCP server — only the blob endpoint needs configuring.

**7. Launch Claude Code**

Open VS Code and the MCP servers will connect automatically using the env vars from `settings.local.json`. Type `/mcp` to verify neo4j and strategy-review tools are visible.

**8. Tear down**

```bash
cd poc
docker compose down        # stops containers, keeps data volumes
docker compose down -v     # stops containers AND deletes data volumes
```

---

### Option B: VS Code DevContainer

Spins up everything inside containers — workspace + data tier — using VS Code's "Reopen in Container".

**Prerequisites:** Docker Desktop running, VS Code with the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension.

**1. Ensure `poc/.env.docker` exists**

```bash
cp poc/.env.example poc/.env.docker
```

**2. Open the repo in VS Code**

```bash
code /path/to/gf-hackathon
```

**3. Reopen in Container**

`Cmd+Shift+P` → **Dev Containers: Reopen in Container**

VS Code will:
- Pull the Python 3.12 workspace image + data-tier images (first time only)
- Start neo4j, opensearch, azurite and wait for health checks
- Start the workspace container
- Run `.devcontainer/post-create.sh` (installs `uv`, creates venv, installs MCP server)

**4. Seed the data stores** (in the DevContainer terminal)

```bash
bash .devcontainer/seed.sh
```

**5. Verify services** (in the DevContainer terminal)

```bash
# Neo4j
curl -s -u neo4j:password http://neo4j:7474/db/neo4j/tx/commit \
  -H "Content-Type: application/json" \
  -d '{"statements":[{"statement":"MATCH (n) RETURN count(n) AS count"}]}'

# OpenSearch
curl -s http://opensearch:9200/_cluster/health | python3 -m json.tool

# Azurite
nc -z azurite 10000 && echo "Azurite is up"
```

**6. Test MCP servers directly** (in the DevContainer terminal)

```bash
# Strategy Review MCP — list tools
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
  poc/.venv/bin/uv run --directory poc/mcp-servers/strategy-review strategy-review-mcp

# Neo4j MCP — list tools
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
  poc/.venv/bin/uvx mcp-neo4j-cypher
```

If both return JSON with a `tools` array, the MCP servers are working.

**7. Access web UIs from your host browser** (ports are auto-forwarded)

| Service | URL |
|---------|-----|
| Neo4j Browser | `http://localhost:7474` (login: `neo4j` / `password`) |
| OpenSearch API | `http://localhost:9200` |

**8. Return to local dev**

`Cmd+Shift+P` → **Dev Containers: Reopen Folder Locally**

> **Future:** Once Claude Code can be installed inside the DevContainer, use
> `/mcp` to verify MCP tool visibility and `/strategy-review` to test the
> full skill → agent → MCP → data store pipeline end-to-end.

---

### Environment Variables Reference

MCP env vars are set in `.claude/settings.local.json` (local) or `containerEnv` (DevContainer).

| Variable | Local | DevContainer | Used By |
|---|---|---|---|
| `NEO4J_URI` | `bolt://localhost:7687` | `bolt://neo4j:7687` | `.mcp.json` → neo4j MCP |
| `NEO4J_USER` | `neo4j` | `neo4j` | docker-compose, `.mcp.json` |
| `NEO4J_PASSWORD` | `password` | `password` | docker-compose, `.mcp.json` |
| `OPENSEARCH_URL` | `http://localhost:9200` | `http://opensearch:9200` | `.mcp.json` → strategy-review MCP |
| `OPENSEARCH_USER` | `admin` | `admin` | `.mcp.json` → strategy-review MCP |
| `OPENSEARCH_PASSWORD` | `admin` | `admin` | `.mcp.json` → strategy-review MCP |
| `AZURE_STORAGE_BLOB_ENDPOINT` | `http://127.0.0.1:10000/devstoreaccount1` | `http://azurite:10000/devstoreaccount1` | strategy-review MCP (server default) |
| `AZURE_STORAGE_CONTAINER` | `strategy-pages` | `strategy-pages` | strategy-review MCP (server default) |

> **Note:** Azurite account name and key are well-known constants baked into
> every Azurite instance. They are hardcoded in the MCP server — not configurable
> via env vars. Only the blob endpoint differs between local and DevContainer.

The only difference between the two modes is the hostname — `localhost`/`127.0.0.1` for local dev vs Docker service names (`neo4j`, `opensearch`, `azurite`) for DevContainer.
